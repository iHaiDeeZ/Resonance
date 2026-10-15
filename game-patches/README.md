# Resonance patch library

Patches change how a Dreamcast game runs: 60 fps, widescreen, removing the flicker filter, fixes.
Resonance downloads the patch for the game being started from this folder when
**Settings → System → Patch Source** is **Download automatically**. The patch is switched on by
itself. Players can switch any patch off in the quick menu (L3+R3 → Cheats & Patches), and
Resonance remembers that per game.

## Other sources Resonance reads

- **60 fps codes:** the community's [Flycast Widescreen Compatibility and Cheat Chart](https://github.com/nexus382/Flycast-Widescreen-Compatability-And-Cheat-Chart)
  by nexus382. When a game starts, Resonance reads the chart's "60 FPS Cheats" column on GitHub. It uses a
  code only when the row's region matches the disc's region (NA, EU or JP, from the product id). The chart
  isn't copied here: add 60 fps codes there, and every Resonance install picks them up.
- **Widescreen:** Flycast's built-in widescreen patches (about 230 games), used when Widescreen is
  set to **Supported games**.

## Adding a patch

1. Add the patch file to this folder. Use one of two formats:
   - **RetroArch `.cht`**, the format Flycast and libretro's cheat database use (`cheatN_desc`,
     `cheatN_address`, `cheatN_value`, `cheatN_cheat_type`, `cheatN_memory_search_size`, ...).
   - **A `.txt` list of GameShark / CodeBreaker codes:** a line with the patch's name, then its
     codes, one `XXXXXXXX YYYYYYYY` pair per line. Lines starting with `#` are comments.

     ```
     # Example layout (not a real code)
     60 FPS
     XXXXXXXX YYYYYYYY
     XXXXXXXX YYYYYYYY
     ```

2. Add a line for it to [`index.txt`](index.txt), with tabs between the fields:

   ```
   <file name>	<product id>	<title>
   ```

   - The **product id** is the disc's id, as in the box art database (for example `T13002N`). It
     matches exactly.
   - The **title** matches by its words when the product id is empty or differs (for example
     another region's disc).

3. Name each patch in the file by what it does ("60 FPS", "Widescreen 16:9"), and say where the
   codes come from in a comment. Only add codes you have tried on Resonance or Flycast.

## The player's own patches

Patches can also go on the console without this library. A `.cht` or `.txt` file in
`/data/Resonance/patches` is used for a game when its name is the game's product id (`T13002N.cht`)
or the game's title. That folder is read even when Patch Source is **Patches folder only**.
