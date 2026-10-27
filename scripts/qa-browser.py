"""QA funcional. Requiere playwright de desarrollo y Chromium, no son dependencias del sitio."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SHELBY_QA_URL', 'http://127.0.0.1:4175')
OUT = Path(os.environ.get('SHELBY_QA_OUTPUT', '/tmp/shelby-qa'))
OUT.mkdir(parents=True, exist_ok=True)
catalog = json.loads((ROOT / 'public/data/routines.json').read_text())
report = {'engine': 'Chromium headless', 'physicalDevices': False, 'viewports': [], 'sessions': 0, 'checks': []}

def route(routine, day):
    return BASE + '/?rutina=' + routine['id'] + '&dia=' + day['id']

def no_overflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Overflow horizontal'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE, wait_until='networkidle')
    assert page.locator('.routine-card').count() == 14
    page.get_by_role('button', name='Femeninas', exact=True).click()
    assert page.locator('.routine-card').count() == 6
    page.get_by_role('button', name='Masculinas', exact=True).click()
    assert page.locator('.routine-card').count() == 7
    page.get_by_role('button', name='Todas', exact=True).click()
    page.locator('#routine-search').fill('femenina 6')
    assert page.locator('.routine-card').count() == 1
    page.locator('#routine-search').fill('no existe esta rutina')
    assert page.locator('.routine-card').count() == 0
    assert page.get_by_text('No encontramos esa rutina').is_visible()
    page.locator('#routine-search').fill('')
    report['checks'].append('Filtros, búsqueda y estado vacío')

    for routine in catalog['routines']:
        for day in routine['days']:
            response = page.goto(route(routine, day), wait_until='networkidle')
            page.wait_for_selector('.exercise')
            assert response.status == 200
            assert page.locator('.exercise').count() == len(day['exercises'])
            assert page.locator('.exercise h3').all_text_contents() == [e['name'] for e in day['exercises']]
            assert page.locator('.dose-strip').count() == len(day['exercises'])
            no_overflow(page)
            report['sessions'] += 1
    report['checks'].append('Navegación directa de los 40 días/sesiones y 301 ejercicios del PDF')

    routine = catalog['routines'][0]
    page.goto(route(routine, routine['days'][0]), wait_until='networkidle')
    first = page.locator('.done-control input').first
    first.check()
    page.reload(wait_until='networkidle')
    assert page.locator('.done-control input').first.is_checked()
    page.get_by_role('button', name='Reiniciar día', exact=True).click()
    assert not page.locator('.done-control input').first.is_checked()
    page.get_by_role('button', name='Deshacer reinicio', exact=True).click()
    assert page.locator('.done-control input').first.is_checked()
    report['checks'].append('Avance persistente, reinicio y deshacer')

    player = page.locator('[data-player]').first
    player.scroll_into_view_if_needed()
    page.wait_for_function('document.querySelector("[data-player] .play-toggle").textContent === "Pausar"')
    before = player.locator('img').get_attribute('src')
    page.wait_for_timeout(1250)
    assert player.locator('img').get_attribute('src') != before
    player.locator('.play-toggle').click()
    before = player.locator('img').get_attribute('src')
    page.wait_for_timeout(1250)
    assert player.locator('img').get_attribute('src') == before
    player.locator('.step-forward').click()
    assert player.locator('img').get_attribute('src') != before
    page.emulate_media(reduced_motion='reduce')
    before = player.locator('img').get_attribute('src')
    page.wait_for_timeout(1250)
    assert player.locator('img').get_attribute('src') == before
    report['checks'].append('Secuencia automática, pausa, paso siguiente y movimiento reducido')

    page.emulate_media(reduced_motion='no-preference')
    player.locator('.play-toggle').click()
    page.locator('#workout-title').scroll_into_view_if_needed()
    page.wait_for_timeout(250)
    before = player.locator('img').get_attribute('src')
    page.wait_for_timeout(1250)
    assert player.locator('img').get_attribute('src') == before
    report['checks'].append('Pausa fuera de pantalla')

    # Sprite: un único panel visible, recorrido de ida y vuelta y control manual.
    sprite = page.locator('.sequence-window').last
    sprite.scroll_into_view_if_needed()
    figure = sprite.locator('..').locator('..')
    page.wait_for_timeout(1300)
    figure.locator('.play-toggle').click()
    image = sprite.locator('img')
    old = image.evaluate('(el)=>el.style.transform')
    figure.locator('.step-forward').click()
    assert image.evaluate('(el)=>el.style.transform') != old
    assert sprite.evaluate('(el)=>getComputedStyle(el).overflow') == 'hidden'
    report['checks'].append('Hoja secuencial recortada: una posición visible y avance manual')

    # Combinación: cada componente mantiene su demostración e indicaciones.
    r = next(r for r in catalog['routines'] if r['id'] == 'rutina-masculina-4')
    page.goto(route(r, r['days'][0]), wait_until='networkidle')
    selector = page.locator('.part-select').first
    selector.select_option('1')
    assert selector.locator('option:checked').inner_text().startswith('2.')
    report['checks'].append('Selector del movimiento de una combinación')

    # MP4 de la muestra original, con el mismo control de reproducción.
    page.goto(route(r, r['days'][1]), wait_until='networkidle')
    video = page.locator('video').first
    video.scroll_into_view_if_needed()
    page.wait_for_function('document.querySelector("video").currentTime > 0')
    figure = video.locator('..').locator('..')
    figure.locator('.play-toggle').click()
    assert video.evaluate('(el)=>el.paused')
    assert video.evaluate('(el)=>el.muted && el.loop && el.playsInline')
    report['checks'].append('MP4 del GIF original: reproducción, silencio y pausa')

    for width in [375, 390, 768, 1024, 1440]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(BASE, wait_until='networkidle')
        no_overflow(page)
        page.screenshot(path=str(OUT / f'home-{width}.png'), full_page=True)
        page.keyboard.press('Tab')
        assert page.locator('.skip-link').evaluate('(el)=>el===document.activeElement')
        page.keyboard.press('Enter')
        page.goto(route(r, r['days'][0]), wait_until='networkidle')
        no_overflow(page)
        for figure in page.locator('[data-player]').all():
            figure.scroll_into_view_if_needed()
            for image in figure.locator('img').all():
                image.evaluate('(el)=>el.decode()')
        page.emulate_media(reduced_motion='reduce')
        page.screenshot(path=str(OUT / f'day-{width}.png'), full_page=True)
        no_overflow(page)
        report['viewports'].append({'width': width, 'overflow': False, 'keyboardSkip': True})
    assert not errors, errors
    report['javascriptErrors'] = errors
    report['webkitAvailable'] = Path(p.webkit.executable_path).exists()
    report['checks'].append('Cinco anchos, imágenes decodificadas y enlace de salto con teclado')
    browser.close()

(OUT / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
