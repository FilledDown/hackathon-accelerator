// Dev tool: `npm install` here, then `npm run render`. Set CHROME_PATH to use an installed Chrome.
// Renders showcase HTML pages to PNG with local fonts substituted for Google Fonts.
// usage: node render.js <out-dir> <file.html> [more.html...]   (env W,H for viewport; FULL=1 for full page)
const { chromium } = require("playwright-core");
const fs = require("fs"), path = require("path");

const FONTS = {  // Google family name -> fontsource woff2 (variable where available)
  "Inter": "@fontsource-variable/inter/files/inter-latin-wght-normal.woff2",
  "Inter Tight": "@fontsource-variable/inter-tight/files/inter-tight-latin-wght-normal.woff2",
  "Geist": "@fontsource-variable/geist/files/geist-latin-wght-normal.woff2",
  "Geist Mono": "@fontsource-variable/geist-mono/files/geist-mono-latin-wght-normal.woff2",
  "JetBrains Mono": "@fontsource-variable/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2",
  "Instrument Serif": "@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2",
  "Instrument Serif|italic": "@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2",
  "Newsreader": "@fontsource-variable/newsreader/files/newsreader-latin-wght-normal.woff2",
  "Newsreader|italic": "@fontsource-variable/newsreader/files/newsreader-latin-wght-italic.woff2",
  "Fraunces": "@fontsource-variable/fraunces/files/fraunces-latin-wght-normal.woff2",
  "Unbounded": "@fontsource-variable/unbounded/files/unbounded-latin-wght-normal.woff2",
  "Space Grotesk": "@fontsource-variable/space-grotesk/files/space-grotesk-latin-wght-normal.woff2",
  "Space Mono": "@fontsource/space-mono/files/space-mono-latin-400-normal.woff2",
  "Manrope": "@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2",
  "DM Sans": "@fontsource-variable/dm-sans/files/dm-sans-latin-wght-normal.woff2",
  "Archivo": "@fontsource-variable/archivo/files/archivo-latin-wght-normal.woff2",
};
const css = Object.entries(FONTS).map(([k, f]) => {
  const [fam, style] = k.split("|");
  return `@font-face{font-family:"${fam}";font-style:${style || "normal"};font-weight:100 900;font-display:block;src:url(https://fonts.local/${f}) format("woff2");}`;
}).join("\n");

(async () => {
  // usage: node render-art.js [src.html out-dir id...]
  //   default: renders #banner, #how, #phases in docs/src/readme-art.html to docs/images/*.png at 2x
  const root = path.resolve(__dirname, "../..");
  const [srcArg, outArg, ...idArgs] = process.argv.slice(2);
  const src = srcArg || "docs/src/readme-art.html", out = outArg || "docs/images";
  const ids = idArgs.length ? idArgs : ["banner", "how", "phases"];
  fs.mkdirSync(path.join(root, out), { recursive: true });
  const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1300, height: 900 }, deviceScaleFactor: 2 });
  await page.route("**/*", async route => {
    const url = route.request().url();
    if (url.startsWith("https://fonts.googleapis.com/")) return route.fulfill({ contentType: "text/css", body: css });
    if (url.startsWith("https://fonts.gstatic.com/")) return route.abort();
    if (url.startsWith("https://fonts.local/")) return route.fulfill({ contentType: "font/woff2", body: fs.readFileSync(path.join(__dirname, "node_modules", url.replace("https://fonts.local/", ""))) });
    if (url.startsWith("https://page.local/")) return route.fulfill({ contentType: "text/html", body: fs.readFileSync(path.join(root, src)) });
    return route.abort();
  });
  await page.goto("https://page.local/readme-art.html");
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  for (const id of ids) {
    await page.locator("#" + id).screenshot({ path: path.join(root, out, id + ".png"), omitBackground: true });
    console.log(out + "/" + id + ".png");
  }
  await browser.close();
})();
