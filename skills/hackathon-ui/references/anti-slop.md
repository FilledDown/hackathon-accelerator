# Anti-Slop Checklist

"AI slop" UI is recognizable because it repeats the same defaults. Judges and developers have seen thousands of them. Each item below lists the tell, why it reads as generic, and the fix. `scripts/ui_audit.py` checks the ones a script can catch. The rest need eyes on a screenshot.

## The tells

| # | Tell | Fix |
|---|---|---|
| 1 | **Purple-to-blue gradient** on a white hero (`from-purple-500 to-blue-500`, `from-indigo-500 via-purple-500 to-pink-500`) | One brand accent from your style file. If you use a gradient, make it a subtle glow or mesh in your accent family. |
| 2 | **Centered everything**: centered headline, centered paragraph, centered button, centered cards | Use a strong left axis for most sections. Center only a short poster hero. |
| 3 | **Three identical feature cards** with an icon in a colored circle, a title and two lines | A bento grid with different spans and *real UI fragments* inside each tile (a mini chart, a notification, a code snippet). |
| 4 | **Generic copy**: "Revolutionize your workflow", "Unlock the power of AI", "Seamless", "Elevate", "Welcome to X" | Say what it does for whom, with a number or a concrete noun. "Postmortems drafted in 40 seconds from your incident timeline." |
| 5 | **Inter at default tracking for a huge headline** | Negative tracking (-0.035em and beyond) at display sizes, or a display face from the style file. |
| 6 | **Emoji as icons** in headings, nav, buttons or feature lists | One icon set (Lucide or Phosphor) at a consistent stroke. |
| 7 | **Glassmorphism everywhere**: blurred translucent cards over a gradient blob | Solid surfaces with hairline borders. Use blur only for overlays like a sticky nav or a command palette. |
| 8 | **`rounded-2xl` + `shadow-xl` on every element** | One radius personality. Layered soft shadows, used sparingly. Borders do most of the work. |
| 9 | **Placeholder data**: Lorem ipsum, John Doe, "Item 1", $1,234, 99.9% everywhere | Realistic, domain-specific seeded data with believable variance. |
| 10 | **Random spacing**: 13px here, 22px there | 4/8px scale tokens only. |
| 11 | **Five accent colors**, rainbow badges | One accent, muted semantics. |
| 12 | **Default component library look** (unstyled shadcn/MUI/Bootstrap left as-is) | Keep the library for behavior, and re-skin it with your tokens (radius, colors, fonts, borders). |
| 13 | **Hero with a stock illustration** of people and laptops, or a floating 3D blob | The real product UI in a framed window. |
| 14 | **No states**: blank screen while loading, nothing for empty lists, raw errors | Skeletons, an empty state with an action, human error messages. |
| 15 | **Every element animates** (bounce, spin, fade on everything) | Motion only for feedback, entrances (once) and the hero moment. |
| 16 | **Low-contrast gray text** on gray, or pure white on pure black | Follow the contrast rules in `foundations.md`. |
| 17 | **A dashboard that's a grid of identical stat cards** with sparkline clip art | A clear primary metric, a real chart with labeled axes, and a table you can act on. |
| 18 | **Fake social proof**: "Trusted by 10,000+ teams" with made-up logos | Leave it out, or show real numbers you can defend (hackathon judges know you launched today). |
| 19 | **Inconsistent icon sizes and stroke widths** | Use one size per context (16/20) and one stroke weight. |
| 20 | **Mobile ignored**: horizontal scroll, tiny tap targets | Test at 390px. Tap targets ≥ 44px, and the nav collapses. |

## Pre-show checklist (run before any demo or screenshot)

- [ ] Squint test: is it obvious what matters most on each screen?
- [ ] Every color, radius, shadow and font comes from tokens (`ui_audit.py` reports hardcoded values)
- [ ] At most 6 font sizes per page, 2 families plus mono
- [ ] Headline tracking is tight, label tracking is wide
- [ ] Real data on every screen of the demo path
- [ ] Loading, empty and error states exist on the demo path
- [ ] Focus rings are visible (Tab through the page)
- [ ] Contrast passes (text ≥ 4.5:1)
- [ ] Looks right at 390px wide
- [ ] Hover, press and selection feedback on everything clickable
- [ ] No console errors, no layout shift when data loads
- [ ] The hero moment is visible within 10 seconds of opening the app
- [ ] Screenshot reviewed at 1440 and 390 widths
