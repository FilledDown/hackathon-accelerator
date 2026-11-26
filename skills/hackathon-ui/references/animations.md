# Component Animations

Smooth, purposeful animation is one of the fastest ways to make a hackathon product feel finished. This file has a recipe for each component judges touch: **buttons, links, cards, images, text, tabs, toggles, inputs, feedback and backgrounds**. Each recipe has a CSS version (works everywhere), a React version (Motion) and, where useful, a vanilla JS version (anime.js).

`references/motion.md` covers the timing principles: curves, durations and the hero moment. This file is the component cookbook. Working examples of everything here are in `assets/showcase/motion-gallery.html`.

## Contents
1. Pick your stack
2. Ground rules
3. Buttons · 4. Links · 5. Cards · 6. Images · 7. Text · 8. Tabs, toggles, inputs · 9. Lists and page sections · 10. Feedback · 11. Backgrounds
12. Ready-made component libraries (React Bits, Kokonut UI)
13. Charts (ECharts)
14. Motion personality per style

---

## 1. Pick your stack

| Project | Use |
|---|---|
| React / Next.js + Tailwind | **CSS** for hovers and presses, **Motion** (`npm i motion`, `import { motion } from "motion/react"`) for entrances, layout and gestures, and copy-paste components from **React Bits** or **Kokonut UI** for signature effects |
| Vanilla HTML, Vue, Svelte, Astro | **CSS** first, plus **anime.js v4** (`npm i animejs`, `import { animate, stagger } from "animejs"`) for sequenced or scroll-driven motion |
| Any | **View Transitions API** (`document.startViewTransition`) for page and state changes, with no library |

Don't install three animation libraries. Pick one JS library per project. CSS covers most hover and press states.

Before you write code against these libraries, check the installed version's docs (Context7 or the official site). The snippets below match Motion 11+, anime.js v4 and ECharts 5/6.

## 2. Ground rules
- **Animate only `transform` and `opacity`** (plus `filter` and `clip-path` sparingly). Never animate `width`, `height`, `top` or `left` in a loop.
- **Fast feedback, slower entrances:** hover and press take 100–200ms, entrances 400–700ms, exits about 70% of the entrance.
- **One easing family per project:** `cubic-bezier(.16,1,.3,1)` (smooth ease-out) for nearly everything. Springs for drag and toggles.
- **Every animation has a job:** feedback, orientation (where something came from) or delight at one key moment. If it has no job, remove it.
- **Respect reduced motion.** CSS: `@media (prefers-reduced-motion: reduce)`. Motion: `useReducedMotion()` or `<MotionConfig reducedMotion="user">`.
- **Test on the demo laptop** with DevTools' FPS meter. Animation that janks during the live demo is worse than none.

```css
:root { --ease: cubic-bezier(.16,1,.3,1); --spring: cubic-bezier(.34,1.56,.64,1); --fast: 150ms; --med: 250ms; --slow: 600ms; }
```

---

## 3. Buttons

**Hover + press (every button):**
```css
.btn { transition: transform var(--fast) var(--ease), background-color var(--fast), box-shadow var(--med) var(--ease); }
.btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px -6px color-mix(in oklab, var(--accent) 60%, transparent); }
.btn:active { transform: translateY(0) scale(.97); transition-duration: 60ms; }
```
```jsx
<motion.button whileHover={{ y: -1 }} whileTap={{ scale: 0.97 }} transition={{ type: "spring", stiffness: 500, damping: 30 }} />
```

**Arrow nudge** (CTA with an icon): the arrow moves 3px right on hover.
```css
.btn .arrow { transition: transform var(--med) var(--ease); } .btn:hover .arrow { transform: translateX(3px); }
```

**Shine sweep** (primary CTA only, once per page):
```css
.btn-shine { position: relative; overflow: hidden; }
.btn-shine::after { content: ""; position: absolute; inset: 0; transform: translateX(-120%);
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.35) 50%, transparent 70%); }
.btn-shine:hover::after { transform: translateX(120%); transition: transform .8s var(--ease); }
```

