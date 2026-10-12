#!/usr/bin/env bash
# Package the PS4 Flycast build (after configure-flycast.sh + build-flycast.sh) as Resonance (formerly
# DeCast-S4), DCST00001 (IV0000-DCST00001_00-DECASTS400000000.pkg:
# the IDs stay, so an update installs over the earlier builds and keeps /data/Resonance).
#   RESONANCE_VERSION=01.00 package-resonance.sh
# Older builds of this app are deleted from out/. The console gets the package from Windows with
# scripts/upload-to-console.sh (uploads sent from WSL were lost on the console).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
BUILD="$PS4_BUILD_ROOT/build/flycast"
EBOOT="$BUILD/shell/ps4/flycast_eboot/eboot.bin"
VERSION="${RESONANCE_VERSION:-01.00}"
HOST="ftp://${PS4_HOST:-192.168.0.90}:${PS4_FTP_PORT:-2121}"

[ -f "$EBOOT" ] || { echo "missing $EBOOT: build first" >&2; exit 1; }
[[ "$VERSION" =~ ^[0-9][0-9]\.[0-9][0-9]$ ]] || { echo "version must look like 01.00" >&2; exit 1; }
STAGE="$PS4_BUILD_ROOT/build/resonance-stage"
rm -rf "$STAGE"
mkdir -p "$STAGE/sce_sys"
cp "$EBOOT" "$STAGE/eboot.bin"
cp "$HERE/../sce_sys/icon0.png" "$HERE/../sce_sys/pic1.png" "$STAGE/sce_sys/"
echo "$VERSION" > "$STAGE/version.txt"
# the home screen's fonts, menu sounds, CA bundle and opening pictures (launcher-assets/launcher)
cp -r "$HERE/../launcher-assets/launcher" "$STAGE/"
# PkgTool's pkg_build crashes ("Sequence contains no elements") on empty folders.
find "$STAGE" -type d -empty -delete
# Vulkan (RADV on GNM) runs under the plain homebrew identity (4.5 GiB of direct memory).
PKG="$(SFO_STYLE=plain NO_RIGHT_SPRX=1 DOLPHIN_PS4_MODULES_DIR=/nonexistent "$HERE/make-pkg.sh" "$STAGE" DCST00001 "Resonance" "$VERSION" DECASTS4 "$PS4_BUILD_ROOT/out" | tail -1)"
ls -la "$PKG"
# a copy next to the repo (E:\PS4 Projects\Resonance\out), easy to find from Windows; *.pkg is ignored by git
mkdir -p "$HERE/../out"
NAME="Resonance-v$VERSION.pkg"
cp "$PKG" "$HERE/../out/$NAME"
# the update archive for a GitHub release (shell/ps4/updater.cpp): the installed app runs it from
# /data/Resonance/app; ustar, which the updater unpacks
UPDATE="Resonance-v$VERSION-update.tar"
tar --format=ustar -C "$STAGE" -cf "$HERE/../out/$UPDATE" eboot.bin version.txt launcher
find "$HERE/../out" -maxdepth 1 \( -name '*.pkg' -o -name '*-update.tar' \) ! -name "$NAME" ! -name "$UPDATE" -print -delete | sed 's|^|removed old |'
rm -f /tmp/DeCast-S4-v*.pkg /tmp/Resonance-v*.pkg
# Keep the symbols of every packaged build: crash logs must be symbolized against the exact binary.
mkdir -p "$PS4_BUILD_ROOT/oelf"
cp "$BUILD/shell/ps4/flycast_eboot/flycast.oelf" "$PS4_BUILD_ROOT/oelf/v$VERSION.oelf"
cp "$BUILD/flycast" "$PS4_BUILD_ROOT/oelf/v$VERSION.elf"
if [ "${1:-}" = upload ]; then
    # from Windows only: see scripts/upload-to-console.sh
    echo "now, from Windows (Git Bash): scripts/upload-to-console.sh out/$NAME"
fi

