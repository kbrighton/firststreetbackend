import { defineConfig } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const frontendDirectory = dirname(fileURLToPath(import.meta.url));
const nodeExecutable = JSON.stringify(process.execPath);
const isCi = Boolean(process.env.CI);
const browserChannel = process.env.PLAYWRIGHT_CHANNEL === ''
  ? undefined
  : process.env.PLAYWRIGHT_CHANNEL ?? 'msedge';

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: isCi ? 2 : 0,
  reporter: isCi
    ? [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]]
    : 'list',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    browserName: 'chromium',
    ...(browserChannel ? { channel: browserChannel } : {}),
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      command: `${nodeExecutable} e2e/start-flask.mjs`,
      cwd: frontendDirectory,
      url: 'http://127.0.0.1:5000/health',
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `${nodeExecutable} node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort`,
      cwd: frontendDirectory,
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: false,
      timeout: 120_000,
      env: { VITE_API_PROXY_TARGET: 'http://127.0.0.1:5000' },
    },
  ],
});
