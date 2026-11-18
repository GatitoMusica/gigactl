# Native package recipes

The Debian package in this fork remains the full desktop package. The
Arch `PKGBUILD` and Fedora RPM spec in this directory package only `gigactld`,
which is the system service required by GigaControl Plasma.

Both recipes pin the source to release commit
`8795f171dd78e884f298f862ff4e666687a9dcb7` (daemon version 1.0.3). Update the
pin and package version together when preparing a new daemon release.

The Arch install hook and RPM pre-install script mirror the hardware guard in
`debian/preinst`. Neither package starts or enables the service during
installation. The Arch package also avoids installing the optional
`modules-load.d` file: `gigactl.service` loads `ec_sys` when the service is
explicitly started.

Run these build commands from the repository root on the target distribution:

    (cd packaging/arch && makepkg --syncdeps --cleanbuild)

    COMMIT=$(sed -n 's/^%global commit //p' packaging/rpm/gigactld.spec)
    mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
    curl --fail --location "https://github.com/GatitoMusica/gigactl/archive/${COMMIT}.tar.gz" \
      -o "$HOME/rpmbuild/SOURCES/${COMMIT}.tar.gz"
    rpmbuild -ba --define "_topdir $HOME/rpmbuild" packaging/rpm/gigactld.spec

The RPM macros leave the service stopped and disabled on a fresh install; the
administrator can enable it explicitly. The package's `ExecStopPost` failsafe
continues to return fans to firmware when a running service is stopped or
removed.

After this repository's Debian release workflow publishes a `v1.0.3`-style tag, the
`release-native-packages` workflow builds the RPM and Arch package and attaches
them to that same GitHub release. It does not start the service on the build
runner.

GitHub also provides source-code ZIP and tar.gz archives for the tagged release.
