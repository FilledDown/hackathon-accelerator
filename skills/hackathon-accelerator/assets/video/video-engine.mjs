// Browser side of the demo-video pipeline. You normally don't run this directly: scripts/demo_video.py
// installs it into <project>/.hackathon/video-tools/ and calls it.
//
//   node video-engine.mjs record <shots.json> <out-dir>     → out-dir/demo.webm + out-dir/timeline.json
//   node video-engine.mjs cards  <cards.html> <out-dir>     → out-dir/<section id>.png (1920×1080)
//
// Browser: CHROME_PATH if set, else an installed Chrome or Edge, else Playwright's own Chromium
// (install it with: npx playwright-core install chromium).
import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const W = 1920, H = 1080;
const [mode, src, outDir] = process.argv.slice(2);
if (!mode || !src || !outDir) {
  console.error("usage: node video-engine.mjs record <shots.json> <out-dir> | cards <cards.html> <out-dir>");
  process.exit(2);
}
fs.mkdirSync(outDir, { recursive: true });

async function launch() {
  const tries = [];
  if (process.env.CHROME_PATH) tries.push({ executablePath: process.env.CHROME_PATH });
  tries.push({ channel: "chrome" }, { channel: "msedge" }, {});
  let last;
  for (const opts of tries) {
    try { return await chromium.launch({ ...opts, args: ["--hide-scrollbars", "--force-color-profile=srgb"] }); }
    catch (e) { last = e; }
  }
  console.error("No browser found. Install Chrome, or run: npx playwright-core install chromium\n" + (last?.message || ""));
  process.exit(3);
}

function toUrl(u, base) {
  if (/^https?:|^file:/.test(u)) return u;
  if (u.startsWith("/") && base && /^https?:/.test(base)) return new URL(u, base).href;
  const p = path.resolve(path.dirname(path.resolve(src)), u);
  if (fs.existsSync(p)) return pathToFileURL(p).href;
  return base ? new URL(u, base).href : u;
}

// ------------------------------------------------------------------ cards
if (mode === "cards") {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  await page.goto(pathToFileURL(path.resolve(src)).href, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const ids = await page.$$eval("section.card", els => els.map(e => e.id));
  for (const id of ids) {
    const transparent = await page.locator(`#${id}`).evaluate(e => e.classList.contains("overlay"));
    await page.locator(`#${id}`).screenshot({ path: path.join(outDir, `${id}.png`), omitBackground: transparent });
    console.log(`card ${id}.png`);
  }
  await browser.close();
  process.exit(0);
}

// ------------------------------------------------------------------ record
const spec = JSON.parse(fs.readFileSync(src, "utf8"));
const BASE = spec.url ? toUrl(spec.url) : undefined;
const accent = spec.brand?.accent || "#f97316";
const ZOOM = Math.min(2, Math.max(1, Number(spec.zoom ?? 1.25)));   // 1.25 = UI sized like a 1536-px laptop screen
const VW = Math.round(W / ZOOM), VH = Math.round(H / ZOOM);
const PAGE_CAPTIONS = !!spec.page_captions;                          // default: captions are added in the edit

function OVERLAY(accent) {
  if (window.__demoOverlay) return; window.__demoOverlay = true;
  const css = document.createElement("style");
  css.textContent = [
    "#__cur{position:fixed;left:0;top:0;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;z-index:2147483647;pointer-events:none;",
    "background:rgba(255,255,255,.92);border:2px solid rgba(0,0,0,.85);box-shadow:0 3px 12px rgba(0,0,0,.35);transition:scale .15s}",
    "#__cur.down{scale:.7}",
    ".__ripple{position:fixed;width:48px;height:48px;margin:-24px 0 0 -24px;border-radius:50%;border:3px solid " + accent + ";z-index:2147483646;pointer-events:none;animation:__rp .55s ease-out forwards}",
    "@keyframes __rp{from{transform:scale(.3);opacity:1}to{transform:scale(1.5);opacity:0}}",
    "#__cap{position:fixed;left:50%;bottom:64px;transform:translateX(-50%) translateY(14px);max-width:1500px;padding:18px 32px;border-radius:18px;z-index:2147483647;pointer-events:none;",
    "background:rgba(10,10,12,.88);color:#fff;font:600 34px/1.3 Inter,'Segoe UI',system-ui,sans-serif;letter-spacing:-.01em;opacity:0;transition:opacity .35s,transform .35s;",
    "box-shadow:0 20px 50px rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.12)}",
    "#__cap.on{opacity:1;transform:translateX(-50%)}",
    "#__cap b{color:" + accent + "}",
    "#__dim{position:fixed;inset:0;z-index:2147483640;pointer-events:none;opacity:0;transition:opacity .6s;",
    "background:radial-gradient(ellipse var(--rw,400px) var(--rh,260px) at var(--sx,50%) var(--sy,50%),transparent 60%,rgba(0,0,0,.6) 100%)}",
    "#__dim.on{opacity:1}",
  ].join("");
  const mount = () => {
    if (!document.body || !document.head) return requestAnimationFrame(mount);
    document.head.appendChild(css);
    for (const id of ["__dim", "__cap", "__cur"]) { const d = document.createElement("div"); d.id = id; document.body.appendChild(d); }
    const s = sessionStorage.getItem("__cap"); if (s) { const c = document.getElementById("__cap"); c.innerHTML = s; c.classList.add("on"); }
  };
  mount();
  addEventListener("mousemove", e => { const c = document.getElementById("__cur"); if (c) c.style.transform = "translate(" + e.clientX + "px," + e.clientY + "px)"; }, true);
  addEventListener("mousedown", e => { const c = document.getElementById("__cur"); if (c) c.classList.add("down");
    const r = document.createElement("div"); r.className = "__ripple"; r.style.left = e.clientX + "px"; r.style.top = e.clientY + "px";
    document.body.appendChild(r); setTimeout(() => r.remove(), 650); }, true);
  addEventListener("mouseup", () => { const c = document.getElementById("__cur"); if (c) c.classList.remove("down"); }, true);
}

// Frames are captured with the Chrome DevTools screencast and encoded by your system ffmpeg, so Playwright's
// own ffmpeg download (often blocked on school/work networks) is never needed.
const FFMPEG = process.env.FFMPEG || "ffmpeg";
const browser = await launch();
const raw = path.join(outDir, "_frames");
fs.rmSync(raw, { recursive: true, force: true });
fs.mkdirSync(raw, { recursive: true });
const context = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: ZOOM });
await context.addInitScript(OVERLAY, accent);
const page = await context.newPage();
page.setDefaultTimeout(spec.timeout_ms || 8000);
const frames = [];
const cdp = await context.newCDPSession(page);
cdp.on("Page.screencastFrame", async f => {
  const file = path.join(raw, `f${String(frames.length).padStart(6, "0")}.jpg`);
  fs.writeFileSync(file, Buffer.from(f.data, "base64"));
  frames.push({ file, ts: f.metadata.timestamp });
  cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
});
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, maxWidth: W, maxHeight: H, everyNthFrame: 1 });

