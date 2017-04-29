########################################################################################

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

########################################################################################

%define pkg_name    argparse
%define pkg_version r140

########################################################################################

Summary:        Python command-line parsing library
Name:           python-argparse
Version:        1.4.0
Release:        0%{?dist}
License:        Python License
Group:          Development/Libraries
URL:            https://github.com/ThomasWaldmann/argparse

Source:         https://github.com/ThomasWaldmann/%{pkg_name}/archive/%{pkg_version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:  python >= 2.3 python-setuptools

Requires:       python >= 2.3 python-setuptools

Provides:       %{name} = %{verion}-%{release}

########################################################################################

%description
The argparse module makes it easy to write user friendly command line interfaces.

The program defines what arguments it requires, and argparse will figure out
how to parse those out of sys.argv. The argparse module also automatically
generates help and usage messages and issues errors when users give the program
invalid arguments.

As of Python >= 2.7 and >= 3.2, the argparse module is maintained within the
Python standard library. For users who still need to support Python < 2.7 or
< 3.2, it is also provided as a separate package, which tries to stay
compatible with the module in the standard library, but also supports older
Python versions.

argparse is licensed under the Python license, for details see LICENSE.txt.

########################################################################################

%prep
%setup -qn %{pkg_name}-%{pkg_version}

%clean
rm -rf %{buildroot}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --prefix=%{_prefix} \
                        --single-version-externally-managed -O1 \
                        --root=%{buildroot}

########################################################################################

%files
%defattr(-,root,root,-)
%doc LICENSE.txt NEWS.txt README.txt
%{python_sitelib}/*

########################################################################################

%changelog
* Sat Apr 29 2017 Yandex Team <opensource@yandex-team.ru> - 1.4.0-0
- Initial build

