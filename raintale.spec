Name: raintale
Version: {{ raintale_version }}
Summary: Raintale is a Python utility for publishing a social media story built from archived web pages to multiple services.
Release: 1%{?dist}
License: MIT
Source0: %{name}-%{version}.tar.gz
ExclusiveArch: x86_64

BuildRequires: coreutils, sed, grep, tar, mktemp, python3-virtualenv, python38
Requires: python38, postgresql, libjpeg-turbo, zlib, libtiff, freetype-devel, freetype, lcms2, libwebp, tcl, tk, openjpeg2, fribidi, harfbuzz, libxcb
Requires(pre): shadow-utils, python38
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
export VIRTUAL_ENV=system
make generic_installer

# thanks -- https://fedoraproject.org/wiki/Packaging%3aUsersAndGroups
%pre
getent group dsa >/dev/null || groupadd -r dsa
getent passwd raintale >/dev/null || \
    useradd -r -g dsa -d /opt/raintale -s /sbin/nologin \
    -c "Raintale service account" raintale
exit 0

%install
echo RPM_BUILD_ROOT is $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/opt/raintale
mkdir -p ${RPM_BUILD_ROOT}/etc/systemd/system
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
bash ./installer/generic-unix/install-raintale.sh -- --install-directory ${RPM_BUILD_ROOT}/opt/raintale --python-exe /usr/bin/python --skip-script-install --raintale-user raintale --cli-wrapper-path ${RPM_BUILD_ROOT}/usr/bin/
# TODO: fix this, everything should stay in RPM_BUILD_ROOT
mv /etc/systemd/system/raintale-celery.service ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-celery.service
mv /etc/systemd/system/raintale-django.service ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-django.service
find ${RPM_BUILD_ROOT}/opt/raintale/raintale-virtualenv/bin -type f -exec sed -i "s?${RPM_BUILD_ROOT}??g" {} \;
echo 'MEMENTOEMBED_ENDPOINT="http://localhost:5550"' > ${RPM_BUILD_ROOT}/etc/raintale.conf
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-django.service
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/raintale-celery.service
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/usr/bin/tellstory
sed -i 's?\(python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Video Story.py"\)?#\1?g'  ${RPM_BUILD_ROOT}/opt/raintale/raintale-gui/add-raintale-scripts.sh
sed -i "s?^python ?/opt/raintale/raintale-virtualenv/bin/python ?g" ${RPM_BUILD_ROOT}/opt/raintale/raintale-gui/add-raintale-scripts.sh
sed -i "s?^python ?/opt/raintale/raintale-virtualenv/bin/python ?g" ${RPM_BUILD_ROOT}/opt/raintale/raintale-gui/set-raintale-database.sh


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, raintale, dsa, 0755)
/opt/raintale/
%attr(0644, raintale, dsa) %config(noreplace) /etc/raintale.conf
%attr(0755, root, root) /etc/systemd/system/raintale-django.service
%attr(0755, root, root) /etc/systemd/system/raintale-celery.service
%attr(0755, raintale, dsa) /usr/bin/tellstory

%post
su -l raintale -s /bin/bash /opt/raintale/raintale-gui/add-raintale-scripts.sh
/usr/bin/systemctl enable raintale-celery.service
/usr/bin/systemctl enable raintale-django.service

%preun
/usr/bin/systemctl stop raintale-django.service
/usr/bin/systemctl stop raintale-celery.service
/usr/bin/systemctl disable raintale-django.service
/usr/bin/systemctl disable raintale-celery.service

%postun
/usr/sbin/userdel raintale
find /opt/raintale -name __pycache__ -exec rm -rf {} \;
find /opt/raintale -name celerybeat-schedule -exec rm -rf {} \;
if [ -d /opt/raintale/raintale_with_wooey/raintale_with_wooey/user_uploads ]; then
    tar -C /opt/raintale/raintale_with_wooey/raintale_with_wooey -c -v -z -f /opt/raintale/user_uploads-backup-`date '+%Y%m%d%H%M%S'`.tar.gz user_uploads
    rm -rf /opt/raintale/raintale_with_wooey
fi
