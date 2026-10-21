"use strict";

const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

function argument(name, fallback = "") {
  const prefix = `--${name}=`;
  const item = process.argv.find((value) => value.startsWith(prefix));
  return item ? item.slice(prefix.length) : fallback;
}

const port = Number(argument("port", "0"));
const token = argument("token");
const parentPid = Number(argument("parent-pid", "0"));
const userDataDir = path.resolve(argument("user-data-dir", ".playwright-profile"));
const executablePath = argument("executable-path");
if (!port || !token) {
  throw new Error("Missing --port or --token");
}

let context;
let currentPage;

function isClosedTargetError(error) {
  const message = error && (error.stack || error.message || String(error));
  return /Target page, context or browser has been closed|browserContext\..*closed|Browser has been closed|Connection closed|Target\.createTarget.*Failed to open a new tab|Failed to open a new tab|browser has disconnected/i.test(message || "");
}

async function resetBrowserState() {
  const staleContext = context;
  context = undefined;
  currentPage = undefined;
  if (staleContext) await staleContext.close().catch(() => {});
}

function json(response, status, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  response.end(body);
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  if (!chunks.length) return {};
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

async function ensureBrowser() {
  if (context) return;
  const launchedContext = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    executablePath: executablePath || undefined,
    // Use the macOS login keychain, matching the normal Chrome process used
    // for the one-time login handoff. Playwright's mock-keychain defaults make
    // cookies written by normal Chrome unreadable after it takes control.
    ignoreDefaultArgs: [
      "--enable-automation",
      "--use-mock-keychain",
      "--password-store=basic",
    ],
    viewport: null,
    args: ["--start-maximized", "--disable-blink-features=AutomationControlled"],
  });
  context = launchedContext;
  launchedContext.setDefaultTimeout(20_000);
  launchedContext.setDefaultNavigationTimeout(90_000);
  launchedContext.on("page", (page) => {
    currentPage = page;
  });
  launchedContext.on("close", () => {
    if (context === launchedContext) {
      context = undefined;
      currentPage = undefined;
    }
  });
  currentPage = launchedContext.pages().find((page) => page.url().startsWith("https://chatgpt.com")) ||
    launchedContext.pages()[0] ||
    await launchedContext.newPage();
}

async function activePage() {
  await ensureBrowser();
  if (!currentPage || currentPage.isClosed()) {
    try {
      currentPage = context.pages().find((page) => !page.isClosed()) || await context.newPage();
    } catch (error) {
      if (isClosedTargetError(error)) {
        await resetBrowserState();
        await ensureBrowser();
        currentPage = context.pages().find((page) => !page.isClosed()) || await context.newPage();
      } else {
        throw error;
      }
    }
  }
  return currentPage;
}

function pageInfo(page, index) {
  return {
    index,
    targetId: String(index),
    tabId: String(index),
    label: page.url(),
    title: "",
    url: page.url(),
  };
}

