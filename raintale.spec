Name: raintale
Version: {{ raintale_version }}
Summary: Raintale is a Python utility for publishing a social media story built from archived web pages to multiple services.
Release: 1%{?dist}
License: MIT
Source0: %{name}-%{version}.tar.gz
ExclusiveArch: x86_64

BuildRequires: coreutils, sed, grep, tar, mktemp, python3-virtualenv, python38
Requires: python38, postgresql, libjpeg-turbo, zlib, libtiff, freetype-devel, freetype, lcms, libwebp, tcl, tk, openjpeg2, fribidi, harfbuzz, libxcb
AutoReq: no

%description
Raintale is a utility for publishing social media stories from groups of archived web pages (mementos). Raintale uses MementoEmbed to extract memento information and then publishes a story to the given storyteller, a static file or an online social media service.

%define  debug_package %{nil}
%define _build_id_links none
%global _enable_debug_package 0
%global _enable_debug_package ${nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%prep
%setup -q

%build
rm -rf $RPM_BUILD_ROOT
make generic_installer

%install
echo RPM_BUILD_ROOT is $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/opt/raintale
mkdir -p ${RPM_BUILD_ROOT}/etc/systemd/system
bash ./installer/install-raintale.sh -- --install-directory ${RPM_BUILD_ROOT}/opt/raintale --python-exe /usr/bin/python --skip-script-install
# TODO: fix this, everything should stay in RPM_BUILD_ROOT
mv /etc/systemd/system/raintale-celery.service ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-celery.service
mv /etc/systemd/system/raintale-django.service ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-django.service
find ${RPM_BUILD_ROOT}/opt/raintale/raintale-virtualenv/bin -type f -exec sed -i "s?${RPM_BUILD_ROOT}??g" {} \;
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-django.service
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-celery.service
sed -i "s?^python ?/opt/raintale/raintale-virtualenv/bin/python ?g" ${RPM_BUILD_ROOT}/opt/raintale/raintale-gui/add-raintale-scripts.sh

%clean
rm -rf $RPM_BUILD_ROOT

%files
/opt/raintale/
/etc/systemd/system/raintale-django.service
/etc/systemd/system/raintale-celery.service
%attr(755, root, -)

%post
/opt/raintale/raintale-gui/add-raintale-scripts.sh
