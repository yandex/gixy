import re
from setuptools import setup, find_packages

with open('gixy/__init__.py', 'r') as fd:
    version = re.search(r'^version\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='gixy',
    version=version,
    description='Nginx configuration [sec]analyzer',
    keywords='nginx security lint static-analysis',
    author='Yandex IS Team',
    author_email='buglloc@yandex.ru',
    url='https://github.com/yandex/gixy',
    install_requires=[
        'pyparsing>=1.5.5',
        'cached-property>=1.2.0',
        'argparse>=1.4.0',
        'six>=1.1.0',
        'Jinja2>=2.8',
        'ConfigArgParse>=0.11.0'
    ],
    entry_points={
        'console_scripts': ['gixy=gixy.cli.main:main'],
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
    ],
    include_package_data=True,
    )
