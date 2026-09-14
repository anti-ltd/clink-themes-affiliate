# Clink affiliate themes

Partner themes for Clink. This repository is included by default and cannot be removed from the app. **Affiliate** appears immediately after **Official** in the theme editor. Downloads and selection are free; affiliate themes cannot be edited, renamed, duplicated, or exported in the app.

**Takeoff Light** and **Takeoff Dark** are the first affiliate themes (ids `take-off-*`, from before the affiliate corrected the spelling): one electronic-paper keyboard on a panel and on an inverted panel, both monospaced and both printed in the affiliate's blue (`0056F7`). The light theme is mint-white paper (`F4FFFB`) with the blue filtered into a muted navy pigment for the legends, frames, grain and suggestion bar. The dark theme is the same sheet inverted — the material bottoms a panel out near 12%, never true black — with the blue printed as a pale periwinkle pigment instead. A light panel holds only two grey rungs, so each theme draws its function keys with whichever colour lands them on the other one: the blue on the light panel, the mint-white on the dark. Letters and the space bar keep the ground's own rung. The manifest is built from `Themes/` and is no longer empty.

**ThreadFlow Dark** and **ThreadFlow Light** are the second affiliate: translucent mechanical caps over visible switches, monospaced throughout. The dark theme is smoked caps (`1D1D1F`) on a near-black deck (`0C0C0D`) with primary-text legends (`F6F4EF`) and secondary (`C7C4BD`) on the function keys; the light theme swaps those four neutrals' roles, so the two text tones become the deck and the caps and the two surface tones become the legends. The Switches renderer colours each key's exposed switch assembly from the resolved lit colour, then the key colour, then the accent — so both themes paint the character keys with their own cap colour to keep those switches neutral, leaving the brand accent (`E2891F`) on the controls and the hover amber (`F0983A`) on a lit Shift or Return.

**Delphi Day** and **Delphi Night** are the third affiliate: Classic keys in monospaced semibold — cream over sage with dark-green legends, and its night sibling in near-black with pale legends — each with the number row painted in the brand colour through Canvas.

**Threadify Light** and **Threadify Dark** are the fourth affiliate: flat Solid keys in the system face — the brand's UI is flat, and a sculpted material glazes a saturated red rather than holding it — built from the brand's own CSS tokens — `0A0A0A` ground, `171717` surface, `FAFAFA` and `737373` type, `DC2626` red and `F87171` for its hover step. The red is placed where the site places it: Return is the primary button, solid `DC2626` with white type; the function keys take `2A1010`, the red-tinted dark surface the app uses for a selected cell; and Backspace flashes the brand red rather than the system's. The keys carry no outline at all: their buttons have none, and a key is a button — the light theme separates its white caps with an `E5E5E5` deck rather than drawing an edge around each one. The light theme reads the same ramp from the other end. Only the dark theme carries the site's glow as a background gradient, stop for stop; the brand defines no light equivalent, so `FEF2F2` and the lighter hairline alpha are the pair's only derived values.

**Clicks 'n Clacks Light** and **Clicks 'n Clacks Dark** are the fifth affiliate: 3D Mechanical caps with sloped walls on a raised base, in Space Mono's stand-in — the site's own face. The light theme is `F3EDD5` cream keycaps on an `A89984` taupe case with `0C0C0C` legends; the dark theme is the `3E3633` dark brown the affiliate asked for, case and caps, with cream legends. Both wear accent keycaps drawn from the ramp sampled off the brand icon — `F50F24` Shift, `FC6906` Backspace, `F5DC33` 123, `86DC36` globe and `14A3FE` Return — with black legends throughout, the way the wordmark sets black type on colour.

**Quiche Industries Day** and **Quiche Industries Night** are the sixth affiliate: Liquid Glass, in Avenir — the closest face iOS ships to their DM Sans. Quiche Browser is soft and translucent, so the keyboard refracts rather than sits on top of it: Clear glass over a barely tinted `F5F5F5` deck by day, Regular over `111111` by night. Their palette is greyscale by design, so the themes are too, and the only thing that ever lights up is the one grey their own UI emphasises with: `111111` by day, their heading and link color, and `AAAAAA` by night, because emphasis lifts in a dark interface instead of darkening.

**Walley Light** and **Walley Dark** are the seventh affiliate: Slab keys — broad bevel, satin face — in Futura, picked to echo the geometry of their W. The lime `CDDC3A` and the green `5CB760` are sampled from the app icon — from the dense middle of each gradient, not the lit edge a single pixel lands on, and they are the only colors on the board: Return wears the lime, Shift lights to the green, everything else is neutral. The icon's own ground is `000000`, which the dark theme uses as its deck; the light theme's `E7E8E0` and both themes' near-black/near-white legends are derived, since the brand is dark-only.

## Permission

Every theme here uses its affiliate's name, and in most cases their colors, **with that affiliate's permission** — several asked specifically that this be visible rather than assumed. The app says so in the sheet behind a theme's ⓘ, and only for themes from this repository: a community repository can publish a link too, and its author is a publisher, not an affiliate. Do not add a theme here until that permission exists in writing.

## Links

`links.json` at the repository root maps a theme id to an `https://` URL — either bare, or as `{"url": …, "description": …}` — and `tools/build-manifest.py` merges them into that theme's manifest entry as `link` and `description`. A description is one paragraph, at most 240 characters, no line breaks. Themes absent from the file carry no link, which is the normal case. A link is metadata rather than theme bytes, so adding or changing one never moves the release version and cached manifests keep resolving to the assets they were published with. The build fails on an id that is not in `Themes/` and on any URL that is not `https://`.

In the app an ⓘ on the theme's catalog tile opens a card naming the publisher, showing the description and offering one button to the site. The tap itself opens nothing. Write the description as the affiliate would say it out loud.

## Structure and publishing

Like the official and unofficial repositories, theme JSON belongs in `Themes/`, the catalog is generated by `tools/build-manifest.py`, and `.github/workflows/release.yml` publishes GitHub release assets automatically on `main` (or manually through Actions).

Run:

```sh
python3 -m unittest discover -s tests
python3 tools/build-manifest.py
```

The workflow publishes the manifest even when there are no themes. Each distinct asset set receives a permanent content-derived release tag; existing release assets are retained so cached manifests continue to verify. The latest-release manifest URL is the app's discovery endpoint.

## Adding an approved affiliate theme

Add a `.clinktheme` JSON file with a permanent lowercase ID matching its filename and a visible name. Themes must be data-only, under 128 KB, without photos, artwork image references, or executable content. Use the same Theme schema as `clink-themes`. Review the affiliate's rights and attribution before including their material. The repository license's third-party terms apply to separately licensed content.

Run the checks above and inspect the theme in Clink before publishing. Do not add placeholder or sample themes to `Themes/`.
