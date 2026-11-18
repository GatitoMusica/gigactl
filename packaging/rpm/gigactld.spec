%global commit 8795f171dd78e884f298f862ff4e666687a9dcb7

Name:           gigactld
Version:        1.0.3
Release:        1%{?dist}
Summary:        System daemon for GigaControl laptop controls
License:        MIT
URL:            https://github.com/smairio/gigactl
Source0:        https://github.com/smairio/gigactl/archive/%{commit}.tar.gz
BuildArch:      noarch

BuildRequires:  systemd-rpm-macros
Requires:       dbus
Requires:       polkit
Requires:       python3 >= 3.10
Requires:       python3-gobject-base
Requires:       systemd

%description
The gigactld system daemon owns Embedded Controller access and provides the
GigaControl D-Bus API for supported Gigabyte G5, G6 and G7 laptops.

%prep
%autosetup -n gigactl-%{commit}

%build
# The daemon is Python code; no compilation step is required.

%install
install -d %{buildroot}%{_prefix}/lib/gigactl/gigactld
install -m 0644 daemon/gigactld/*.py \
    %{buildroot}%{_prefix}/lib/gigactl/gigactld/
install -D -m 0755 debian/bin/launcher \
    %{buildroot}%{_prefix}/lib/gigactl/launcher
install -d %{buildroot}%{_bindir}
ln -s %{_prefix}/lib/gigactl/launcher \
    %{buildroot}%{_bindir}/gigactld

install -D -m 0644 daemon/data/gigactl.service \
    %{buildroot}%{_unitdir}/gigactl.service
install -D -m 0644 daemon/data/io.github.smairio.gigactl.conf \
    %{buildroot}%{_datadir}/dbus-1/system.d/io.github.smairio.gigactl.conf
install -D -m 0644 daemon/data/io.github.smairio.gigactl.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/io.github.smairio.gigactl.policy
install -D -m 0644 debian/extra/modprobe.d/gigactl.conf \
    %{buildroot}%{_prefix}/lib/modprobe.d/gigactl.conf
install -d %{buildroot}%{_prefix}/lib/systemd/system-preset
printf 'disable gigactl.service\n' > %{buildroot}%{_prefix}/lib/systemd/system-preset/90-gigactld.preset
install -D -m 0644 man/gigactld.8 \
    %{buildroot}%{_mandir}/man8/gigactld.8

%pre
if [ "$1" -gt 1 ] || [ "${GIGACTL_FORCE_INSTALL:-0}" = 1 ]; then
    exit 0
fi
vendor=$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || true)
model=$(cat /sys/class/dmi/id/product_name 2>/dev/null || true)
case "$vendor" in
    GIGABYTE*|Gigabyte*) ;;
    *) echo "gigactld: refusing installation on '$vendor $model' (supported: Gigabyte G5/G6/G7)." >&2; exit 1 ;;
esac
case "$model" in
    'G6 KF'|G5*|G6*|G7*) ;;
    *) echo "gigactld: refusing installation on '$vendor $model' (supported: Gigabyte G5/G6/G7)." >&2; exit 1 ;;
esac

%post
# The systemd macros reload/preset the unit but do not start it. The service
# loads ec_sys in ExecStartPre only after an administrator starts it.
%systemd_post gigactl.service

%preun
%systemd_preun gigactl.service

%postun
%systemd_postun gigactl.service

%files
%license LICENSE
%{_bindir}/gigactld
%{_prefix}/lib/gigactl/launcher
%{_prefix}/lib/gigactl/gigactld/*.py
%{_unitdir}/gigactl.service
%{_datadir}/dbus-1/system.d/io.github.smairio.gigactl.conf
%{_datadir}/polkit-1/actions/io.github.smairio.gigactl.policy
%{_prefix}/lib/modprobe.d/gigactl.conf
%{_prefix}/lib/systemd/system-preset/90-gigactld.preset
%{_mandir}/man8/gigactld.8*

%changelog
* Wed Nov 18 2026 GigaControl maintainers - 1.0.3-1
- Add an RPM package for the upstream daemon.
