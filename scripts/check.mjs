import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (file) => readFileSync(resolve(root, file), 'utf8');
const catalog = JSON.parse(read('public/data/routines.json'));
const media = JSON.parse(read('public/data/movements.json'));
const source = read('docs/source/RUTINAS.txt');
const entries = catalog.routines.flatMap((r) => r.days.flatMap((d) => d.exercises));
assert.equal(catalog.routines.length, 14);
assert.equal(catalog.routines.reduce((sum, r) => sum + r.days.length, 0), 40);
assert.equal(entries.length, 301);
assert.equal((source.match(/Repeticiones:/g) || []).length, entries.length, 'Cada dosis del PDF debe estar importada una sola vez');
assert.equal(catalog.routines.filter((r) => r.category === 'femenina').length, 6);
assert.equal(catalog.routines.filter((r) => r.category === 'masculina').length, 7);
for (const routine of catalog.routines) {
  assert.equal(routine.warmup, '10 minutos de escalador + 10 minutos de cinta + 10 minutos de bici.');
  assert.equal(new Set(routine.days.map((d) => d.id)).size, routine.days.length);
  for (const day of routine.days) {
    assert(day.exercises.length > 0);
    assert.equal(new Set(day.exercises.map((e) => e.id)).size, day.exercises.length);
    for (const e of day.exercises) {
      assert(e.name && e.prescription && e.page >= 2 && e.page <= 38);
      assert(source.split('\f')[e.page - 1].includes(e.name), `Nombre no encontrado en la página declarada: ${e.name}`);
      assert(e.rest === null || e.prescription.includes('s/descanso'), 'No agregar descansos no presentes en la fuente');
    }
  }
}
const last = catalog.routines.at(-1);
assert.equal(last.id, 'rutina-masculina-7');
assert.equal(last.days[0].exercises[0].prescription, '20-15-12-10-8-6-4.');
assert.equal(last.days[0].exercises[4].prescription, '20-15-10-12-10-8-6.');
assert.equal(last.days[1].exercises.at(-1).prescription, '20-18-15-10-8- (10 + 10 + 10)');
assert(entries.some((e) => e.prescription === '1 x 20 - 3 x 10 + 10 (bajando el peso).'));
for (const ids of Object.values(media.mapping)) {
  assert(ids.length);
  for (const id of ids) assert(media.movements[id], `Referencia visual rota: ${id}`);
}
for (const movement of Object.values(media.movements)) {
  assert(movement.title && movement.steps.length >= 2 && movement.author && movement.license && movement.source);
  for (const file of [...(movement.frames || []), movement.video, movement.poster].filter(Boolean)) {
    assert(existsSync(resolve(root, 'public', file)), `Medio faltante: ${file}`);
    if (file.endsWith('.svg')) assert(!/<script|<foreignObject|\bonload=|\bonerror=|https?:\/\//i.test(read(`public/${file}`).replace(/xmlns="http:\/\/www.w3.org\/2000\/svg"/, '')), `SVG activo: ${file}`);
  }
}
assert(existsSync(resolve(root, 'public/source/RUTINAS.pdf')));
console.log(`Contenido válido: 14 rutinas, 40 sesiones, ${entries.length} entradas; ${entries.filter((e) => media.mapping[e.key]).length} con demostración.`);
