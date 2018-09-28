# flake8: noqa

from configargparse import *
from six.moves import StringIO

from gixy.core.plugins_manager import PluginsManager

# used while parsing args to keep track of where they came from
_COMMAND_LINE_SOURCE_KEY = 'command_line'
_ENV_VAR_SOURCE_KEY = 'environment_variables'
_CONFIG_FILE_SOURCE_KEY = 'config_file'
_DEFAULTS_SOURCE_KEY = 'defaults'


class GixyConfigParser(DefaultConfigFileParser):
    def get_syntax_description(self):
        return ''

    def parse(self, stream):
        """Parses the keys + values from a config file."""

        items = OrderedDict()
        prefix = ''
        for i, line in enumerate(stream):
            line = line.strip()
            if not line or line[0] in ['#', ';'] or line.startswith('---'):
                continue
            if line[0] == '[':
                prefix = '%s-' % line[1:-1].replace('_', '-')
                continue

            white_space = '\\s*'
            key = '(?P<key>[^:=;#\s]+?)'
            value = white_space + '[:=\s]' + white_space + '(?P<value>.+?)'
            comment = white_space + '(?P<comment>\\s[;#].*)?'

            key_only_match = re.match('^' + key + comment + '$', line)
            if key_only_match:
                key = key_only_match.group('key')
                items[key] = 'true'
                continue

            key_value_match = re.match('^' + key + value + comment + '$', line)
            if key_value_match:
                key = key_value_match.group('key')
                value = key_value_match.group('value')

                if value.startswith('[') and value.endswith(']'):
                    # handle special case of lists
                    value = [elem.strip() for elem in value[1:-1].split(',')]

                items[prefix + key] = value
                continue

            raise ConfigFileParserException('Unexpected line %s in %s: %s' % (i,
                                                                              getattr(stream, 'name', 'stream'), line))
        return items

    def serialize(self, items):
        """Does the inverse of config parsing by taking parsed values and
        converting them back to a string representing config file contents.
        """
        r = StringIO()
        for key, value in items.items():
            if type(value) == OrderedDict:
                r.write('\n[%s]\n' % key)
                r.write(self.serialize(value))
            else:
                value, help = value
                if help:
                    r.write('; %s\n' % help)
                r.write('%s = %s\n' % (key, value))
        return r.getvalue()


class GixyHelpFormatter(HelpFormatter):
    def format_help(self):
        manager = PluginsManager()
        help_message = super(GixyHelpFormatter, self).format_help()
        if 'plugins options:' in help_message:
            # Print available blugins _only_ if we prints options for it
            plugins = '\n'.join('\t' + plugin.__name__ for plugin in manager.plugins_classes)
            help_message = '{orig}\n\navailable plugins:\n{plugins}\n'.format(orig=help_message, plugins=plugins)
        return help_message


class ArgsParser(ArgumentParser):
    def get_possible_config_keys(self, action):
        """This method decides which actions can be set in a config file and
        what their keys will be. It returns a list of 0 or more config keys that
        can be used to set the given action's value in a config file.
        """
        keys = []
        for arg in action.option_strings:
            if arg in ['--config', '--write-config', '--version']:
                continue
            if any([arg.startswith(2 * c) for c in self.prefix_chars]):
                keys += [arg[2:], arg]  # eg. for '--bla' return ['bla', '--bla']

        return keys

    def get_items_for_config_file_output(self, source_to_settings,
                                         parsed_namespace):
        """Converts the given settings back to a dictionary that can be passed
        to ConfigFormatParser.serialize(..).

        Args:
            source_to_settings: the dictionary described in parse_known_args()
            parsed_namespace: namespace object created within parse_known_args()
        Returns:
            an OrderedDict where keys are strings and values are either strings
            or lists
        """
        config_file_items = OrderedDict()
        for source, settings in source_to_settings.items():
            if source == _COMMAND_LINE_SOURCE_KEY:
                _, existing_command_line_args = settings['']
                for action in self._actions:
                    config_file_keys = self.get_possible_config_keys(action)
                    if config_file_keys and not action.is_positional_arg and \
                        already_on_command_line(existing_command_line_args,
                                                action.option_strings):
                        value = getattr(parsed_namespace, action.dest, None)
                        if value is not None:
                            if type(value) is bool:
                                value = str(value).lower()
                            if ':' in action.dest:
                                section, key = action.dest.split(':', 2)
                                key = key.replace('_', '-')
                                if section not in config_file_items:
                                    config_file_items[section] = OrderedDict()
                                config_file_items[section][key] = (value, action.help)
                            else:
                                config_file_items[config_file_keys[0]] = (value, action.help)
            elif source.startswith(_CONFIG_FILE_SOURCE_KEY):
                for key, (action, value) in settings.items():
                    if ':' in action.dest:
                        section, key = action.dest.split(':', 2)
                        key = key.replace('_', '-')
                        if section not in config_file_items:
                            config_file_items[section] = OrderedDict()
                        config_file_items[section][key] = (value, action.help)
                    else:
                        config_file_items[key] = (value, action.help)
        return config_file_items


def create_parser():
    return ArgsParser(
        description='Gixy - a Nginx configuration [sec]analyzer\n\n',
        formatter_class=GixyHelpFormatter,
        config_file_parser_class=GixyConfigParser,
        auto_env_var_prefix='GIXY_',
        add_env_var_help=False,
        default_config_files=['/etc/gixy/gixy.cfg', '~/.config/gixy/gixy.conf'],
        args_for_setting_config_path=['-c', '--config'],
        args_for_writing_out_config_file=['--write-config'],
        add_config_file_help=False
    )