async function runAction(action, body, existingPage) {
  if (action === "init") {
    await ensureBrowser();
    return { enabled: true, backend: "playwright", userDataDir };
  }
  if (action === "cleanup") {
    if (context) {
      await context.close();
      context = undefined;
      currentPage = undefined;
    }
    setImmediate(() => server.close(() => process.exit(0)));
    return { success: true };
  }

  const page = existingPage || await activePage();
  if (action === "open") {
    const targetUrl = new URL(body.url);
    const matchingPages = context.pages().filter((item) => {
      try {
        return !item.isClosed() && new URL(item.url()).host === targetUrl.host;
      } catch {
        return false;
      }
    });
    currentPage = matchingPages[0] || page;
    await Promise.all(matchingPages.slice(1).map((item) => item.close().catch(() => {})));
    // Re-read the shared profile after a normal Chrome login. A restored tab
    // can otherwise keep showing its pre-login DOM even though cookies exist.
    await currentPage.goto(body.url, { waitUntil: "domcontentloaded" });
    await currentPage.bringToFront();
    return pageInfo(currentPage, context.pages().indexOf(currentPage));
  }
  if (action === "get-url") return page.url();
  if (action === "tabs") {
    const tabs = await Promise.all(context.pages().map(async (item, index) => ({
      ...pageInfo(item, index),
      title: await item.title().catch(() => ""),
    })));
    return { tabs };
  }
  if (action === "tab-new") {
    currentPage = await context.newPage();
    if (body.url && body.url !== "about:blank") {
      await currentPage.goto(body.url, { waitUntil: "domcontentloaded" });
    }
    await currentPage.bringToFront();
    return pageInfo(currentPage, context.pages().indexOf(currentPage));
  }
  if (action === "tab-focus") {
    const pages = context.pages();
    if (body.index < 0 || body.index >= pages.length) throw new Error(`Tab index out of range: ${body.index}`);
    currentPage = pages[body.index];
    await currentPage.bringToFront();
    return pageInfo(currentPage, body.index);
  }
  if (action === "wait") {
    await page.waitForLoadState("domcontentloaded");
    await page.locator("body").waitFor({ state: "attached" });
    return { success: true };
  }
  if (action === "eval") {
    await page.locator("body").waitFor({ state: "attached" });
    let lastError;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        return await page.evaluate((expression) => {
          // The caller owns these expressions; indirect eval preserves global-page scope.
          return (0, eval)(expression);
        }, body.expression);
      } catch (error) {
        lastError = error;
        if (!/Execution context was destroyed|Target page.*closed|Cannot find context/i.test(error.message)) throw error;
        await page.waitForLoadState("domcontentloaded").catch(() => {});
      }
    }
    throw lastError;
  }
  if (action === "press") {
    await page.keyboard.press(body.key);
    return { success: true };
  }
  throw new Error(`Unsupported action: ${action}`);
}

const server = http.createServer(async (request, response) => {
  if (request.headers.authorization !== `Bearer ${token}`) {
    json(response, 401, { ok: false, error: "Unauthorized" });
    return;
  }
  if (request.method === "GET" && request.url === "/health") {
    try {
      const page = await activePage();
      await page.locator("body").waitFor({ state: "attached", timeout: 5_000 });
      json(response, 200, {
        ok: true,
        browserReady: true,
        pageCount: context.pages().filter((item) => !item.isClosed()).length,
      });
    } catch (error) {
      if (isClosedTargetError(error)) await resetBrowserState();
      json(response, 503, {
        ok: false,
        browserReady: false,
        error: error.stack || error.message || String(error),
      });
    }
    return;
  }
  if (request.method !== "POST" || request.url !== "/action") {
    json(response, 404, { ok: false, error: "Not found" });
    return;
  }
  try {
    const body = await readBody(request);
    let result;
    try {
      if (body.action === "init" || body.action === "cleanup") {
        result = await runAction(body.action, body);
      } else {
        const page = await activePage();
        result = await runAction(body.action, body, page);
      }
    } catch (error) {
      if (body.action === "cleanup" || !isClosedTargetError(error)) throw error;
      await resetBrowserState();
      if (body.action === "init") {
        result = await runAction(body.action, body);
      } else {
        const page = await activePage();
        result = await runAction(body.action, body, page);
      }
    }
    json(response, 200, { ok: true, result });
  } catch (error) {
    json(response, 500, { ok: false, error: error.stack || error.message || String(error) });
  }
});

server.listen(port, "127.0.0.1", () => {
  process.stdout.write(`READY ${port}\n`);
});

async function shutdown() {
  if (context) await context.close().catch(() => {});
  server.close(() => process.exit(0));
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
if (parentPid) {
  const parentWatch = setInterval(() => {
    try {
      process.kill(parentPid, 0);
    } catch {
      clearInterval(parentWatch);
      shutdown();
    }
  }, 2_000);
  parentWatch.unref();
}
