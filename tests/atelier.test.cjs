// Tests comportementaux ciblés de l'atelier de scènes, sans dépendance npm.
// L'atelier réinjecte les données de la base : ces tests ne vérifient que les
// règles d'écriture outillées (protection des mineurs), pas le canon.
// Exécution : node --test tests/atelier.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../atelier/index.html'), 'utf8');

function extrait(debut, fin) {
  const a = html.indexOf(debut);
  const b = html.indexOf(fin, a);
  assert.ok(a >= 0 && b > a, `Bloc absent : ${debut}`);
  return html.slice(a, b);
}

const ADULTE = {id: 'P900', nom: 'Adulte', type: 'Humain', age: 44, secteur: 'La Baie'};
const MINEUR = {id: 'P901', nom: 'Mineur', type: 'Humain', age: 13, secteur: 'La Baie'};
const CHAT = {id: 'P902', nom: 'Chat', type: 'Animal', age: 7, secteur: 'La Baie'};

function chargerAtelier(personnages) {
  const contexte = vm.createContext({
    PERSOS: personnages,
    rels: [],
  });
  // Bloc des règles et de la distribution : melanger, relation, estMineur,
  // pressionAutorisee et choisirAutres.
  vm.runInContext(extrait('function melanger(liste){', 'function portrait(p){'), contexte);
  return contexte;
}

test('Les mineurs sont identifiés par le type et l’âge, jamais par le clan', () => {
  const contexte = chargerAtelier([ADULTE, MINEUR, CHAT]);
  assert.equal(vm.runInContext('estMineur(' + JSON.stringify(MINEUR) + ')', contexte), true);
  assert.equal(vm.runInContext('estMineur(' + JSON.stringify(ADULTE) + ')', contexte), false);
  // L'âge animal ne rend pas un animal « mineur » : la règle ne concerne que les humains.
  assert.equal(vm.runInContext('estMineur(' + JSON.stringify(CHAT) + ')', contexte), false);
});

test('Un mineur ne peut pas être la « pression » d’une dette ou d’un refus', () => {
  const contexte = chargerAtelier([ADULTE, MINEUR, CHAT]);
  for (const cle of ['dette', 'limite']) {
    assert.equal(vm.runInContext(
      `pressionAutorisee(${JSON.stringify(MINEUR)},'${cle}')`, contexte), false);
  }
  // Les autres moteurs gardent les mineurs disponibles comme pression.
  for (const cle of ['trace', 'rumeur', 'silence']) {
    assert.equal(vm.runInContext(
      `pressionAutorisee(${JSON.stringify(MINEUR)},'${cle}')`, contexte), true);
  }
  assert.equal(vm.runInContext(
    `pressionAutorisee(${JSON.stringify(ADULTE)},'dette')`, contexte), true);
});

test('choisirAutres respecte la règle sur un tirage réel', () => {
  const personnages = [ADULTE, MINEUR, {id: 'P903', nom: 'Autre', type: 'Humain', age: 30,
    secteur: 'Chicoutimi'}];
  const contexte = chargerAtelier(personnages);
  for (const cle of ['dette', 'limite']) {
    for (let i = 0; i < 200; i++) {
      vm.runInContext(`globalThis.__tirage = choisirAutres(PERSOS[0],'${cle}')`, contexte);
      const pression = vm.runInContext('globalThis.__tirage[0]', contexte);
      assert.notEqual(pression.id, MINEUR.id, `mineur en pression pour ${cle}`);
    }
  }
  // Le mineur reste disponible comme témoin : la protection ne l'exclut pas des scènes.
  vm.runInContext("globalThis.__temoins = choisirAutres(PERSOS[0],'dette').map(q=>q.id)", contexte);
  const pris = vm.runInContext('globalThis.__temoins', contexte);
  assert.equal(pris.length, 2);
  assert.ok(pris.every(id => id !== ADULTE.id));
});

test('L’atelier signale visiblement les mineurs en scène', () => {
  assert.match(html, /const MODES_SANS_MINEUR=\['dette','limite'\];/);
  assert.match(html, /— mineur, à protéger/);
  assert.match(html, /estMineur\(p\)\?' · mineur':'/);
  assert.match(html, /Les mineurs ne peuvent pas occuper la « pression »/);
  // La règle d'écriture existe aussi dans la documentation de l'atelier.
  const saison = fs.readFileSync(path.join(__dirname, '../docs/atelier-saison-1.md'), 'utf8');
  assert.match(saison, /mineurs restent des personnes à protéger/);
});