let pos = { x: VW / 2, y: VH / 2 };
const ease = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
async function moveTo(x, y, ms = 650) {
  const from = { ...pos }, steps = Math.max(12, Math.round(ms / 16));
  for (let i = 1; i <= steps; i++) { const t = ease(i / steps); await page.mouse.move(from.x + (x - from.x) * t, from.y + (y - from.y) * t); }
  pos = { x, y };
}
async function box(sel) {
  const el = page.locator(sel).first();
  await el.waitFor({ state: "visible" });
  const inView = await el.evaluate(e => { const r = e.getBoundingClientRect(); return r.top >= 90 && r.bottom <= innerHeight - 190; });
  if (!inView) { await el.evaluate(e => e.scrollIntoView({ block: "center", behavior: "smooth" })); await page.waitForTimeout(750); }
  const b = await el.boundingBox();
  if (!b) throw new Error(`not visible: ${sel}`);
  return b;
}
const center = b => ({ x: b.x + b.width / 2, y: b.y + b.height / 2 });
async function caption(text) {
  if (!PAGE_CAPTIONS) return;
  const html = String(text || "").replace(/[<>&]/g, c => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c])).replace(/\*(.+?)\*/g, "<b>$1</b>");
  await page.evaluate(t => { sessionStorage.setItem("__cap", t); const c = document.getElementById("__cap"); if (!c) return;
    c.classList.remove("on"); setTimeout(() => { c.innerHTML = t; if (t) c.classList.add("on"); }, 200); }, html).catch(() => {});
}

let hero = null;
const actions = {
  goto: async u => { await page.goto(toUrl(u, BASE), { waitUntil: "load" }); await page.waitForTimeout(700); },
  click: async sel => { const c = center(await box(sel)); await moveTo(c.x, c.y); await page.waitForTimeout(120);
    await page.mouse.down(); await page.waitForTimeout(90); await page.mouse.up(); await page.waitForTimeout(400); },
  hover: async sel => { const c = center(await box(sel)); await moveTo(c.x, c.y); await page.waitForTimeout(900); },
  move: async sel => { const c = center(await box(sel)); await moveTo(c.x, c.y); },
  type: async ([sel, text, delay = 45]) => { const c = center(await box(sel)); await moveTo(c.x, c.y); await page.mouse.click(c.x, c.y);
    await page.keyboard.type(String(text), { delay }); },
  fill: async ([sel, text]) => { await page.locator(sel).first().fill(String(text)); },
  press: async key => { await page.keyboard.press(key); await page.waitForTimeout(300); },
  drag: async ([sel, dx, dy = 0]) => { const c = center(await box(sel)); await moveTo(c.x, c.y); await page.mouse.down();
    await moveTo(c.x + dx, c.y + dy, 1200); await page.mouse.up(); },
  scroll: async dy => { const steps = 24; for (let i = 0; i < steps; i++) { await page.mouse.wheel(0, dy / steps); await page.waitForTimeout(35); } await page.waitForTimeout(300); },
  wait: async ms => page.waitForTimeout(ms),
  waitFor: async sel => page.locator(sel).first().waitFor({ state: "visible", timeout: 30000 }),
  spotlight: async sel => { const b = await box(sel); hero = { x: b.x, y: b.y, w: b.width, h: b.height };
    await page.evaluate(([x, y, w, h]) => { const d = document.getElementById("__dim"); if (!d) return;
      d.style.setProperty("--sx", x + "px"); d.style.setProperty("--sy", y + "px");
      d.style.setProperty("--rw", w + "px"); d.style.setProperty("--rh", h + "px"); d.classList.add("on"); },
      [b.x + b.width / 2, b.y + b.height / 2, b.width * 1.6, b.height * 1.6]); },
  unspotlight: async () => page.evaluate(() => document.getElementById("__dim")?.classList.remove("on")),
};

