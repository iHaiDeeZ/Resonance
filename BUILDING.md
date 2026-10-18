# Building Resonance

Flycast (Dreamcast / NAOMI / Atomiswave) for jailbroken PS4 homebrew, built in WSL Ubuntu with the
DolphinPS4 / Crema PS4 toolchain (clang 21 + libc++ 21 on OpenOrbis).

- Graphics: Flycast's Vulkan renderer on DolphinPS4's RADV/GNM port, presented through VideoOut
- CPU: Flycast's x86-64 SH4 and ARM7 dynarecs, RWX code near the eboot
- Memory: fast memory over PS4 direct memory with aliasing (16 KiB pages)
- Input: DualShock 4 (ScePad), one per signed-in user
- Network shares: Crema's layer (`port/ps4_netfs.cpp`), shares mounted at `/net/<name>`
- Audio: sceAudioOut, 44.1 kHz resampled to 48 kHz

```
scripts/clone-flycast.sh          # upstream Flycast at patches/BASE.txt into ~/resonance-build/src
git -C ~/resonance-build/src/flycast checkout -b ps4 && git apply patches/flycast-ps4.patch
scripts/seed-build-tree.sh        # sysroot + RADV build copied from Crema's build tree
scripts/build-netfs.sh            # libsmb2 and libnfs into the sysroot
scripts/rebuild-flycast.sh        # configure + build (logs in ~/resonance-build/logs)
RESONANCE_VERSION=01.00 scripts/package-resonance.sh
```

Run the scripts from WSL through `~/resonance` (the space in "PS4 Projects" breaks linker flags).
Send the package to the console from Windows (Git Bash), not from WSL:
`bash scripts/upload-to-console.sh out/Resonance-v01.00.pkg`.

Title ID `DCST00001`. The menu texts' translations are in `lang/` (`scripts/make-lang.py`), the logo
comes from `scripts/make-logo.py`, the app's pictures from `scripts/make-resonance-art.py`.
