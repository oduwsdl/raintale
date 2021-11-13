Name: raintale
Version: {{ raintale_version }}
Summary: Raintale is a Python utility for publishing a social media story built from archived web pages to multiple services.
Release: 1%{?dist}
License: MIT
Source0: %{name}-%{version}.tar.gz
ExclusiveArch: x86_64

BuildRequires: coreutils, sed, grep, tar, mktemp, python3-virtualenv, python38
Requires: python38
# Requires: nodejs, sed, grep, tar, which, redis, python38, cairo, nss, atk, at-spi2-atk, cups-libs, libdrm-devel, libxkbcommon-devel, libXcomposite, libXdamage, libXrandr-devel, mesa-libgbm, pango, alsa-lib, libxshmfence
# Requires: nodejs, sed, grep, tar, python3-virtualenv, makeself, which, python38, redis, libX11, libXcomposite, libXdamage, libXext, libXfixes, libXrandr, alsa-lib, atk, at-spi2-atk, at-spi2-core, cairo, cups-libs, libdrm, mesa-libgbm, libgfortran, libjpeg-turbo, libjpeg-turbo-devel, libjpeg-turbo-utils, libffi, libffi-devel, xz-devel, nspr, nspr-devel, nss, nss-devel, nss-util, nss-util-devel, pango, pango-devel, libpng16, libquadmath, libquadmath-devel, libxcb, libxcb-devel, libxshmfence, libxshmfence-devel, zlib, zlib-devel
# Provides: libffi-9c61262e.so.8.1.0(LIBFFI_BASE_8.0)(64bit), libffi-9c61262e.so.8.1.0(LIBFFI_CLOSURE_8.0)(64bit), libgfortran-040039e1.so.5.0.0(GFORTRAN_8)(64bit), libgfortran-2e0d59d6.so.5.0.0(GFORTRAN_8)(64bit), libjpeg-183418da.so.9.4.0(LIBJPEG_9.0)(64bit), liblzma-d540a118.so.5.2.5(XZ_5.0)(64bit), libpng16, libpng16-213e245f.so.16.37.0(PNG16_0)(64bit), libquadmath-2d0c479f.so.0.0.0(QUADMATH_1.0)(64bit), libquadmath-96973f99.so.0.0.0(QUADMATH_1.0)(64bit), libz-dd453c56.so.1.2.11(ZLIB_1.2.3.4)(64bit), libz-dd453c56.so.1.2.11(ZLIB_1.2.9)(64bit)
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
