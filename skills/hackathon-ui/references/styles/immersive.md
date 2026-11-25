# immersive

**Inspired by:** Lusion, Immersive Garden, Spline, Rive, Awwwards Sites of the Day
**Feels:** cinematic, surprising, crafted, emotional. An experience, not a page.
**Demo page:** none. A static page can't show this honestly. Study the reference sites with a browser tool instead.

## Hackathon warning (read first)
This is the riskiest direction. Pick it only if **all** of these are true:
- 36+ hours left, and 3D or scroll storytelling *is* the product or the core of its value.
- Someone on the team has shipped Three.js, R3F, Spline or GSAP before.
- You build a static fallback first (a poster image with the same layout), so the demo never shows a blank canvas.
- You test on the actual demo laptop and projector. WebGL plus a projector plus venue Wi-Fi is a classic failure point.

Otherwise, borrow **one** immersive element (a Spline embed in the hero, a Rive animation, a scroll-pinned section) and use another style for everything else.

## What makes it work (reverse-engineered)
- **A single 3D or generative scene** carries the hero: soft materials, studio lighting, objects reacting to the cursor or scroll.
- **Scroll is the timeline.** Sections pin while the scene changes. Text arrives in lines, synced to camera moves.
- **Minimal UI chrome:** small nav, big type, a custom cursor, a sound toggle, a preloader with a percentage.
- Dark or rich single-color backgrounds that make lighting read well.

## Tokens
```css
:root {
  --font-sans: "Inter Variable", system-ui, sans-serif;
  --font-display: "Inter Tight Variable", sans-serif;   /* or a single expressive display face */
  --bg: #0b0b0d; --text: #f2f2f0; --text-2: rgba(242,242,240,.65);
  --accent: #c8ff3d;
  --ease-cinematic: cubic-bezier(.77, 0, .175, 1);
}
```

## Building blocks
- **Spline**: design the scene visually and embed it (`@splinetool/react-spline` or the viewer web component). It's the fastest way to good 3D. Export a static image fallback.
- **React Three Fiber + drei**: when the scene must react to app data. Use `<Environment>`, `<Float>`, `<MeshTransmissionMaterial>` sparingly, and cap the device pixel ratio at 1.5.
- **GSAP ScrollTrigger** or **Lenis** for smooth scroll and pinning.
- **Rive** for interactive 2D animations driven by state machines (mascots, buttons, onboarding).

## Performance rules
- Lazy-load the scene after the first paint. Show the poster image immediately.
- Keep the total 3D payload under ~5 MB, compress textures (KTX2) and meshes (Draco/Meshopt).
- Pause rendering when off-screen (`frameloop="demand"`). Hold 60fps on the demo machine.
- Respect `prefers-reduced-motion`: show the static poster and plain scroll.

## Don'ts
- Never hide essential information inside the 3D scene. Text stays in the DOM, readable and accessible.
- No scroll-jacking on app screens. Immersive belongs to the landing or story page only.
- Don't start it at hour 30.

## Starter prompt
> Add one immersive hero element to [product]: a [Spline scene / R3F scene / Rive animation] of [object] that reacts to cursor movement, on a `#0b0b0d` background with big Inter Tight type over it. Lazy-load it after first paint, show a static poster immediately, cap DPR at 1.5, pause when off-screen, and use the poster under prefers-reduced-motion. Everything else stays in the [other style] direction.
