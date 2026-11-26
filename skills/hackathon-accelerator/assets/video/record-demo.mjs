// Records a polished demo of your running app: real clicks, a visible cursor, captions, and a spotlight on the hero moment.
//
// Setup (once, in your project):   npm i -D playwright   &&   npx playwright install chromium
// Run:                              node video/record-demo.mjs            (app must be running, e.g. npm run dev)
// Options (env):                    DEMO_URL=http://localhost:3000  OUT=video/raw  CHROME_PATH=<use an installed Chrome>
//
// Edit STEPS below to follow submission/DEMO_SCRIPT.md. Each step: a caption (what the viewer should notice),
// an async run(page, h) using the helpers, and how long to hold afterwards. Keep captions under ~70 characters.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const URL = process.env.DEMO_URL || "http://localhost:3000";
const OUT = process.env.OUT || "video/raw";
const W = 1920, H = 1080;

const STEPS = [
  { caption: "Maya has three pieces to learn and 30 minutes a day.", hold: 1800, run: async (page, h) => {
      await h.goto(URL);
  }},
  { caption: "She adds her repertoire…", hold: 1200, run: async (page, h) => {
      await h.click("text=Add piece");                       // ← replace with your real selectors
      await h.type("input[name=title]", "Chopin · Nocturne Op. 9 No. 2");
      await h.press("Enter");
  }},
  { caption: "…and Cadence plans her week in one click.", hold: 2200, run: async (page, h) => {
      await h.click("text=Plan my week");
  }},
  { caption: "★ She records a run-through. The rushed bars light up.", hold: 3500, run: async (page, h) => {
      await h.click("text=Record");
      await h.spotlight(".result");                          // dims everything except the hero moment
  }},
];

// ---------------------------------------------------------------- helpers (no need to edit below)
function OVERLAY() {   // runs inside the page before your app's scripts (passed to addInitScript as a function)
  if (window.__demoOverlay) return; window.__demoOverlay = true;
  const css = document.createElement("style");
  css.textContent = [
    "#__cur{position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;z-index:2147483647;pointer-events:none;",
    "background:rgba(255,255,255,.9);border:2px solid rgba(0,0,0,.85);box-shadow:0 2px 10px rgba(0,0,0,.35);transition:scale .15s}",
    "#__cur.down{scale:.7}",
    ".__ripple{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:2px solid rgba(124,131,245,.9);z-index:2147483646;pointer-events:none;animation:__rp .5s ease-out forwards}",
    "@keyframes __rp{from{transform:scale(.3);opacity:1}to{transform:scale(1.4);opacity:0}}",
    "#__cap{position:fixed;left:50%;bottom:56px;transform:translateX(-50%) translateY(10px);max-width:1400px;padding:16px 28px;border-radius:16px;z-index:2147483647;pointer-events:none;",
    "background:rgba(12,12,14,.86);color:#fff;font:600 30px/1.3 Inter,system-ui,sans-serif;letter-spacing:-.01em;opacity:0;transition:opacity .35s,transform .35s;backdrop-filter:blur(8px)}",
    "#__cap.on{opacity:1;transform:translateX(-50%)}",
    "#__dim{position:fixed;inset:0;z-index:2147483640;pointer-events:none;opacity:0;transition:opacity .6s;",
    "background:radial-gradient(ellipse var(--rw,400px) var(--rh,260px) at var(--sx,50%) var(--sy,50%),transparent 60%,rgba(0,0,0,.62) 100%)}",
    "#__dim.on{opacity:1}",
  ].join("");
  const mount = () => {
    if (!document.body || !document.head) return requestAnimationFrame(mount);
    document.head.appendChild(css);
    for (const id of ["__dim", "__cap", "__cur"]) { const d = document.createElement("div"); d.id = id; document.body.appendChild(d); }
  };
  mount();
  addEventListener("mousemove", e => { const c = document.getElementById("__cur"); if (c) c.style.transform = "translate(" + e.clientX + "px," + e.clientY + "px)"; }, true);
  addEventListener("mousedown", e => { const c = document.getElementById("__cur"); if (c) c.classList.add("down");
    const r = document.createElement("div"); r.className = "__ripple"; r.style.left = e.clientX + "px"; r.style.top = e.clientY + "px";
    document.body.appendChild(r); setTimeout(() => r.remove(), 600); }, true);
  addEventListener("mouseup", () => { const c = document.getElementById("__cur"); if (c) c.classList.remove("down"); }, true);
}