**Loading → success** (the button that triggers your hero moment): fix the width, swap the label for a spinner, then a check that draws itself.
```jsx
const [state, setState] = useState("idle"); // idle | loading | done
<motion.button layout disabled={state === "loading"} onClick={run}>
  <AnimatePresence mode="wait" initial={false}>
    <motion.span key={state} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: .18 }}>
      {state === "idle" ? "Generate" : state === "loading" ? <Spinner/> : "✓ Done"}
    </motion.span>
  </AnimatePresence>
</motion.button>
```

**Magnetic button** (playful-builder and bold-media styles only): the button follows the cursor by up to 6px.
```js
btn.addEventListener("pointermove", e => { const r = btn.getBoundingClientRect();
  btn.style.transform = `translate(${(e.clientX - r.left - r.width/2) * .15}px, ${(e.clientY - r.top - r.height/2) * .25}px)`; });
btn.addEventListener("pointerleave", () => btn.style.transform = "");
```

## 4. Links

**Underline that draws from the left** (nav and inline links):
```css
.link { background: linear-gradient(currentColor, currentColor) 0 100% / 0 1px no-repeat; transition: background-size var(--med) var(--ease); }
.link:hover, .link:focus-visible { background-size: 100% 1px; }
```
**Sliding nav highlight:** a pill behind the hovered nav item that glides between items. Use Motion `layoutId="nav-pill"` on a `motion.span` rendered inside the hovered item.
```jsx
{links.map(l => <a key={l} onMouseEnter={() => setHover(l)} className="relative px-3 py-1.5">
  {hover === l && <motion.span layoutId="nav-pill" className="absolute inset-0 rounded-full bg-surface-2" transition={{ type: "spring", stiffness: 400, damping: 35 }} />}
  <span className="relative">{l}</span></a>)}
```
**Arrow links** ("Read the docs →"): same arrow nudge as buttons. Color shifts from `--text-2` to `--text`.

## 5. Cards

**Lift on hover** (no scale on large cards):
```css
.card { transition: transform var(--med) var(--ease), border-color var(--med), box-shadow var(--med) var(--ease); }
.card:hover { transform: translateY(-3px); border-color: var(--border-strong); box-shadow: var(--shadow-lg); }
```
**Spotlight that follows the cursor:** see `motion.md`. It works best on dark styles.

**Subtle 3D tilt** (feature or template cards, max 6°):
```js
card.addEventListener("pointermove", e => { const r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
  card.style.transform = `perspective(900px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg)`; });
card.addEventListener("pointerleave", () => card.style.transform = "");
```
(`card` needs `transition: transform .3s var(--ease)` so it settles smoothly.)

**Expand to detail** (card → modal or full view, the most "native app" feeling effect): Motion shared layout.
```jsx
<motion.div layoutId={`card-${id}`} onClick={() => setOpen(id)}>…</motion.div>
<AnimatePresence>{open && <motion.div layoutId={`card-${open}`} className="fixed inset-8 z-50">…</motion.div>}</AnimatePresence>
```

**Stagger in on scroll:**
```jsx
<motion.div initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-80px" }}
  transition={{ duration: .6, delay: i * 0.06, ease: [.16, 1, .3, 1] }} />
```
```js
// vanilla + anime.js v4
import { animate, stagger } from "animejs";
new IntersectionObserver((entries, io) => entries.forEach(en => { if (!en.isIntersecting) return;
  animate(en.target.querySelectorAll(".card"), { opacity: [0, 1], y: [12, 0], delay: stagger(60), duration: 600, ease: "outExpo" });
  io.unobserve(en.target); }), { rootMargin: "-80px" }).observe(document.querySelector(".cards"));
```

## 6. Images

**Blur-up on load** (no flash of empty boxes): show a tiny blurred placeholder or a solid dominant color, then fade in the real image.
```css
.img { opacity: 0; filter: blur(12px); transform: scale(1.02); transition: opacity .5s var(--ease), filter .6s var(--ease), transform .8s var(--ease); }
.img.loaded { opacity: 1; filter: none; transform: none; }
```
```html
<img class="img" src="hero.webp" alt="…" onload="this.classList.add('loaded')" width="1200" height="800">
```
Next.js: `<Image placeholder="blur" blurDataURL=…>` does this for you.

