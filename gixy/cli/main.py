import os
import sys
import logging
import copy

import gixy
from gixy.core.manager import Manager as Gixy
from gixy.formatters import get_all as formatters
from gixy.core.plugins_manager import PluginsManager
from gixy.core.config import Config
from gixy.cli.argparser import create_parser

LOG = logging.getLogger()


def _init_logger(debug=False):
    LOG.handlers = []
    log_level = logging.DEBUG if debug else logging.INFO
    logging.captureWarnings(True)

    LOG.setLevel(log_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('[%(module)s]\t%(levelname)s\t%(message)s'))
    LOG.addHandler(handler)
    LOG.debug("logging initialized")


def _create_plugin_help(option):
    if isinstance(option, (tuple, list, set)):
        default = ','.join(list(option))
    else:
        default = str(option)

    return 'Default: {}'.format(default)


def _get_cli_parser():
    parser = create_parser()
    parser.add_argument('nginx_file', nargs='?', type=str, default='/etc/nginx/nginx.conf', metavar='nginx.conf',
                        help='Path to nginx.conf, e.g. /etc/nginx/nginx.conf')

    parser.add_argument(
        '-v', '--version', action='version',
        version='Gixy v{}'.format(gixy.version))

    parser.add_argument(
        '-l', '--level', dest='level', action='count', default=0,
        help='Report issues of a given severity level or higher (-l for LOW, -ll for MEDIUM, -lll for HIGH)')

    default_formatter = 'console' if sys.stdout.isatty() else 'text'
    available_formatters = formatters().keys()
    parser.add_argument(
        '-f', '--format', dest='output_format', choices=available_formatters, default=default_formatter,
        type=str, help='Specify output format')

    parser.add_argument(
        '-o', '--output', dest='output_file', type=str,
        help='Write report to file')

    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true', default=False,
        help='Turn on debug mode')

    parser.add_argument(
        '--tests', dest='tests', type=str,
        help='Comma-separated list of tests to run')

    parser.add_argument(
        '--skips', dest='skips', type=str,
        help='Comma-separated list of tests to skip')

    parser.add_argument(
        '--disable-includes', dest='disable_includes', action='store_true', default=False,
        help='Disable "include" directive processing')

    group = parser.add_argument_group('plugins options')
    for plugin_cls in PluginsManager().plugins_classes:
        name = plugin_cls.__name__
        if not plugin_cls.options:
            continue

        options = copy.deepcopy(plugin_cls.options)
        for opt_key, opt_val in options.items():
            option_name = '--{plugin}-{key}'.format(plugin=name, key=opt_key).replace('_', '-')
            dst_name = '{plugin}:{key}'.format(plugin=name, key=opt_key)
            opt_type = str if isinstance(opt_val, (tuple, list, set)) else type(opt_val)
            group.add_argument(
                option_name, metavar=opt_key, dest=dst_name, type=opt_type,
                help=_create_plugin_help(opt_val)
            )

    return parser


def _is_nginx_file(file_path):
    s = open(file_path).read()
    return 'server {' in s or 'http {' in s


def main():
    parser = _get_cli_parser()
    args = parser.parse_args()
    _init_logger(args.debug)

    path = os.path.expanduser(args.nginx_file)
    if not os.path.isfile(path):
        sys.stderr.write('Please specify path to Nginx configuration.\n\n')
        parser.print_help()
        sys.exit(1)

    if not _is_nginx_file(path):
        sys.stderr.write('This is nginx config? Rly?\n')
        sys.exit(1)

    try:
        severity = gixy.severity.ALL[args.level]
    except IndexError:
        sys.stderr.write('Too high level filtering. Maximum level: -{}\n'.format('l' * (len(gixy.severity.ALL) - 1)))
        sys.exit(1)

    if args.tests:
        tests = [x.strip() for x in args.tests.split(',')]
    else:
        tests = None

    if args.skips:
        skips = [x.strip() for x in args.skips.split(',')]
    else:
        skips = None

    config = Config(
        severity=severity,
        output_format=args.output_format,
        output_file=args.output_file,
        plugins=tests,
        skips=skips,
        allow_includes=not args.disable_includes
    )

    for plugin_cls in PluginsManager().plugins_classes:
        name = plugin_cls.__name__
        options = copy.deepcopy(plugin_cls.options)
        for opt_key, opt_val in options.items():
            option_name = '{}:{}'.format(name, opt_key)
            if option_name not in args:
                continue

            val = getattr(args, option_name)
            if val is None:
                continue

            if isinstance(opt_val, tuple):
                val = tuple([x.strip() for x in val.split(',')])
            elif isinstance(opt_val, set):
                val = set([x.strip() for x in val.split(',')])
            elif isinstance(opt_val, list):
                val = [x.strip() for x in val.split(',')]
            options[opt_key] = val
        config.set_for(name, options)

    with Gixy(config=config) as yoda:
        yoda.audit(path)
        formatted = formatters()[config.output_format]().format(yoda)
        if args.output_file:
            with open(config.output_file, 'w') as f:
                f.write(formatted)
        else:
            print(formatted)

        if sum(yoda.stats.values()) > 0:
            # If something found - exit code must be 1, otherwise 0
            sys.exit(1)
        sys.exit(0)
