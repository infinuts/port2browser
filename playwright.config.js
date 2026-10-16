const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser',
  fullyParallel: true,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'test-results/results.json' }]],
  use: { baseURL: 'http://127.0.0.1:8765', screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }, { name: 'firefox', use: { browserName: 'firefox' } }],
  webServer: {
    command: `${process.env.PYTHON || 'python3'} scripts/serve.py examples --port 8765`,
    url: 'http://127.0.0.1:8765/sdl-beacon/build/web/',
    reuseExistingServer: false
  }
});
