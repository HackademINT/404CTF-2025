const puppeteer = require('puppeteer');

async function visit(path, token, challenge_host) {
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome-stable",
    args: [
      "--no-sandbox",
      "--disable-gpu",
      "--disable-jit",
      "--disable-wasm",
      "--ignore-certificate-errors",
      "--incognito",
    ],
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await browser.setCookie({
      name: "token",
      value: token,
      domain: challenge_host,
    });
    await page.goto(`http://${challenge_host}${path}`, {
      waitUntil: "networkidle0",
      timeout: 4000,
    });
    await page.close();
  } catch (e) {
    console.error("Error during visit:", e.message);
  } finally {
    await browser.close();
  }
}

module.exports = { visit };
