// Tests comportementaux ciblés du JavaScript canonique, sans dépendance npm.
// Exécution : node --test tests/carte.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../carte/index.html'), 'utf8');
function extrait(debut, fin) {
  const a = html.indexOf(debut);
  const b = html.indexOf(fin, a);
  assert.ok(a >= 0 && b > a, `Bloc absent : ${debut}`);
  return html.slice(a, b);
}

test('Les événements Leaflet affichent latitude et longitude sans erreur', () => {
  const handlers = {};
  const coords = {textContent: ''};
  const contexte = vm.createContext({
    document: {getElementById: () => coords},
    map: {
      on: (event, handler) => { handlers[event] = handler; },
      getZoom: () => 15,
      getCenter: () => ({lat: 48.34, lng: -70.88}),
    },
  });
  vm.runInContext(extrait("map.on('mousemove',e=>{", "document.getElementById('home')"), contexte);
  handlers.mousemove({latlng: {lat: 48.33, lng: -70.89}});
  assert.equal(coords.textContent, '48.33000, -70.89000  ·  z15');
  handlers.zoomend();
  assert.equal(coords.textContent, '48.34000, -70.88000  ·  z15');
});

test('Les repères locaux corrompus sont ignorés sans exception', () => {
  const bloc = extrait("const KEY='mes_reperes_labaie';", 'function saveMine');
  const contexte = vm.createContext({
    localStorage: {getItem: () => JSON.stringify([
      {n: '  Point conservé  ', la: '48.33', lo: '-70.89'},
      {n: '', la: 48.3, lo: -70.8},
      {n: 'Coordonnée invalide', la: 999, lo: -70.8},
    ])},
    console: {warn: () => {}},
  });
  vm.runInContext(bloc, contexte);
  assert.equal(vm.runInContext('mine.length', contexte), 1);
  assert.equal(vm.runInContext('mine[0].n', contexte), 'Point conservé');
  assert.equal(vm.runInContext('mine[0].la', contexte), 48.33);

  const corrompu = vm.createContext({
    localStorage: {getItem: () => '{pas du JSON'},
    console: {warn: () => {}},
  });
  vm.runInContext(bloc, corrompu);
  assert.equal(vm.runInContext('mine.length', corrompu), 0);
});

test('Un échec de stockage des repères ne fait pas planter la carte', () => {
  const bloc = extrait('function saveMine(){', 'function renderCount(){');
  let alertes = 0;
  const contexte = vm.createContext({
    localStorage: {setItem: () => { throw new Error('quota'); }},
    console: {warn: () => {}},
    alert: () => { alertes++; },
    renderCount: () => {},
    mine: [{n: 'Point', la: 48.3, lo: -70.8}],
  });
  vm.runInContext(bloc, contexte);
  assert.equal(vm.runInContext('saveMine()', contexte), false);
  assert.equal(alertes, 1);
});

for (const categorie of ['p', 'a']) {
  test(`La recherche révèle un résultat masqué (${categorie}) et synchronise les cases`, () => {
    const p = {secteur: 'La Baie', type: categorie === 'p' ? 'Humain' : 'Animal'};
    const o = {p, c: categorie, m: {}};
    const couches = {p: new Set(), a: new Set()};
    const cases = {p: {checked: false}, a: {checked: false}};
    const filtresCases = [{checked: false}, {checked: false}];
    const FILTRES = {secteurs: new Set(), types: new Set(), tranche: '60+'};
    const catOn = {p: false, a: false};
    const sel = {value: '60+'};
    let applications = 0;
    const contexte = vm.createContext({
      PERSOS: [p], FILTRES, catOn, sel,
      grp: Object.fromEntries(['p', 'a'].map(k => [k, {
        hasLayer: m => couches[k].has(m),
        removeLayer: m => couches[k].delete(m),
      }])),
      cb: {querySelector: selector => cases[selector.match(/data-c="([pa])"/)[1]]},
      fBox: {querySelectorAll: () => filtresCases},
      appliquerFiltres: () => {
        applications++;
        if (catOn[o.c] && FILTRES.secteurs.has(p.secteur)
            && FILTRES.types.has(p.type) && FILTRES.tranche === '') couches[o.c].add(o.m);
      },
    });
    vm.runInContext(extrait('function reveler(o){', 'function allerPerso(o){'), contexte);
    contexte.reveler(o);
    assert.ok(couches[o.c].has(o.m));
    assert.equal(cases[o.c].checked, true);
    const autre = categorie === 'p' ? 'a' : 'p';
    assert.equal(catOn[autre], false);
    assert.equal(cases[autre].checked, false);
    assert.ok(filtresCases.every(i => i.checked));
    assert.equal(sel.value, '');
    assert.equal(applications, 1);
    // Un résultat déjà visible ne modifie pas les filtres.
    contexte.reveler(o);
    assert.equal(applications, 1);
  });
}
