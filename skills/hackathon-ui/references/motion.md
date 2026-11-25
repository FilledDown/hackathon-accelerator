# Motion

Good motion is fast, purposeful and mostly unnoticed. Premium sites move less than you think: Linear, Stripe and Vercel animate entrances once, give instant feedback, and save the theatrics for one moment.

## Curves and durations
| Token | Value | Use |
|---|---|---|
| `--ease-out` | `cubic-bezier(.16, 1, .3, 1)` | Entrances, expanding, almost everything |
| `--ease-in-out` | `cubic-bezier(.65, 0, .35, 1)` | Moving between two positions (tabs, drawers) |
| `--ease-spring` (Framer Motion) | `{ type: "spring", stiffness: 400, damping: 30 }` | Drag, toggles, playful styles |
| `--dur-fast` | 100–150ms | Hover, press, color changes |
| `--dur` | 180–250ms | Dropdowns, tooltips, small panels |
| `--dur-slow` | 300–500ms | Modals, page sections entering |
| Hero reveal | 600–1200ms total | The one big moment, staggered |

Exits are faster than entrances, at about 70% of the entrance duration. Never use `linear` easing for UI movement. It's only for spinners and marquees.

## Patterns worth stealing

**Entrance stagger** (hero and section reveal, once per page load):
```css
.reveal { opacity: 0; transform: translateY(8px); filter: blur(4px);
  animation: reveal .7s var(--ease-out) forwards; animation-delay: calc(var(--i, 0) * 70ms); }
@keyframes reveal { to { opacity: 1; transform: none; filter: none; } }
```
Set `style="--i:1"`, `--i:2`… on children. Use an 8–12px offset. Bigger offsets look dated.

**Press feedback** (every button): `:active { transform: scale(.98); }` with a 100ms transition.

**Hover lift for cards** (subtle): `translateY(-2px)` plus a stronger border or shadow over 150ms. No scale-up on large cards.

**Spotlight border** (Linear/Vercel-style card highlight that follows the cursor):
```css
.card { background: radial-gradient(400px circle at var(--mx) var(--my), color-mix(in oklab, var(--accent) 18%, transparent), transparent 40%), var(--surface); }
```
```js
card.addEventListener("pointermove", e => { const r = card.getBoundingClientRect();
  card.style.setProperty("--mx", `${e.clientX - r.left}px`); card.style.setProperty("--my", `${e.clientY - r.top}px`); });
```

**Number ticker** for metrics that matter: count up over 600–900ms with ease-out, using tabular numbers.

**Typing or streaming text** for AI output (Musicwave hero, any LLM feature). Stream real tokens if you have them. It also turns waiting into a feature.

**Logo or partner marquee**: a CSS `@keyframes` translateX loop at 30–60s linear, paused on hover, with a mask fade at both edges: `mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent)`.

**Skeleton shimmer**: a gradient sweep over 1.2–1.6s. Match the skeleton shapes to the real layout.

**Command palette** (⌘K): open with a 150ms scale from .98 plus fade, backdrop blur, instant filtering, and arrow-key focus that moves without animation.

**Layout transitions**: Framer Motion `layout` prop or the View Transitions API (`document.startViewTransition`) for list reordering and tab content.

## The hero moment (the thing judges remember)
1. **Build-up:** show the "before" state (the problem) for a beat.
2. **Trigger:** one obvious action (a button, a drop zone, a prompt).
3. **Visible work:** progress steps, streaming output, intermediate results. Never a spinner alone.
4. **Reveal:** the result arrives with a stagger and a confident final state. Optionally add a subtle celebration, like a check that draws in, but never confetti for routine actions.

## Accessibility
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important;
    transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
```
Never flash more than 3 times per second, and never autoplay big motion behind body text.

## Libraries (only if the project already uses React)
- **Framer Motion / Motion**: entrances, layout, gestures.
- **Auto-animate**: one-line list animations.
- **Lottie / Rive**: designed animations (Rive for interactive state machines).
- **GSAP + ScrollTrigger**: scroll-driven storytelling (immersive style only).
- **Three.js / React Three Fiber / Spline embeds**: 3D (immersive style only, with a static fallback).
