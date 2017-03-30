from nose.tools import assert_equals, assert_true, assert_in
import os
from os import path
import json

import gixy
from ..utils import *
from gixy.core.manager import Manager as Gixy
from gixy.core.plugins_manager import PluginsManager
from gixy.core.config import Config


def setup_module():
    pass


def teardown_module():
    pass


def test_from_config():
    tested_plugins = set()
    tested_fp_plugins = set()

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
                test_func = check_configuration
            else:
                tested_fp_plugins.add(plugin)
                test_func = check_configuration_fp

            yield test_func, plugin, config_path, config

    manager = PluginsManager()
    for plugin in manager.plugins:
        plugin = plugin.name
        assert_true(plugin in tested_plugins,
                    'Plugin "{}" should have at least one simple test config'.format(plugin))
        assert_true(plugin in tested_fp_plugins,
                    'Plugin "{}" should have at least one simple test config with false positive'.format(plugin))


def yoda_provider(plugin):
    config = Config(
        allow_includes=False,
        plugins=[plugin]
    )
    return Gixy(config=config)


def check_configuration(plugin, config_path, test_config):
    with yoda_provider(plugin) as yoda:
        yoda.audit(config_path)
        results = RawFormatter().format(yoda)

        assert_equals(len(results), 1, 'Should have one report')
        result = results[0]

        if 'severity' in test_config:
            if not hasattr(test_config['severity'], '__iter__'):
                assert_equals(result['severity'], test_config['severity'])
            else:
                assert_in(result['severity'], test_config['severity'])
        assert_equals(result['plugin'], plugin)
        assert_true(result['summary'])
        assert_true(result['description'])
        assert_true(result['config'])
        assert_true(result['help_url'].startswith('https://'),
                    'help_url must starts with https://. It\'is URL!')


def check_configuration_fp(plugin, config_path, test_config):
    with yoda_provider(plugin) as yoda:
        yoda.audit(config_path)
        results = RawFormatter().format(yoda)

        assert_equals(len(results), 0,
                      'False positive configuration must not trigger any plugins')
