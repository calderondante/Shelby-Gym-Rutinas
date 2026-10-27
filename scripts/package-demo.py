"""Exporta una demo HTML autocontenida y un paquete público para Netlify Drop."""
import base64
import json
import mimetypes
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
OUT = Path('/workspace/entrega-shelby')
OUT.mkdir(exist_ok=True)
catalog = json.loads((PUBLIC / 'data/routines.json').read_text())
library = json.loads((PUBLIC / 'data/movements.json').read_text())
paths = {'images/shelby-reference.jpg', 'source/RUTINAS.pdf', 'licenses/everkinetic-CC-BY-SA-4.0.txt', 'data/movements.json'}
for movement in library['movements'].values():
    paths.update(movement.get('frames', []))
    paths.update(filter(None, [movement.get('video'), movement.get('poster')]))
assets = {}
for path in sorted(paths):
    file = PUBLIC / path
    assets[path] = {'mime': mimetypes.guess_type(path)[0] or 'application/octet-stream', 'base64': base64.b64encode(file.read_bytes()).decode()}

html = (PUBLIC / 'index.html').read_text()
html = html.replace('<link rel="stylesheet" href="style.css">', '<style>' + (PUBLIC / 'style.css').read_text() + '</style>')
html = html.replace('<script type="module" src="app.js"></script>', '')
logo = assets['images/shelby-reference.jpg']
html = html.replace('src="images/shelby-reference.jpg"', 'src="data:' + logo['mime'] + ';base64,' + logo['base64'] + '"')
html = html.replace('GUÍA DE ENTRENAMIENTO', 'VISTA PREVIA · RUTINAS')

credits = (PUBLIC / 'creditos.html').read_text()
credits = re.search(r'<main[^>]*>(.*?)</main>', credits, re.S)[1]
credits = re.sub(r'<a class="back-link".*?</a>', '', credits, count=1, flags=re.S)
html = html.replace('</main>', '</main><details id="demo-creditos" class="wrap credit-content"><summary>Créditos y fuentes de la demostración</summary>' + credits + '</details>', 1)

script = (PUBLIC / 'app.js').read_text()
fetch_block = """const data = await Promise.all(['data/routines.json', 'data/movements.json'].map(async (url) => {
      const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json();
    }));"""
assert script.count(fetch_block) == 1, 'Revisar el exportador: cambió la carga del catálogo.'
script = script.replace(fetch_block, 'const data = [embedded.catalog, embedded.library];')
# El archivo transportable mantiene navegación propia sin depender del historial file://.
script = script.replace("history.pushState({}, '', url);", 'demoQuery = url;')
script = script.replace('new URLSearchParams(location.search)', 'new URLSearchParams(demoQuery)')
bootstrap = """
const embedded = JSON.parse(document.getElementById('shelby-demo-data').textContent);
let demoQuery = location.search;
const demoUrls = {};
for (const [path, asset] of Object.entries(embedded.assets)) {
  const bytes = Uint8Array.from(atob(asset.base64), (c) => c.charCodeAt(0));
  demoUrls[path] = URL.createObjectURL(new Blob([bytes], {type: asset.mime}));
}
for (const movement of Object.values(embedded.library.movements)) {
  if (movement.frames) movement.frames = movement.frames.map((path) => demoUrls[path]);
  if (movement.video) movement.video = demoUrls[movement.video];
  if (movement.poster) movement.poster = demoUrls[movement.poster];
}
function resolveDemoLinks() {
  document.querySelectorAll('a[href]').forEach((link) => {
    const href = link.getAttribute('href');
    if (href === 'creditos.html' || href === 'creditos.html#ilustraciones-shelby') link.setAttribute('href', '#demo-creditos');
    const [path, fragment] = href.split('#');
    if (demoUrls[path]) link.setAttribute('href', demoUrls[path] + (fragment ? '#' + fragment : ''));
  });
}
new MutationObserver(resolveDemoLinks).observe(document.body, {childList:true, subtree:true});
document.addEventListener('click', (event) => {
  if (event.target.closest('a[href="#demo-creditos"]')) document.getElementById('demo-creditos').open = true;
});
resolveDemoLinks();
"""
payload = json.dumps({'catalog': catalog, 'library': library, 'assets': assets}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
html = html.replace('</body>', '<script id="shelby-demo-data" type="application/json">' + payload + '</script><script type="module">' + bootstrap + script + '</script></body>')
standalone = OUT / 'Shelby-Gym-DEMO.html'
standalone.write_text(html)

folder = OUT / 'Shelby-Gym-Rutinas-demo'
folder.mkdir(exist_ok=True)
shutil.copytree(PUBLIC, folder, dirs_exist_ok=True)
(folder / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n')
index = folder / 'index.html'
index.write_text(index.read_text().replace('GUÍA DE ENTRENAMIENTO', 'VISTA PREVIA · RUTINAS'))
archive = OUT / 'Shelby-Gym-Rutinas-Netlify.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as package:
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            package.write(path, Path(folder.name) / path.relative_to(folder))
assert not any(part.startswith('.') for path in folder.rglob('*') for part in path.relative_to(folder).parts)
(OUT / 'LEEME.txt').write_text('SHELBY GYM · DEMOSTRACIÓN\n\nPARA VER AHORA EN PC\nDescargar Shelby-Gym-DEMO.html y abrirlo con Chrome o Edge. No requiere servidor ni instalación. Incluye imágenes, animaciones, planilla y créditos.\n\nPARA OBTENER UN ENLACE COMPARTIBLE\n1. Descomprimir Shelby-Gym-Rutinas-Netlify.zip.\n2. Entrar en https://app.netlify.com/drop con tu cuenta.\n3. Arrastrar la carpeta Shelby-Gym-Rutinas-demo (la que contiene index.html).\n4. Netlify entrega el enlace del nuevo sitio. No seleccionar ni reemplazar el sitio de la administración.\n\nESTADO\n14 rutinas, 40 días/sesiones, 301 entradas. 255 entradas tienen demostración; las demás están identificadas como pendientes. Los descansos no escritos se consultan al entrenador. Es una vista previa, no la entrega final completa.\n')
print(f'Demo autocontenida: {standalone} ({standalone.stat().st_size} bytes)')
print(f'Paquete Netlify: {archive} ({archive.stat().st_size} bytes)')
