"""Importa el texto de pdftotext -layout, sin inferir dosis ni instrucciones."""
import json
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def slug(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def parse(text):
    routines = []
    routine = day = exercise = None
    bullets = 0
    for page, content in enumerate(text.split('\f'), 1):
        if page == 1:
            continue  # índice, no duplicar rutinas
        for line in content.splitlines():
            line = ' '.join(line.split())
            if not line or line.startswith('Instagram:'):
                continue
            if re.match(r'^RUTINA (?:MASCULINA|FEMENINA|DE ADAPTACION)', line):
                routine = {'id': slug(line), 'title': line.capitalize(), 'category': 'adaptacion' if 'ADAPTACION' in line else ('femenina' if 'FEMENINA' in line else 'masculina'), 'page': page, 'warmup': '', 'days': []}
                routines.append(routine)
                day = exercise = None
            elif 'Pre-calentamiento' in line:
                continue
            elif line.startswith('10 minutos'):
                routine['warmup'] = line
            elif re.search(r'D[ÍíIi]A?\s*\d\s*:', line, re.I):
                match = re.search(r'D[ÍíIi]A?\s*(\d)\s*:\s*(.*)', line, re.I)
                day = {'id': 'dia-' + match[1], 'number': int(match[1]), 'title': match[2].strip().rstrip('.'), 'page': page, 'exercises': []}
                routine['days'].append(day)
                exercise = None
            elif line[0] in '•✓':
                bullets += 1
                if day is None:
                    day = {'id': 'sesion', 'number': 1, 'title': 'Sesión de adaptación', 'page': page, 'exercises': []}
                    routine['days'].append(day)
                parts = re.split(r'Repeticiones:\s*', line[1:].strip(), maxsplit=1)
                name = parts[0].strip().rstrip('.:')
                exercise = {'id': f'{day["id"]}-{len(day["exercises"])+1}', 'name': name, 'key': slug(name), 'prescription': parts[1] if len(parts) > 1 else '', 'page': page, 'rest': None}
                day['exercises'].append(exercise)
            elif line.startswith('Repeticiones:'):
                assert exercise is not None, (page, line)
                exercise['prescription'] = line.split(':', 1)[1].strip()
            else:
                raise ValueError(f'Línea no interpretada, página {page}: {line}')
    for r in routines:
        assert r['warmup'] and r['days'], r['title']
        for d in r['days']:
            assert d['exercises'], (r['title'], d['title'])
            for e in d['exercises']:
                assert e['prescription'], e
                if 's/descanso' in e['prescription']:
                    e['rest'] = 'Sin descanso, según la planilla'
    assert len(routines) == 14
    assert bullets == sum(len(d['exercises']) for r in routines for d in r['days'])
    return {'source': {'file': 'source/RUTINAS.pdf', 'pages': 38, 'title': 'RUTINAS.pdf', 'revision': hashlib.sha256(text.encode()).hexdigest(), 'approval': 'Material aportado y aprobado por el gimnasio en esta conversación'}, 'routines': routines}

if __name__ == '__main__':
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs/source/RUTINAS.txt'
    data = parse(source.read_text())
    (ROOT / 'public/data/routines.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    entries = [e for r in data['routines'] for d in r['days'] for e in d['exercises']]
    print(f'{len(data["routines"])} rutinas; {sum(len(r["days"]) for r in data["routines"])} días/sesiones; {len(entries)} entradas; {len({e["key"] for e in entries})} nombres distintos')
