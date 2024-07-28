import os
from os import path
import json
import pytest

from ..utils import *
from gixy.core.manager import Manager as Gixy
from gixy.core.plugins_manager import PluginsManager
from gixy.core.config import Config


def generate_config_test_cases():
    tested_plugins = set()
    tested_fp_plugins = set()

    config_cases = []
    config_fp_cases = []

    conf_dir = path.join(path.dirname(__file__), 'simply')
    for plugin in os.listdir(conf_dir):
        if plugin in ('.', '..'):
            continue

        plugin_path = path.join(conf_dir, plugin)
        if not path.isdir(plugin_path):
            continue

        config = {}
        if path.exists(path.join(plugin_path, 'config.json')):
            with open(path.join(plugin_path, 'config.json'), 'r') as file:
                config = json.loads(file.read())

        for test_case in os.listdir(plugin_path):
            if not test_case.endswith('.conf'):
                continue

            config_path = path.join(plugin_path, test_case)
            if not test_case.endswith('_fp.conf'):
                # Not False Positive test
                tested_plugins.add(plugin)
                config_cases.append((plugin, config_path, config))
            else:
                tested_fp_plugins.add(plugin)
                config_fp_cases.append((plugin, config_path, config))

    manager = PluginsManager()
    for plugin in manager.plugins:
        plugin = plugin.name
        assert plugin in tested_plugins, 'Plugin {name!r} should have at least one simple test config'.format(name=plugin)
        assert plugin in tested_fp_plugins, 'Plugin {name!r} should have at least one simple test config with false positive'.format(name=plugin)

    return config_cases, config_fp_cases


all_config_cases, all_config_fp_cases = generate_config_test_cases()


def parse_plugin_options(config_path):
    with open(config_path, 'r') as f:
        config_line = f.readline()
        if config_line.startswith('# Options: '):
            return json.loads(config_line[10:])
    return None


def yoda_provider(plugin, plugin_options=None):
    config = Config(
        allow_includes=False,
        plugins=[plugin]
    )
    if plugin_options:
        config.set_for(plugin, plugin_options)
    return Gixy(config=config)


@pytest.mark.parametrize('plugin,config_path,test_config', all_config_cases)
def test_configuration(plugin, config_path, test_config):
    plugin_options = parse_plugin_options(config_path)
    with yoda_provider(plugin, plugin_options) as yoda:
        yoda.audit(config_path, open(config_path, mode='r'))
        formatter = BaseFormatter()
        formatter.feed(config_path, yoda)
        _, results = formatter.reports.popitem()

        assert len(results) == 1, 'Should have one report'
        result = results[0]

        if 'severity' in test_config:
            if not hasattr(test_config['severity'], '__iter__'):
                assert result['severity'] == test_config['severity']
            else:
                assert result['severity'] in test_config['severity']
        assert result['plugin'] == plugin
        assert result['summary']
        assert result['description']
        assert result['config']
        assert result['help_url'].startswith('https://'), 'help_url must starts with https://. It\'is URL!'


@pytest.mark.parametrize('plugin,config_path,test_config', all_config_fp_cases)
def test_configuration_fp(plugin, config_path, test_config):
    with yoda_provider(plugin) as yoda:
        yoda.audit(config_path, open(config_path, mode='r'))
        assert len([x for x in yoda.results]) == 0, 'False positive configuration must not trigger any plugins'
