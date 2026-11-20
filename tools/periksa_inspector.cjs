/* Smoke test logika inspector dengan DOM tiruan, bukan browser visual.
 * node tools/periksa_inspector.cjs — stdlib Node, tanpa npm install.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
class Element {
  constructor() { this.textContent = ''; this.children = []; this.value = ''; }
  append(element) { this.children.push(element); }
  replaceChildren() { this.children = []; }
  addEventListener() {}
}
const nodes = {};
const document = {
  getElementById: id => nodes[id] || (nodes[id] = new Element()),
  createElement: () => new Element()
};
const html = fs.readFileSync(path.join(__dirname, '../examples/inspector.html'), 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];
const assertions = `
show(JSON.stringify({hud:{nama:'<script>alert(1)</script>',bars:{energi:.5}}}));
assert.equal(nodes.name.textContent,'<script>alert(1)</script>');
assert.equal(nodes.bars.children.length,1);
assert.equal(nodes.bars.children[0].children[0].value,.5);
show('{"nama":"Rama","bars":{"energi":2}}');
assert.equal(nodes.name.textContent,'Data tidak sah');
assert.equal(nodes.bars.children.length,0);
show('[]');assert.ok(nodes.error.textContent);
show('{');assert.ok(nodes.error.textContent);
show('{"nama":"Rama","bars":null}');assert.ok(nodes.error.textContent);
show('{"nama":"Rama","bars":{"energi":0}}');assert.equal(nodes.error.textContent,'');
`;
new Function('document', 'assert', 'nodes', script + assertions)(document, assert, nodes);
console.log('Inspector DOM smoke: PASS');
