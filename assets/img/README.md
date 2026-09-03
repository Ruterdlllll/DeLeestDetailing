# Website photos — what lives where

Every photo on the website is a local file in this folder. To replace a photo:
**save your new photo over the existing file, keeping the exact same filename**
(e.g. replace `pc-ipad/gallery/result-03/01.jpg` with your own `01.jpg`). No
code changes needed — the site picks it up automatically.

## Two versions of every photo: PC/iPad and mobile

Photos come in **two device categories**, so you can choose which photo is
shown on which device:

| Folder | Shown on |
| --- | --- |
| `pc-ipad/` | Desktop computers, laptops **and iPads / tablets** |
| `mobile/` | **Phones** (screens narrower than 768px) |

Both folders contain exactly the same files in the same structure. The website
automatically serves the `mobile/` version on phones and the `pc-ipad/`
version on anything larger — including the popup (lightbox) photos.

**Want the same photo everywhere?** Then you don't need to do anything extra:
right now both folders contain identical copies, so every photo already looks
the same on all devices. Only replace a file in `mobile/` when you want a
different photo on phones (e.g. a portrait/cropped version).

Tips for best results:

- Use `.jpg` files. Landscape (wider than tall) for `pc-ipad/`; for
  `mobile/` a portrait or more tightly cropped photo often works better.
- Minimum width: ~2000px for the hero, ~1600px for everything else.
- Keep file sizes reasonable (under ~500 KB per photo is plenty).

## Where each photo appears

The table below shows the path inside each category folder — so
`hero/hero.jpg` means both `pc-ipad/hero/hero.jpg` and `mobile/hero/hero.jpg`.

| File | Where on the website |
| --- | --- |
| `hero/hero.jpg` | Homepage — large banner at the very top, behind the headline |
| `services/car.jpg` | Homepage — "Our services" → photo next to the **car** services |
| `services/motorcycle.jpg` | Homepage — "Our services" → photo next to the **motorcycle** services |
| `about/about.jpg` | Homepage — "Our standard" section, photo beside the text |
| `gallery/result-01/` | Homepage — "Recent work" gallery, tile 1 (top-left) |
| `gallery/result-02/` | Gallery tile 2 |
| `gallery/result-03/` | Gallery tile 3 |
| `gallery/result-04/` | Gallery tile 4 |
| `gallery/result-05/` | Gallery tile 5 |
| `gallery/result-06/` | Gallery tile 6 |
| `gallery/result-07/` | Gallery tile 7 |
| `gallery/result-08/` | Gallery tile 8 (bottom-right) |

Tiles are numbered left to right, top to bottom (on desktop: 4 tiles per row).
`hero/hero2.jpg` is a spare hero photo that is currently not shown anywhere.

## Gallery tiles (`result-01` … `result-08`)

Each tile has its own folder with exactly 3 photos:

- `01.jpg` — the photo shown in the gallery grid **and** the first photo in the
  popup (lightbox) when a visitor clicks the tile.
- `02.jpg`, `03.jpg` — extra photos visitors can swipe/click through in the
  popup.

To change a tile: replace the files in its folder. Keep the names
`01.jpg`, `02.jpg`, `03.jpg`. Want fewer than 3 photos in a popup, more tiles,
or new photos of recent work? That's a small code change — ask your developer
(or the AI assistant) to add it.
