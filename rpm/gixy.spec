########################################################################################

Summary:        Nginx configuration static analyzer
Name:           gixy
Version:        0.1.5
Release:        0%{?dist}
License:        MPLv2.0
Group:          Development/Utilities
URL:            https://github.com/yandex/gixy

Source:         https://github.com/yandex/%{name}/archive/v%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       python-setuptools
Requires:       python-jinja >= 3.1.5
Requires:       python-cached_property >= 2.0.1
Requires:       python2-configargparse >= 1.7
Requires:       pyparsing >= 3.2.1

Provides:       %{name} = %{verion}-%{release}

########################################################################################

%description
Gixy is a tool to analyze Nginx configuration. The main goal of Gixy is to prevent 
misconfiguration and automate flaw detection.

########################################################################################

%prep
%setup -qn %{name}-%{version}

%clean
rm -rf %{buildroot}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --prefix=%{_prefix} \
                        --root=%{buildroot}

########################################################################################

%files
%defattr(-,root,root,-)
%doc LICENSE AUTHORS README.md docs/*
%{python_sitelib}/*
%{_bindir}/%{name}

########################################################################################

%changelog
* Sun May 21 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.5-0
- Supported Python 2.6
- Supported multiple config files scanning
- Fixed summary count
- Fixed symlink resolution
- Minor improvements and fixes

* Sun May 14 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.4-0
- Allow processing stdin, file descriptors
- Fixed configuration parser

* Thu May 11 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.3-0
- Uses english versions in plugins references

* Tue May 02 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.2-0
- Fixed blank comments parsing
- Added "auth_request_set" directive

* Sat Apr 29 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.1-0
- Initial build

