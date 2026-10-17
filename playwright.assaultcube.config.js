const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser-assaultcube',
  timeout: 180000,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'test-results/assaultcube-results.json' }]],
  use: { baseURL: 'http://127.0.0.1:8878', viewport: { width: 1280, height: 1000 },
    headless: false, screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }, { name: 'firefox', use: { browserName: 'firefox' } }],
  webServer: {
    command: `${process.env.PYTHON || 'python3'} scripts/serve.py examples/assaultcube/build/web --port 8878`,
    url: 'http://127.0.0.1:8878/', reuseExistingServer: false
  }
});
