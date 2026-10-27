// Refresca correspondencias usando únicamente recursos ya preparados localmente.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (file) => JSON.parse(readFileSync(resolve(root, file), 'utf8'));
const write = (file, data) => writeFileSync(resolve(root, file), JSON.stringify(data, null, 2) + '\n');
const library = read('public/data/movements.json');
Object.assign(library.movements, read('data/generated-movements.json'));
library.mapping = Object.fromEntries(Object.entries(read('data/aliases.json')).flatMap(([id, names]) => names.map((name) => [name, [id]])));
Object.assign(library.mapping, read('data/combinations.json'));
for (const [name, ids] of Object.entries(library.mapping)) {
  for (const id of ids) if (!library.movements[id]) throw new Error(`Falta demostración ${id} para ${name}`);
}
write('public/data/movements.json', library);
const entries = read('public/data/routines.json').routines.flatMap((r) => r.days.flatMap((d) => d.exercises));
write('docs/MEDIOS_PENDIENTES.json', Object.fromEntries(entries.filter((e) => !library.mapping[e.key]).map((e) => [e.key, e.name])));
console.log('Correspondencias regeneradas sin descargar medios ni instalar paquetes.');