function helpers(page) {
  let pos = { x: W / 2, y: H / 2 };
  const ease = t => 1 - Math.pow(1 - t, 3);
  async function moveTo(x, y, ms = 650) {
    const from = { ...pos }, steps = Math.max(12, Math.round(ms / 16));
    for (let i = 1; i <= steps; i++) { const t = ease(i / steps);
      await page.mouse.move(from.x + (x - from.x) * t, from.y + (y - from.y) * t); }
    await page.evaluate(([cx, cy]) => { const c = document.getElementById("__cur"); if (c) c.style.transform = `translate(${cx}px,${cy}px)`; }, [x, y]);
    pos = { x, y };
  }
  async function centerOf(sel) {
    const el = page.locator(sel).first();
    const inView = await el.evaluate(e => { const r = e.getBoundingClientRect(); return r.top >= 80 && r.bottom <= innerHeight - 160; });
    if (!inView) { await el.evaluate(e => e.scrollIntoView({ block: "center", behavior: "smooth" })); await page.waitForTimeout(700); }
    const b = await el.boundingBox();
    if (!b) throw new Error(`Not visible: ${sel}`); return { x: b.x + b.width / 2, y: b.y + b.height / 2, b };
  }
  return {
    goto: async url => { await page.goto(url, { waitUntil: "networkidle" }); await page.waitForTimeout(600); },
    move: async sel => { const c = await centerOf(sel); await moveTo(c.x, c.y); },
    hover: async (sel, ms = 900) => { const c = await centerOf(sel); await moveTo(c.x, c.y); await page.waitForTimeout(ms); },
    click: async sel => { const c = await centerOf(sel); await moveTo(c.x, c.y); await page.waitForTimeout(120);
      await page.mouse.down(); await page.waitForTimeout(90); await page.mouse.up(); await page.waitForTimeout(350); },
    type: async (sel, text, delay = 45) => { const c = await centerOf(sel); await moveTo(c.x, c.y); await page.mouse.click(c.x, c.y);
      await page.keyboard.type(text, { delay }); },
    press: key => page.keyboard.press(key),
    drag: async (sel, dx, dy = 0, ms = 1200) => { const c = await centerOf(sel); await moveTo(c.x, c.y); await page.mouse.down();
      await moveTo(c.x + dx, c.y + dy, ms); await page.mouse.up(); },
    scroll: async (dy, ms = 900) => { const steps = 20; for (let i = 0; i < steps; i++) { await page.mouse.wheel(0, dy / steps); await page.waitForTimeout(ms / steps); } },
    wait: ms => page.waitForTimeout(ms),
    caption: async text => page.evaluate(t => { const c = document.getElementById("__cap"); if (!c) return;
      c.classList.remove("on"); setTimeout(() => { c.textContent = t; if (t) c.classList.add("on"); }, 180); }, text),
    spotlight: async (sel, pad = 1.6) => { const { b } = await centerOf(sel);
      await page.evaluate(([x, y, w, h]) => { const d = document.getElementById("__dim"); if (!d) return;
        d.style.setProperty("--sx", x + "px"); d.style.setProperty("--sy", y + "px");
        d.style.setProperty("--rw", w + "px"); d.style.setProperty("--rh", h + "px"); d.classList.add("on"); },
        [b.x + b.width / 2, b.y + b.height / 2, b.width * pad, b.height * pad]); },
    unspotlight: async () => page.evaluate(() => document.getElementById("__dim")?.classList.remove("on")),
  };
}

const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
fs.mkdirSync(OUT, { recursive: true });
const context = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, recordVideo: { dir: OUT, size: { width: W, height: H } } });
await context.addInitScript(OVERLAY);
const page = await context.newPage();
const h = helpers(page);
const t0 = Date.now(), srt = [];
const stamp = ms => { const d = new Date(ms); return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}:${String(d.getUTCSeconds()).padStart(2, "0")},${String(d.getUTCMilliseconds()).padStart(3, "0")}`; };
try {
  for (const [i, step] of STEPS.entries()) {
    const start = Date.now() - t0;
    if (i > 0) await h.caption(step.caption);
    await step.run(page, h);
    if (i === 0) await h.caption(step.caption);
    await h.wait(step.hold ?? 1500);
    await h.unspotlight();
    srt.push(`${i + 1}\n${stamp(start)} --> ${stamp(Date.now() - t0)}\n${step.caption}\n`);
    console.log(`✓ step ${i + 1}/${STEPS.length}: ${step.caption}`);
  }
  await h.caption("");
  await h.wait(800);
} catch (e) {
  console.error(`✗ Step failed: ${e.message}\nFix the selector in STEPS (tip: use text=…, role or data-testid selectors).`);
  process.exitCode = 1;
} finally {
  const video = page.video();
  await context.close();               // finalizes the recording
  await browser.close();
  if (video) {
    const final = path.join(OUT, "demo.webm");
    fs.renameSync(await video.path(), final);
    fs.writeFileSync(path.join(OUT, "demo.srt"), srt.join("\n"));
    console.log(`Saved ${final} (${Math.round((Date.now() - t0) / 1000)}s) and ${path.join(OUT, "demo.srt")} (captions, already burned in)`);
  }
}
