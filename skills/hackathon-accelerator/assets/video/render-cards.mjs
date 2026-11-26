// Renders every <section class="card" id="..."> in video/cards.html to video/cards/<id>.png at 1920×1080.
// Run: node video/render-cards.mjs    (needs: npm i -D playwright && npx playwright install chromium; or set CHROME_PATH)
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SRC = process.argv[2] || "video/cards.html";
const OUT = process.argv[3] || "video/cards";
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.resolve(SRC)).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const ids = await page.$$eval("section.card", els => els.map(e => e.id));
for (const id of ids) {
  await page.locator(`#${id}`).screenshot({ path: path.join(OUT, `${id}.png`) });
  console.log(`✓ ${path.join(OUT, id + ".png")}`);
}
await browser.close();
