%define name fuel-nailgun
%{!?version: %define version 8.0.0}
%{!?release: %define release 1}

Summary: Nailgun package
Name: %{name}
Obsoletes: nailgun
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: Apache
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Prefix: %{_prefix}
BuildRequires:  python-setuptools
BuildRequires:  python-yaml
BuildRequires:  git
#BuildRequires: nodejs
BuildArch: noarch
Requires:    python-alembic >= 0.6.2
Requires:    python-amqplib >= 1.0.2
Requires:    python-anyjson >= 0.3.3
Requires:    python-argparse >= 1.2.1
Requires:    python-babel >= 1.3
Requires:    python-crypto >= 2.6.1
Requires:    python-decorator >= 3.4.0
Requires:    python-fysom >= 1.0.11
Requires:    python-iso8601 >= 0.1.9
Requires:    python-jinja2 >= 2.7
Requires:    python-jsonschema >= 2.3.0
Requires:    python-keystoneclient >= 0.11
Requires:    python-keystonemiddleware >= 1.2.0
Requires:    python-kombu >= 1:3.0.16
Requires:    python-mako >= 0.9.1
Requires:    python-markupsafe >= 0.18
Requires:    python-netaddr >= 0.7.10
Requires:    python-netifaces >= 0.8
Requires:    python-oslo-config >= 1:1.2.1
Requires:    python-oslo-serialization >= 1.0.0
Requires:    python-oslo-db >= 1.0.0
Requires:    python-paste >= 1.7.5.1
Requires:    python-ply >= 3.4
Requires:    python-psycopg2 >= 2.5.1
Requires:    python-requests >= 1.2.3
Requires:    python-simplejson >= 3.3.0
Requires:    python-six >= 1.5.2
Requires:    python-sqlalchemy >= 0.7.9
Requires:    python-stevedore >= 0.14
Requires:    python-urllib3 >= 1.7
Requires:    python-webpy >= 0.37
Requires:    python-wsgilog >= 0.3
Requires:    python-wsgiref >= 0.1.2
Requires:    PyYAML >= 3.10
Requires:    python-novaclient >= 2.17.0
Requires:    python-networkx-core >= 1.8.0
Requires:    python-networkx-core < 1.10.0
Requires:    python-cinderclient >= 1.0.7
Requires:    pydot-ng >= 1.0.0
Requires:    python-ordereddict >= 1.1
# Workaroud for babel bug
Requires:    pytz

BuildRequires: nodejs-nailgun

%description
Nailgun package

%prep
%setup -cq -n %{name}-%{version}

mkdir -p %{_builddir}/%{name}-%{version}/nailgun/node_modules/
cp -pr /usr/lib/node_modules/ %{_builddir}/%{name}-%{version}/nailgun/
cp -pr /usr/lib/node_modules/.bin %{_builddir}/%{name}-%{version}/nailgun/node_modules/

%build
cd %{_builddir}/%{name}-%{version}/nailgun && %{_builddir}/%{name}-%{version}/nailgun/node_modules/.bin/gulp build --static-dir=compressed_static
[ -n %{_builddir} ] && rm -rf %{_builddir}/%{name}-%{version}/nailgun/static
mv %{_builddir}/%{name}-%{version}/nailgun/compressed_static %{_builddir}/%{name}-%{version}/nailgun/static
cd %{_builddir}/%{name}-%{version}/nailgun && python setup.py build
cd %{_builddir}/%{name}-%{version}/fuel_upgrade_system/fuel_package_updates && python setup.py build

%install
cd %{_builddir}/%{name}-%{version}/nailgun && python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=%{_builddir}/%{name}-%{version}/nailgun/INSTALLED_FILES
cd %{_builddir}/%{name}-%{version}/fuel_upgrade_system/fuel_package_updates && python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=%{_builddir}/%{name}-%{version}/fuel_upgrade_system/fuel_package_updates/INSTALLED_FILES
mkdir -p %{buildroot}/opt/nailgun/bin
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}/etc/fuel
install -m 755 %{_builddir}/%{name}-%{version}/bin/fencing-agent.rb %{buildroot}/opt/nailgun/bin/fencing-agent.rb
install -m 644 %{_builddir}/%{name}-%{version}/bin/fencing-agent.cron %{buildroot}/etc/cron.d/fencing-agent
install -p -D -m 755 %{_builddir}/%{name}-%{version}/bin/download-debian-installer %{buildroot}%{_bindir}/download-debian-installer
install -p -D -m 644 %{_builddir}/%{name}-%{version}/nailgun/nailgun/fixtures/openstack.yaml %{buildroot}%{_datadir}/fuel-openstack-metadata/openstack.yaml
python -c "import yaml; print filter(lambda r: r['fields'].get('name'), yaml.safe_load(open('%{_builddir}/%{name}-%{version}/nailgun/nailgun/fixtures/openstack.yaml')))[0]['fields']['version']" > %{buildroot}%{_sysconfdir}/fuel_openstack_version

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{_builddir}/%{name}-%{version}/nailgun/INSTALLED_FILES
%defattr(0755,root,root)

%package -n fuel-openstack-metadata

Summary:   Fuel Openstack metadata files
Version:   %{version}
Release:   %{release}
License:   GPLv2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:       http://github.com/Mirantis

%description -n fuel-openstack-metadata
This package currently installs just a single file openstack.yaml

%files -n fuel-openstack-metadata
%defattr(-,root,root)
%{_datadir}/fuel-openstack-metadata/*
%{_sysconfdir}/fuel_openstack_version

%package -n fencing-agent
Summary:   Fencing agent
Version:   %{version}
Release:   %{release}
License:   GPLv2
BuildRoot: %{_tmppath}/%{name}-%{version}
URL:       http://mirantis.com
Requires:  rubygem-ohai

%description -n fencing-agent
Fuel fencing agent

%files -n fencing-agent
/opt/nailgun/bin/fencing-agent.rb
/etc/cron.d/fencing-agent
%defattr(-,root,root)


%package -n fuel-package-updates

Summary: Fuel package update downloader
Version: %{version}
Release: %{release}
License: Apache
Group: Development/Libraries
Prefix: %{_prefix}
BuildArch: noarch
Requires:  python-keystoneclient >= 0.11
Requires:  python-keystonemiddleware >= 1.2.0
Requires:  python-ordereddict >= 1.1

%description -n fuel-package-updates
Command line utility to download apt/yum repositories for Fuel

%files -n fuel-package-updates  -f %{_builddir}/%{name}-%{version}/fuel_upgrade_system/fuel_package_updates/INSTALLED_FILES
%defattr(0755,root,root)

%package -n fuel-provisioning-scripts

Summary: Fuel provisioning scripts
Version: %{version}
Release: %{release}
URL:     http://mirantis.com
License: Apache
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Requires:    wget

%description -n fuel-provisioning-scripts
Fuel provisioning scripts package.
This is a part of Fuel All-in-one Controle plane
for Openstack. For more info go to http://wiki.openstack.org/Fuel

%files -n fuel-provisioning-scripts
%defattr(-,root,root)
%{_bindir}/download-debian-installer
