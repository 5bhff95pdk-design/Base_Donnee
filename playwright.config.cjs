const {defineConfig} = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [['list'], ['html', {open: 'never'}]],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:8000',
    browserName: 'chromium',
    viewport: {width: 1280, height: 900},
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    // Facultatif : navigateur déjà installé dans un environnement isolé.
    launchOptions: process.env.CHROMIUM_EXECUTABLE_PATH ? {
      executablePath: process.env.CHROMIUM_EXECUTABLE_PATH,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    } : {},
  },
  // En local, démarrer le serveur séparément (voir README).
  // En CI, Playwright gère son démarrage et son arrêt.
  webServer: process.env.CI ? {
    command: 'python3 -m http.server 8000 --bind 0.0.0.0',
    url: 'http://127.0.0.1:8000/carte/index.html',
    reuseExistingServer: false,
  } : undefined,
});