**Reveal mask** (editorial, hero images): the image wipes in.
```css
.reveal-img { clip-path: inset(0 0 100% 0); transition: clip-path 1s var(--ease); } .reveal-img.in { clip-path: inset(0 0 0 0); }
```
**Hover zoom inside its frame** (product and gallery cards): the frame stays still, the image scales 1.04.
```css
.frame { overflow: hidden; border-radius: var(--radius-lg); } .frame img { transition: transform .8s var(--ease); } .frame:hover img { transform: scale(1.04); }
```
**Slow Ken Burns** on a full-bleed hero photo: `animation: kb 20s ease-in-out infinite alternate` from `scale(1)` to `scale(1.06) translate(-1%, -1%)`.

**Gallery → lightbox:** Motion `layoutId` on the thumbnail and the enlarged image, plus a backdrop fade.

**Before/after slider** (great for AI image, design or cleanup products): two stacked images, the top one clipped with `clip-path: inset(0 calc(100% - var(--pos)) 0 0)`, and a draggable handle that updates `--pos`.

## 7. Text

- **Headline reveal:** split into words, each rising 12px plus a fade, 40–60ms stagger. React Bits **SplitText** / **BlurText** do this, or with anime.js: `animate(".word", { opacity: [0,1], y: ["0.4em", 0], delay: stagger(50), ease: "outExpo" })`.
- **Typing or streaming** for AI output: stream real tokens if you have them. Kokonut **Typing Text** or a 30–50ms per-character interval.
- **Number counter** for key metrics: 700ms ease-out with tabular numbers. anime.js: `animate(obj, { value: 1240, duration: 800, ease: "outExpo", onUpdate: () => el.textContent = Math.round(obj.value).toLocaleString() })`.
- **Shimmer or gradient text:** one word in the hero, never body text.
- **Rotating words** ("for **students** / **teachers** / **bands**"): swap with a vertical slide every 2.5s.

## 8. Tabs, toggles, inputs
- **Tab indicator that slides:** Motion `layoutId="tab-indicator"` under the active tab, or in CSS, animate the indicator's `translateX` and width with `--ease`.
- **Toggle:** the knob moves with a spring (`--spring`, 250ms), and the track color crossfades.
- **Input focus:** the border color and a 3px soft ring fade in over 150ms. The floating label moves up 8px and scales to .85.
- **Segmented control:** same sliding pill as the nav highlight.
- **Accordion:** animate `grid-template-rows: 0fr → 1fr` (CSS-only, smooth), or Motion `animate={{ height: "auto" }}`.

## 9. Lists and page sections
- **List add and remove:** Motion `AnimatePresence` + `layout` on items, so new items slide in and the others glide over. The one-line alternative is `@formkit/auto-animate`.
- **Section entrance:** fade + 12px rise on first view, once. No more than one entrance style per page.
- **Page and route transitions:** View Transitions API, `::view-transition-old(root)`/`-new(root)` crossfade 200ms, or Next.js App Router with Motion's `AnimatePresence` on a keyed wrapper.
- **Sticky scroll story** (landing pages): a pinned product frame whose content changes as the text on the side scrolls by. Use anime.js `onScroll` or an IntersectionObserver that swaps states.

## 10. Feedback
- **Toast:** slides in 16px from the edge with a fade, auto-dismisses, and stacks with `layout`.
- **Skeleton shimmer:** see `motion.md`. Skeleton shapes match the real content.
- **Success moment:** a check that draws itself (SVG `stroke-dashoffset` from the path length to 0 over 400ms), plus a gentle scale pop on the container. Save confetti (React Bits **ClickSpark** or canvas-confetti) for the one real milestone, like "your first song is ready".
- **Error shake:** 3 quick ±4px x-oscillations over 300ms on the field, plus a red border. Use it only for invalid submit.

