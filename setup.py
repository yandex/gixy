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
    python_requires='>=3.9',
    install_requires=[
        'pyparsing>=3.2.1',
        'cached-property>=2.0.1',
        'Jinja2>=3.1.5',
        'ConfigArgParse>=1.7'
    ],
    entry_points={
        'console_scripts': ['gixy=gixy.cli.main:main'],
    },
    test_suite='nose.collector',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: 3.9',
        'Programming Language :: Python :: 3 :: 3.10',
        'Programming Language :: Python :: 3 :: 3.11',
        'Programming Language :: Python :: 3 :: 3.12',
        'Programming Language :: Python :: 3 :: 3.13',
    ],
    include_package_data=True
)
