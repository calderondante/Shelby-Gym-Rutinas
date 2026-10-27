"""Copia únicamente recursos usados, conservando licencia y procedencia."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
upstream = json.loads((source / 'exercises.json').read_text())
by_id = {e['id_num']: e for e in upstream}
destination = ROOT / 'public/media/everkinetic'
destination.mkdir(parents=True, exist_ok=True)
movements = {}
commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD']).decode().strip()
for line in (ROOT / 'data/movements.tsv').read_text().splitlines():
    if not line or line.startswith('#'):
        continue
    ident, title, setup, action, cue = line.split('|')
    entry = by_id[ident]
    frames = []
    for i, phase in enumerate(['relaxation', 'tension']):
        svg = source / f'dist/svg/{ident}-{phase}.svg'
        original = svg if svg.exists() else source / 'src/images-web' / Path(entry['img'][i]).name
        assert original.exists(), original
        target = destination / (ident + '-' + str(i) + original.suffix)
        shutil.copyfile(original, target)
        frames.append(str(target.relative_to(ROOT / 'public')))
    if ident in {'0007', '0010', '0124', '0122', '0194', '0079', '0054', '0220', '0294', '0107', '0123', '0127', '0143', '0198', '0183'}:
        frames.reverse()  # El orden de archivo upstream no siempre coincide con la postura inicial.
    movements[ident] = {'title': title, 'steps': [setup, action], 'cue': cue, 'frames': frames, 'sourceName': entry['title'], 'source': f'https://github.com/everkinetic/data/tree/{commit}', 'license': 'CC BY-SA 4.0', 'author': 'Everkinetic · Greg Priday', 'adaptation': 'Indicaciones adaptadas al español; ilustraciones copiadas sin modificar.'}

movements['original-remo'] = {'title': 'Remo con mancuerna a un brazo', 'steps': ['Apoyá una mano y una rodilla en el banco; dejá el otro pie firme en el piso.', 'Desde el brazo extendido, llevá el codo hacia la cadera. Bajá la mancuerna despacio antes de cambiar de lado.'], 'cue': 'Evitá girar el tronco para levantar la carga.', 'video': 'media/remo-mancuerna.mp4', 'poster': 'images/remo-mancuerna-01.webp', 'author': 'Shelby Gym · muestra original', 'license': 'Uso autorizado por el gimnasio', 'source': 'https://github.com/calderondante/Shelby-Gym/tree/gh-pages/rutinas'}
movements['original-puente'] = {'title': 'Elevación de pelvis en colchoneta', 'steps': ['Acostate boca arriba con las rodillas flexionadas y los pies en el piso.', 'Empujá con los pies y elevá la cadera de forma controlada. Bajá sin dejarla caer.'], 'cue': 'Buscá el esfuerzo en glúteos sin arquear de más la zona lumbar.', 'video': 'media/puente-gluteos.mp4', 'poster': 'images/puente-gluteos-01.webp', 'author': 'Shelby Gym · muestra original', 'license': 'Uso autorizado por el gimnasio', 'source': 'https://github.com/calderondante/Shelby-Gym/tree/gh-pages/rutinas'}
video = ROOT / 'public/media/remo-mancuerna.mp4'
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(ROOT / 'public/images/remo-mancuerna.gif'), '-an', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)], check=True)
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(ROOT / 'public/images/puente-gluteos.gif'), '-an', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(ROOT / 'public/media/puente-gluteos.mp4')], check=True)
(ROOT / 'public/licenses').mkdir(exist_ok=True)
shutil.copyfile(source / 'LICENSE.md', ROOT / 'public/licenses/everkinetic-CC-BY-SA-4.0.txt')
movements.update(json.loads((ROOT / 'data/generated-movements.json').read_text()))
aliases = json.loads((ROOT / 'data/aliases.json').read_text())
mapping = {alias: [ident] for ident, names in aliases.items() for alias in names}
mapping.update(json.loads((ROOT / 'data/combinations.json').read_text()))
assert all(ident in movements for ids in mapping.values() for ident in ids)
result = {'movements': movements, 'mapping': mapping, 'upstreamCommit': commit}
(ROOT / 'public/data/movements.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
catalog = json.loads((ROOT / 'public/data/routines.json').read_text())
entries = [e for r in catalog['routines'] for d in r['days'] for e in d['exercises']]
missing = {e['key']: e['name'] for e in entries if e['key'] not in mapping}
(ROOT / 'docs/MEDIOS_PENDIENTES.json').write_text(json.dumps(missing, ensure_ascii=False, indent=2) + '\n')
print(f'{len(movements)} demostraciones; {sum(e["key"] in mapping for e in entries)}/{len(entries)} entradas con coincidencia visual; {len(missing)} nombres pendientes.')