## 11. Backgrounds
Animated backgrounds (aurora, gradient mesh, particles, grids) make a hero feel premium, but they're the easiest thing to overdo.
- One per page, behind the hero only, slow (20–40s loops), at low contrast.
- React Bits has ready ones (for example Aurora, Particles, Squares). Check the component page for its dependency (some use WebGL through `ogl`, some use GSAP).
- Pause when off-screen (IntersectionObserver), and show a static gradient under reduced motion.

---

## 12. Ready-made component libraries

Use these when the project is **React + Tailwind**. They're copy-paste components, so the code lands in your repo and you can restyle it with your tokens.

**React Bits** (reactbits.dev): text animations, animated components and backgrounds.
```bash
npx shadcn@latest add @react-bits/SplitText-TS-TW     # suffix: -JS-CSS | -JS-TW | -TS-CSS | -TS-TW
```
Browse the site for the component you want, open its Code tab to see its dependencies (often `motion` or `gsap`), and install with the pattern above.

**Kokonut UI** (kokonutui.com): polished buttons, cards, text effects and AI inputs. It needs shadcn/ui and Tailwind v4.
```bash
npx shadcn@latest init                                  # if the project has no components.json yet
npx shadcn@latest add https://kokonutui.com/r/utils.json
npx shadcn@latest add @kokonutui/particle-button        # requires the @kokonutui registry in components.json (see their docs)
```
Good picks for hackathon products: AI Input Search or AI Input Selector (AI products), Typing Text, Hold Button, Particle Button (one celebratory CTA), Now Playing (media apps).

**Rules for using component libraries:**
- Re-skin every component with your tokens (colors, radius, font). Unchanged library components look like everyone else's demo.
- Use one or two "signature" components, not ten. Everything else stays calm.
- Make sure each one respects reduced motion, and add a check if it doesn't.

## 13. Charts (ECharts)

Most hackathon products are not dashboards, but many have *one* data view: a progress chart, a usage graph, an impact number. **ECharts** (`npm i echarts`) animates beautifully by default and handles big data.
```js
import * as echarts from "echarts";
const chart = echarts.init(el, null, { renderer: "svg" });   // svg = crisp in screenshots
chart.setOption({
  animationDuration: 900, animationEasing: "cubicOut",
  textStyle: { fontFamily: getComputedStyle(document.body).getPropertyValue("--font-sans") },
  grid: { left: 40, right: 16, top: 24, bottom: 32 },
  xAxis: { type: "category", data: days, axisLine: { show: false }, axisTick: { show: false } },
  yAxis: { type: "value", splitLine: { lineStyle: { opacity: .08 } } },
  tooltip: { trigger: "axis" },
  series: [{ type: "line", data: values, smooth: true, showSymbol: false, lineStyle: { width: 2.5, color: accent },
    areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: accent + "33" }, { offset: 1, color: accent + "00" }]) } }]
});
addEventListener("resize", () => chart.resize());
```
Use the tree-shaken import (`echarts/core` + `echarts.use([...])` with a `CanvasRenderer` or `SVGRenderer`) to keep bundles small. In React, wrap it in a component that inits in `useEffect` and disposes on unmount. Pull colors from your tokens, so the chart matches the style.

## 14. Motion personality per style
| Style | Feel | Signature motion |
|---|---|---|
| precision-dark | instant, exact | spotlight cards, ⌘K palette pop, blur-rise entrances |
| fintech-gradient | slow, luxurious | gradient drift, floating cards settling, number tickers |
| calm-workspace | gentle | soft fades, tab crossfades, moving "multiplayer" cursors |
| dev-platform | technical | typing code, streaming logs, packets along diagram lines |
| editorial-luxe | slow, deliberate | line-by-line headline rise, image reveal masks, underline draws |
| spec-sheet | mechanical | stepped easing, click-into-place, hanging-card swing |
| bold-media | kinetic | typed accent line, marquee, card tilt, waveform motion |
| playful-builder | springy | magnetic buttons, springs, floating cursors, sticker pops |
| data-dashboard | functional | chart morphs between ranges, number ticks, row highlights |
