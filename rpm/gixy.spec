########################################################################################

Summary:        Nginx configuration static analyzer
Name:           gixy
Version:        0.1.3
Release:        0%{?dist}
License:        MPLv2.0
Group:          Development/Utilities
URL:            https://github.com/yandex/gixy

Source:         https://github.com/yandex/%{name}/archive/v%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:  python-devel python-setuptools

Requires:       python-setuptools python-six >= 1.1.0 python-jinja >= 2.8
Requires:       python2-cached_property >= 1.2.0 python2-configargparse >= 0.11.0
Requires:       python-argparse >= 1.4.0 pyparsing >= 1.5.5 python-markupsafe

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
* Thu May 11 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.3-0
- Uses english versions in plugins references

* Tue May 02 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.2-0
- Fixed blank comments parsing
- Added "auth_request_set" directive

* Sat Apr 29 2017 Yandex Team <opensource@yandex-team.ru> - 0.1.1-0
- Initial build

