import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'node:fs';
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
export default defineConfig({
  testDir: './tests', fullyParallel: false, workers: 1, timeout: 30000,
  expect: { timeout: 10000 }, reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:3107', trace: 'retain-on-failure', ...devices['Desktop Chrome'],
    launchOptions: existsSync(chrome) ? { executablePath: chrome } : {},
  },
  webServer: { command: 'npm run dev -- --hostname 127.0.0.1 --port 3107', url: 'http://127.0.0.1:3107/api/health', reuseExistingServer: !process.env.CI, timeout: 120000 },
});
