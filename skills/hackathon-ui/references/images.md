# Images

The best hero image for a hackathon product is usually **the product's own UI**. Photos help when the product is about the physical world (food, places, music, fashion, sports, health, climate) or when a landing page needs mood. This file covers when to use photos, where to get them legally, and how to make them look consistent and load fast.

## Contents
1. When to use photos (and when not)
2. Getting images: `scripts/fetch_images.py`
3. Art direction: make them look like one set
4. Technical: size, format, loading
5. Alternatives to photos
6. Rules

## 1. When to use photos
| Use photos for | Use something else for |
|---|---|
| Landing page hero mood (one striking image) | Explaining the product: use the real UI |
| Product content: recipes, places, listings, outfits, events | Icons and features: use one icon set (Lucide or Phosphor) |
| Empty states with personality (one illustration-like photo) | Avatars in a demo: use initials or generated gradients |
| Social proof, only with real people who agreed to it | Abstract concepts like "AI" or "growth": skip the stock photo |

## 2. Getting images
```bash
python3 <ui-dir>/scripts/fetch_images.py "rainy city street at night" --count 4 --orientation landscape --out public/images
```
(Use `python` on Windows.)

| Provider | Key needed | What you get | Credit |
|---|---|---|---|
| `openverse` (default) | No | Creative Commons and public domain photos from Flickr, Wikimedia and others. Commercial-use licenses only, unless you pass `--allow-noncommercial` | Usually required. The script writes it |
| `pexels` | Free key in `PEXELS_API_KEY` | High-quality stock photos | Appreciated ("Photo by X on Pexels") |
| `unsplash` | Free key in `UNSPLASH_ACCESS_KEY` | High-quality editorial-style photos | Required by the API guidelines |

The script saves the files, an `images.json` manifest and a `CREDITS.md`. Keep `CREDITS.md` in the repo and link it from the README or the app footer, which also counts in your favor with judges.

**Search tips:** describe the *scene and mood*, not the concept ("hands on piano keys warm light", not "music learning"). Use `--dry-run` to preview the matches first. Fetch 2–3× more than you need, then pick the set that looks most consistent.

If the network blocks the script, download images by hand from those same sites and add each one to `CREDITS.md`, with the creator, license and source link.

## 3. Art direction: make them look like one set
Random stock photos side by side look cheap. Make them consistent:
- **Same light and palette:** pick images with a similar color temperature, or unify them with a CSS treatment.
  ```css
  .photo-duotone { filter: grayscale(1) contrast(1.1); mix-blend-mode: multiply; }   /* place on an accent-colored background */
  .photo-warm   { filter: saturate(.9) sepia(.12) contrast(1.05); }
  .photo-dim    { filter: brightness(.75) saturate(.9); }                          /* under hero text */
  ```
- **Same aspect ratio per context:** cards 4:5 or 3:2, heroes 16:9 or full-bleed. Use `aspect-ratio` plus `object-fit: cover`, and set `object-position` to keep the subject in frame.
- **Overlay for text legibility:** `linear-gradient(180deg, transparent 40%, rgba(0,0,0,.65))` under any text on a photo. Contrast must still pass.
- **Crop with intent:** tighter crops feel more editorial. Leave negative space where text will sit.
- **Match the style direction:** editorial-luxe takes one big art-directed photo, bold-media takes a dark, tinted, cinematic photo, calm-workspace takes soft, bright, small photos.

## 4. Technical
- **Resize before shipping:** heroes ~1920px wide, cards ~800px. Convert to WebP or AVIF (Next.js `<Image>`, `sharp`, or squoosh.app).
- **Always set `width` and `height`** (or `aspect-ratio`) to avoid layout shift.
- **Responsive:** `srcset` plus `sizes`, or the framework image component.
- **Lazy-load** everything below the fold (`loading="lazy"`). Never lazy-load the hero (`fetchpriority="high"` there).
- **Blur-up placeholders:** see `animations.md` §6. Next.js has `placeholder="blur"`.
- **Alt text:** describe what's in the image for real content. Use `alt=""` for purely decorative images.

## 5. Alternatives to photos
- **The product UI** in a framed window (see `components.md`, Product frame).
- **Generated art in code:** CSS gradients, SVG blobs, noise, grids and patterns (see the showcase pages: cover art in bold-media, ceramics in editorial-luxe).
- **AI image generation:** only if an image-generation MCP or tool is actually installed (check `PROGRESS.md` → Environment). Generate in one consistent style, and note it as AI-generated in `CREDITS.md`.
- **Illustrations:** only from free-licensed sets with the license checked, and kept to one set.

## 6. Rules
- Never download photos of a **specific real person** (celebrities, public figures, other students), logos, or trademarked products to use in the project.
- Never remove watermarks or use images from Google Images without a license.
- Keep `CREDITS.md` up to date. A missing attribution is an easy rules-audit failure.
- Don't put sensitive stereotypes in stock photos (for example, all "doctors" are men). Choose diverse, realistic images.