const scaleBox = b => ({ x: b.x * ZOOM, y: b.y * ZOOM, w: b.w * ZOOM, h: b.h * ZOOM });
const t0 = Date.now();
const T0 = t0 / 1000;
const timeline = [];
let failed = null;
try {
  if (BASE) await actions.goto(BASE);
  for (const [i, shot] of (spec.shots || []).entries()) {
    const start = (Date.now() - t0) / 1000;
    hero = null;
    await caption(shot.caption);
    for (const a of shot.actions || []) {
      const [name, arg] = Object.entries(a)[0];
      if (!actions[name]) throw new Error(`unknown action "${name}" in shot ${i + 1}`);
      try { await actions[name](arg); }
      catch (e) { throw new Error(`shot ${i + 1}, ${name} ${JSON.stringify(arg)}: ${e.message.split("\n")[0]}`); }
    }
    await page.waitForTimeout(Math.round((shot.hold ?? 1.6) * 1000));
    const end = (Date.now() - t0) / 1000;
    timeline.push({ i, caption: shot.caption || "", start, end, hero: shot.hero ? scaleBox(hero || { x: pos.x - 240, y: pos.y - 135, w: 480, h: 270 }) : null });
    await actions.unspotlight();
    console.log(`shot ${i + 1}/${spec.shots.length} ${(end - start).toFixed(1)}s  ${shot.caption || ""}`);
  }
  await caption("");
  await page.waitForTimeout(500);
} catch (e) {
  failed = e.message;
  console.error(`FAILED: ${failed}`);
  console.error("Fix the selector in shots.json (prefer text=…, role=button[name=\"…\"], or [data-testid=…]).");
} finally {
  const endTs = Date.now() / 1000;
  await cdp.send("Page.stopScreencast").catch(() => {});
  await page.waitForTimeout(150);
  await context.close();
  await browser.close();
  if (frames.length) {
    // concat list with each frame's real duration → constant 30 fps H.264
    // align to t0 (the timeline's zero): drop frames before it, but keep the last one as the opening image
    let k = 0;
    while (k + 1 < frames.length && frames[k + 1].ts <= T0) k++;
    const use = frames.slice(k).map((fr, i) => ({ ...fr, ts: i === 0 ? Math.min(fr.ts, T0) : fr.ts }));
    const lines = [];
    if (use[0].ts > T0) lines.push(`file '${path.basename(use[0].file)}'`, `duration ${(use[0].ts - T0).toFixed(4)}`);
    use.forEach((fr, i) => {
      const t = i === 0 ? T0 : fr.ts;
      const next = i + 1 < use.length ? use[i + 1].ts : endTs;
      lines.push(`file '${path.basename(fr.file)}'`, `duration ${Math.max(0.001, next - t).toFixed(4)}`);
    });
    lines.push(`file '${path.basename(use[use.length - 1].file)}'`);
    fs.writeFileSync(path.join(raw, "list.txt"), lines.join("\n"));
    const final = path.resolve(outDir, "demo.mp4");
    const r = spawnSync(FFMPEG, ["-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-vf", `scale=${W}:${H},fps=30,format=yuv420p`,
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", final], { cwd: raw, encoding: "utf8" });
    if (r.status !== 0) { console.error("ffmpeg failed to encode the recording:\n" + (r.stderr || "").slice(-1200)); failed = failed || "encode failed"; }
    else fs.rmSync(raw, { recursive: true, force: true });
    fs.writeFileSync(path.join(outDir, "timeline.json"), JSON.stringify({ total: endTs - T0, frames: frames.length, failed, shots: timeline }, null, 2));
  } else {
    console.error("No frames were captured.");
    fs.writeFileSync(path.join(outDir, "timeline.json"), JSON.stringify({ failed: failed || "no frames captured", shots: timeline }, null, 2));
  }
  process.exit(failed ? 1 : 0);
}
