from __future__ import absolute_import

import json
from collections import defaultdict

from gixy.formatters.base import BaseFormatter

# Trying to get version
try:
    from gixy import version
except (ImportError, AttributeError):
    version = "unknown"


class SarifFormatter(BaseFormatter):
    """
    Форматтер, выводящий результаты в формате SARIF (Static Analysis Results Interchange Format).
    Совместим с GitHub Code Scanning, Azure DevOps, SonarQube и другими инструментами.
    """

    # Mapping Gixy severity to SARIF
    SEVERITY_MAP = {
        'UNSPECIFIED': 'note',
        'LOW': 'note',
        'MEDIUM': 'warning',
        'HIGH': 'error',
    }

    def _get_sarif_level(self, severity):
        """Mapping Gixy severity to SARIF"""
        return self.SEVERITY_MAP.get(severity.upper(), 'warning')



    def format_reports(self, reports, stats):
        """
        Formatting reports to SARIF.

        Args:
            reports: dict {path: [list_of_issues]}
            stats: dict с подсчетами по severity (не используется напрямую,
                   но может быть добавлен в свойства)

        Returns:
            str: JSON строка в формате SARIF
        """
        # Собираем все уникальные правила (по plugin) и результаты
        rules_dict = {}      # plugin -> rule_info
        results_list = []    # список результатов
        artifacts_set = set() # уникальные пути файлов

        for path, issues in reports.items():
            artifacts_set.add(path)
            for issue in issues:
                plugin = issue['plugin']
                severity = issue.get('severity', 'UNSPECIFIED')
                level = self._get_sarif_level(severity)

                # Формируем информацию о правиле, если ещё не добавлено
                if plugin not in rules_dict:
                    rules_dict[plugin] = {
                        'id': plugin,
                        'name': issue.get('summary', plugin),
                        'shortDescription': {
                            'text': issue.get('summary', '')[:100]  # ограничим длину
                        },
                        'fullDescription': {
                            'text': issue.get('description', '')
                        },
                        'helpUri': issue.get('help_url', ''),
                        'properties': {
                            'reason': issue.get('reason', ''),
                            'config': issue.get('config', {})
                        }
                    }

                # Создаём результат
                result = {
                    'ruleId': plugin,
                    'level': level,
                    'message': {
                        'text': issue.get('description') or issue.get('summary') or 'Issue detected'
                    },
                    'locations': [
                        {
                            'physicalLocation': {
                                'artifactLocation': {
                                    'uri': path
                                },
                                'region': {
                                    'snippet':{
                                        'text': issue['config']
                                    }
                                }
                            }
                        }
                    ]
                }

                # Добавляем дополнительные поля, если они есть
                if issue.get('reason'):
                    result['properties'] = {'reason': issue['reason']}
                if issue.get('config'):
                    if 'properties' not in result:
                        result['properties'] = {}
                    result['properties']['config'] = issue['config']

                results_list.append(result)

        # Формируем rules в порядке, требуемом SARIF
        rules = list(rules_dict.values())

        # Формируем артефакты
        artifacts = [{'location': {'uri': path}} for path in sorted(artifacts_set)]

        # Собираем полный SARIF объект
        sarif_report = {
            "$schema": "https://docs.oasis-open.org/sarif/sarif-v2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "gixy",
                            "organization": "Yandex",
                            "informationUri": "https://github.com/yandex/gixy",
                            "version": version,
                            "rules": rules
                        }
                    },
                    "artifacts": artifacts,
                    "results": results_list,
                    "properties": {
                        "stats": stats
                    }
                }
            ]
        }

        # Сериализуем в JSON
        return json.dumps(sarif_report, sort_keys=False, indent=2, separators=(',', ': '))