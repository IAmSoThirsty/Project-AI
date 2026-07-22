import { defineConfig, devices } from "@playwright/test";

const baseURL = "http://127.0.0.1:4176";

export default defineConfig({
  testDir: "./tests/visual",
  outputDir: "../../../output/playwright/operator-console-results",
  snapshotPathTemplate: "{testDir}/__screenshots__/{testFilePath}/{arg}-{projectName}-{platform}{ext}",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ["line"],
    ["html", { outputFolder: "../../../output/playwright/operator-console-report", open: "never" }],
  ],
  expect: {
    toHaveScreenshot: {
      animations: "disabled",
      caret: "hide",
      maxDiffPixelRatio: 0.001,
      threshold: 0.2,
    },
  },
  use: {
    ...devices["Desktop Chrome"],
    baseURL,
    colorScheme: "dark",
    deviceScaleFactor: 1,
    locale: "en-US",
    reducedMotion: "reduce",
    screenshot: "only-on-failure",
    timezoneId: "UTC",
    trace: "retain-on-failure",
    viewport: { width: 1440, height: 1000 },
  },
  webServer: {
    command: "pnpm build && pnpm exec vite preview --host 127.0.0.1 --port 4176 --strictPort",
    url: baseURL,
    reuseExistingServer: false,
    timeout: 120_000,
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
