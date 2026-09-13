const {test, expect} = require('@playwright/test');
const personnages = require('../../base_personnages_fictifs.json');
const fs = require('node:fs/promises');

// Même parcours pour la source canonique et la copie livrée à la racine.
for (const url of ['/carte/index.html', '/carte-la-baie-saguenay.html']) {
  test.describe(url, () => {
    let erreurs;
    test.beforeEach(async ({page, baseURL}) => {
      erreurs = [];
      page.on('pageerror', error => erreurs.push(error.message));
      // Aucun appel réel aux services de tuiles ou à Nominatim : tests stables,
      // sans charge sur les services publics. Le code Leaflet reste bien réel.
      await page.route('**/*', route => {
        if (new URL(route.request().url()).origin === new URL(baseURL).origin) return route.continue();
        if (route.request().resourceType() === 'image') return route.fulfill({
          contentType: 'image/png',
          body: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aOZkAAAAASUVORK5CYII=', 'base64'),
        });
        return route.fulfill({contentType: 'application/json', body: '[]'});
      });
      await page.goto(url);
      await expect(page.locator('#nvis')).toHaveText(`${personnages.length} / ${personnages.length} personnages affichés`);
    });
    test.afterEach(() => { expect(erreurs, 'Aucune exception JavaScript').toEqual([]); });

    test('recherche sans accents et portrait chargé', async ({page}) => {
      await page.getByRole('searchbox').fill('real chicoine');
      await page.locator('#res-persos').getByText('Réal Chicoine', {exact: true}).click();
      const popup = page.locator('.leaflet-popup');
      await expect(popup).toContainText('Réal Chicoine');
      await expect(popup.locator('img.pic')).toBeVisible();
      await expect.poll(() => popup.locator('img.pic').evaluate(img => img.complete && img.naturalWidth > 0)).toBe(true);
    });

    test('filtres secteur, type et âge combinés', async ({page}) => {
      await page.locator('#filtres').getByRole('checkbox', {name: 'Chicoutimi'}).uncheck();
      await page.locator('#filtres').getByRole('checkbox', {name: 'Animal'}).uncheck();
      await page.getByLabel('Tranche d’âge').selectOption('-18');
      const nombre = personnages.filter(p => p.secteur !== 'Chicoutimi' && p.type !== 'Animal' && p.age < 18).length;
      await expect(page.locator('#nvis')).toHaveText(`${nombre} / ${personnages.length} personnages affichés`);
      await expect(page.locator('.leaflet-marker-icon.mk-p')).toHaveCount(nombre);
      await expect(page.locator('.leaflet-marker-icon.mk-a')).toHaveCount(0);
    });

    for (const [categorie, nom] of [['p', 'Réal Chicoine'], ['a', 'Pisse-Feu']]) {
      test(`recherche après masquage de la catégorie ${categorie}`, async ({page}) => {
        await page.locator('#cats input[data-c="p"]').uncheck();
        await page.locator('#cats input[data-c="a"]').uncheck();
        await page.locator('#filtres').getByRole('checkbox', {name: 'La Baie'}).uncheck();
        await page.getByLabel('Tranche d’âge').selectOption('60+');
        await page.getByRole('searchbox').fill(nom);
        await page.locator('#res-persos').getByText(nom, {exact: true}).click();
        await expect(page.locator('.leaflet-popup')).toContainText(nom);
        await expect(page.locator(`#cats input[data-c="${categorie}"]`)).toBeChecked();
        await expect(page.locator(`#cats input[data-c="${categorie === 'p' ? 'a' : 'p'}"]`)).not.toBeChecked();
        await expect(page.getByLabel('Tranche d’âge')).toHaveValue('');
        const nombre = personnages.filter(p => p.type === (categorie === 'p' ? 'Humain' : 'Animal')).length;
        await expect(page.locator('#nvis')).toHaveText(`${nombre} / ${personnages.length} personnages affichés`);
        await expect(page.locator(`.leaflet-marker-icon.mk-${categorie}`)).toHaveCount(nombre);
      });
    }

    test('coordonnées au mouvement et au zoom', async ({page}) => {
      await page.locator('#map').hover({position: {x: 350, y: 250}});
      await expect(page.locator('#coords')).toHaveText(/48\.\d{5}, -7\d\.\d{5}  ·  z\d+/);
      const avant = Number((await page.locator('#coords').textContent()).match(/z(\d+)/)[1]);
      await page.locator('.leaflet-control-zoom-in').click();
      await expect(page.locator('#coords')).toHaveText(new RegExp(`48\\.\\d{5}, -7\\d\\.\\d{5}  ·  z${avant + 1}$`));
    });

    test('repère : création, persistance, export et suppression', async ({page}) => {
      const nom = 'Mon repère « test »';
      page.once('dialog', dialog => dialog.accept(nom));
      await page.locator('#map').click({button: 'right', position: {x: 350, y: 250}});
      await expect(page.locator('#count')).toContainText('1 repère enregistré');
      await page.reload();
      await expect(page.locator('#count')).toContainText('1 repère enregistré');
      await expect(page.locator('.leaflet-marker-icon.mk-u')).toHaveCount(1);
      const exportPromise = page.waitForEvent('download', d => d.suggestedFilename().endsWith('.geojson'));
      await page.locator('#exp').click();
      const download = await exportPromise;
      const geojson = JSON.parse(await fs.readFile(await download.path(), 'utf8'));
      expect(geojson.features).toHaveLength(1);
      expect(geojson.features[0].properties.nom).toBe(nom);
      expect(geojson.features[0].geometry.coordinates.every(Number.isFinite)).toBe(true);
      page.once('dialog', dialog => dialog.accept());
      await page.locator('#clr').click();
      await expect(page.locator('#count')).toBeEmpty();
      await page.reload();
      await expect(page.locator('.leaflet-marker-icon.mk-u')).toHaveCount(0);
    });

    test('mobile : avertissement visible et menu ouvrable', async ({page}) => {
      await page.setViewportSize({width: 390, height: 844});
      await expect(page.locator('header .banner')).toBeVisible();
      await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
      await page.getByTitle('Menu', {exact: true}).click();
      await expect(page.locator('#sidebar')).toHaveClass('open');
      await page.locator('#cats input[data-c="p"]').uncheck();
      await expect(page.locator('#nvis')).toHaveText(`1 / ${personnages.length} personnages affichés`);
      await page.getByTitle('Menu', {exact: true}).click();
      await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
    });
  });
}
