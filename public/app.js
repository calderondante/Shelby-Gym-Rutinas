const externalIcon = '<svg class="external-icon" aria-hidden="true" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 13 13 3M3 3h10v10"/></svg>';
const $ = (selector, root = document) => root.querySelector(selector);
const escape = (value) => String(value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
let catalog, library, category = 'todas', search = '', players = [], globalPaused = false;
let renderedQuery = null;
let saved = {}, canSave = true, undo = null;
try { saved = JSON.parse(localStorage.getItem('shelby-rutinas-progress-v1') || '{}'); if (!saved || typeof saved !== 'object' || Array.isArray(saved)) saved = {}; }
catch { canSave = false; }

function persist() {
  try { localStorage.setItem('shelby-rutinas-progress-v1', JSON.stringify(saved)); }
  catch { canSave = false; }
  const status = $('#save-status');
  if (status) status.textContent = canSave ? 'Tu avance se guarda en este dispositivo.' : 'Tu avance se conserva solo durante esta sesión.';
}
function address(routine, day) {
  return `?rutina=${encodeURIComponent(routine.id)}&dia=${encodeURIComponent(day.id)}`;
}
function go(url, focus = true) {
  history.pushState({}, '', url);
  render(focus);
}
function stopPlayers() { players.forEach((player) => player.destroy()); players = []; }
function focusHeading(id) {
  const heading = $(id); heading.focus({ preventScroll: true });
  heading.scrollIntoView({ block: 'start', behavior: 'instant' });
}
function render(focus = false) {
  stopPlayers();
  renderedQuery = location.search;
  const params = new URLSearchParams(location.search);
  const routine = catalog.routines.find((item) => item.id === params.get('rutina'));
  $('#catalog-view').hidden = !!routine;
  $('#workout-view').hidden = !routine;
  $('#home-link').hidden = !routine;
  if (!routine) {
    document.title = 'Rutinas · Shelby Gym';
    renderCatalog();
    if (focus) focusHeading('#catalog-title');
    return;
  }
  const day = routine.days.find((item) => item.id === params.get('dia')) || routine.days[0];
  document.title = `${routine.title} · ${day.id === 'sesion' ? 'Sesión' : `Día ${day.number}`} | Shelby Gym`;
  const stateKey = `${catalog.source.revision}/${routine.id}/${day.id}`;
  const validIds = new Set(day.exercises.map((e) => e.id));
  const completed = new Set(Array.isArray(saved[stateKey]) ? saved[stateKey].filter((id) => validIds.has(id)) : []);
  const dayName = day.id === 'sesion' ? 'Sesión de adaptación' : `Día ${day.number}`;
  const view = $('#workout-view');
  view.innerHTML = `
    <section class="workout-heading wrap">
      <a class="back-link" href="?" data-route>← Todas las rutinas</a>
      <p class="eyebrow">TU PLAN DE ENTRENAMIENTO</p>
      <h1 id="workout-title" tabindex="-1">${escape(routine.category === 'adaptacion' ? 'Rutina de adaptación' : routine.title)}</h1>
      <p class="intro">Elegí el día indicado por tu entrenador y seguí los ejercicios en orden.</p>
      <label class="routine-switch">Cambiar rutina<select id="routine-select">${catalog.routines.map((r) => `<option value="${escape(r.id)}" ${r.id === routine.id ? 'selected' : ''}>${escape(r.title)}</option>`).join('')}</select></label>
      <nav class="day-tabs" aria-label="Días de la rutina">${routine.days.map((d) => `<a href="${address(routine, d)}" data-route ${d.id === day.id ? 'aria-current="page"' : ''}>${d.id === 'sesion' ? 'Sesión' : `Día ${d.number}`}<span>${d.exercises.length} ejercicios</span></a>`).join('')}</nav>
    </section>
    <section class="wrap session" aria-labelledby="day-title">
      <div class="session-heading"><div><p class="eyebrow">${escape(dayName)}</p><h2 id="day-title">${escape(day.title)}</h2></div><a class="source-link" href="source/RUTINAS.pdf#page=${day.page}" target="_blank" rel="noopener">Ver planilla ${externalIcon}<span>Página ${day.page} · PDF</span></a></div>
      <details class="warmup"><summary><span><span class="warmup-icon" aria-hidden="true">${externalIcon}</span> Precalentamiento</span><span class="warmup-time">30 min <span aria-hidden="true">＋</span></span></summary><p>${escape(routine.warmup)}</p><p class="muted small">Indicación de la planilla original del gimnasio.</p></details>
      <div class="session-tools"><div><p id="progress-label" class="progress-label" aria-live="polite"></p><progress id="progress" max="${day.exercises.length}" value="0" aria-label="Ejercicios marcados como hechos"></progress><p class="small muted" id="save-status"></p></div><div class="session-actions"><button class="text-button" id="pause-all">${globalPaused ? 'Reanudar demostraciones' : 'Pausar demostraciones'}</button><button class="text-button" id="reset-day">Reiniciar día</button><button class="text-button" id="undo-reset" hidden>Deshacer reinicio</button></div></div>
      <nav class="exercise-index" aria-label="Ir a un ejercicio"><ol>${day.exercises.map((e, i) => `<li><a href="#${e.id}"><span>${String(i + 1).padStart(2, '0')}</span>${escape(e.name)}</a></li>`).join('')}</ol></nav>
      <ol class="exercise-list">${day.exercises.map((e, i) => exerciseHTML(e, i, completed.has(e.id))).join('')}</ol>
      <div class="session-end"><p id="finish-status" aria-live="polite"></p><a class="button" href="${routine.days[day.number] ? address(routine, routine.days[day.number]) : '?'}" data-route>${routine.days[day.number] ? 'Ver día siguiente →' : 'Volver a las rutinas →'}</a></div>
    </section>`;
  $('#routine-select').addEventListener('change', (event) => { const r = catalog.routines.find((r) => r.id === event.target.value); go(address(r, r.days[0])); });
  function updateProgress() {
    $('#progress').value = completed.size;
    $('#progress-label').textContent = `${completed.size} de ${day.exercises.length} ejercicios marcados`;
    $('#finish-status').textContent = completed.size === day.exercises.length ? 'Día marcado como completo. Buen trabajo.' : 'A tu ritmo. Marcá cada ejercicio cuando lo termines.';
    persist();
  }
  view.querySelectorAll('.done-control input').forEach((input) => input.addEventListener('change', () => {
    input.checked ? completed.add(input.value) : completed.delete(input.value);
    input.closest('.exercise').classList.toggle('is-done', input.checked);
    saved[stateKey] = [...completed]; updateProgress();
  }));
  $('#reset-day').onclick = () => {
    undo = [...completed]; completed.clear(); saved[stateKey] = [];
    view.querySelectorAll('.done-control input').forEach((input) => { input.checked = false; input.closest('.exercise').classList.remove('is-done'); });
    $('#undo-reset').hidden = false; updateProgress();
  };
  $('#undo-reset').onclick = () => {
    completed.clear(); (undo || []).forEach((id) => completed.add(id)); saved[stateKey] = [...completed];
    view.querySelectorAll('.done-control input').forEach((input) => { input.checked = completed.has(input.value); input.closest('.exercise').classList.toggle('is-done', input.checked); });
    $('#undo-reset').hidden = true; updateProgress();
  };
  $('#pause-all').onclick = () => {
    globalPaused = !globalPaused;
    $('#pause-all').textContent = globalPaused ? 'Reanudar demostraciones' : 'Pausar demostraciones';
    players.forEach((player) => player.refresh());
  };
  view.querySelectorAll('[data-player]').forEach((figure) => {
    const e = day.exercises.find((e) => e.id === figure.dataset.player);
    players.push(makePlayer(figure, library.mapping[e.key].map((id) => library.movements[id])));
  });
  updateProgress();
  if (focus) focusHeading('#workout-title');
}
function renderCatalog() {
  const results = catalog.routines.filter((r) => (category === 'todas' || r.category === category) && r.title.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().includes(search.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()));
  $('#catalog-count').textContent = `${results.length} ${results.length === 1 ? 'rutina disponible' : 'rutinas disponibles'}`;
  $('#routine-grid').innerHTML = results.length ? results.map((routine) => `<a class="routine-card" href="${address(routine, routine.days[0])}" data-route><div class="card-top"><span class="category">${routine.category === 'adaptacion' ? 'ADAPTACIÓN' : escape(routine.category.toUpperCase())}</span><span class="arrow" aria-hidden="true">${externalIcon}</span></div><h3>${routine.category === 'adaptacion' ? 'Tu punto de partida' : `Rutina ${routine.title.match(/\d+/)[0]}`}</h3><p>${routine.category === 'adaptacion' ? 'Para hombres y mujeres' : 'Seguí el plan que te asignó el entrenador'}</p><div class="card-bottom"><span>${routine.category === 'adaptacion' ? '1 sesión' : `${routine.days.length} días`}</span><span>Ver rutina →</span></div></a>`).join('') : '<div class="empty"><h3>No encontramos esa rutina</h3><p>Probá otro nombre o elegí “Todas”.</p></div>';
}
function prescriptionHTML(raw) {
  const simple = raw.trim().match(/^(\d+)\s*[xX×]\s*(\d+)\.?$/);
  if (simple) return `<div><span>Series</span><strong>${simple[1]}</strong></div><div><span>Repeticiones</span><strong>${simple[2]}</strong></div>`;
  const normalized = raw.trim().replace(/[–−]/g, '-').replace(/\.$/, '');
  let series = null;
  if (/^\d+(?:\s*-\s*\d+)+$/.test(normalized)) series = normalized.split(/\s*-\s*/);
  if (/^\d+\s*[xX×]\s*\d+(?:\s*-\s*\d+\s*[xX×]\s*\d+)+$/.test(normalized)) {
    series = normalized.split(/\s*-\s*/).flatMap((group) => { const [count, reps] = group.split(/\s*[xX×]\s*/); return Array(Number(count)).fill(reps); });
  }
  if (series) return `<div class="complex-dose"><span>${series.length} series · repeticiones en orden</span><strong>${series.map(escape).join(' · ')}</strong><small class="dose-help">Una serie con cada cantidad de repeticiones.</small></div>`;
  return `<div class="complex-dose"><span>Series y repeticiones · según planilla</span><strong>${escape(raw)}</strong></div>`;
}
function exerciseHTML(e, index, done) {
  const ids = library.mapping[e.key];
  const known = ids && ids.length;
  const movement = known ? library.movements[ids[0]] : null;
  return `<li><article class="exercise ${done ? 'is-done' : ''}" id="${e.id}" aria-labelledby="${e.id}-title">
    <header class="exercise-heading"><div class="exercise-name"><span class="number">${String(index + 1).padStart(2, '0')}</span><div><p class="eyebrow">${known && ids.length > 1 ? 'COMBINACIÓN · EN EL ORDEN DE LA PLANILLA' : 'EJERCICIO'} ${index + 1}</p><h3 id="${e.id}-title">${escape(e.name)}</h3></div></div><label class="done-control"><input type="checkbox" value="${e.id}" ${done ? 'checked' : ''} aria-label="Marcar ${escape(e.name)} como hecho"><span>Hecho</span></label></header>
    <div class="dose-strip">${prescriptionHTML(e.prescription)}<div class="rest"><span>Descanso</span><strong>${e.rest ? 'Sin descanso' : 'Consultar'}</strong><small>${e.rest ? 'Indicado en la planilla' : 'No indicado en la planilla'}</small></div></div>
    ${known ? `<div class="exercise-layout"><figure class="demonstration" data-player="${e.id}"><div class="visual-stage">${movement.video ? `<video muted loop playsinline preload="none" poster="${movement.poster}" aria-label="Demostración de ${escape(movement.title)}"></video>` : `<img src="${movement.frames[0]}" width="640" height="640" alt="${escape(movement.title)}: posición inicial" loading="lazy">`}</div><figcaption><span class="phase">Posición inicial</span><div class="player-controls"><button type="button" class="play-toggle" aria-label="Pausar demostración de ${escape(e.name)}">Pausar</button><button type="button" class="step-forward" aria-label="Ver la posición siguiente de ${escape(e.name)}">Paso siguiente →</button></div></figcaption><p class="media-error" role="status" hidden>No se pudo cargar la demostración. Consultá las indicaciones y volvé a intentar al recargar.</p></figure><div class="instructions">${ids.length > 1 ? `<label class="part-label">Movimiento de la combinación<select class="part-select" data-for="${e.id}">${ids.map((id, i) => `<option value="${i}">${i + 1}. ${escape(library.movements[id].title)}</option>`).join('')}</select></label>` : ''}<h4>Cómo hacerlo</h4><p class="movement-title">${escape(movement.title)}</p><ol class="movement-steps">${movement.steps.map((step) => `<li>${escape(step)}</li>`).join('')}</ol><p class="cue"><strong>Prestá atención</strong><span>${escape(movement.cue)}</span></p><p class="attribution small">${escape(movement.author)} · ${escape(movement.license)}<br><a href="creditos.html">Fuente y créditos ${externalIcon}</a></p></div></div>` : `<div class="pending-media"><span class="pending-icon" aria-hidden="true">${externalIcon}</span><div><h4>Demostración por completar</h4><p>La planilla indica “${escape(e.name)}”. Conservamos el ejercicio y su dosis; falta una secuencia que corresponda a esta variante.</p><p>Pedí al entrenador que te muestre el recorrido antes de hacerlo.</p></div></div>`}
    <details class="source-details"><summary>Ver indicación original · página ${e.page}</summary><p><strong>${escape(e.name)}</strong><br>Repeticiones: ${escape(e.prescription)}</p><a href="source/RUTINAS.pdf#page=${e.page}" target="_blank" rel="noopener">Abrir esta página del PDF ${externalIcon}</a></details>
  </article></li>`;
}

function makePlayer(figure, movements) {
  let part = 0, frame = 0, direction = 1, visible = false, ready = false, paused = false, manualPlay = false, timer = null, disposed = false;
  let loadVersion = 0;
  const toggle = $('.play-toggle', figure), next = $('.step-forward', figure), phase = $('.phase', figure);
  const video = $('video', figure);
  let img = $('img', figure);
  const article = figure.closest('.exercise');
  const partSelect = $('.part-select', article);
  const current = () => movements[part];
  const mayPlay = () => ready && visible && !document.hidden && !paused && !globalPaused && (!reduced.matches || manualPlay);
  function displayType() {
    if (video) return;
    const stage = $('.visual-stage', figure);
    stage.innerHTML = current().sprite ? '<div class="sequence-window"><img width="2172" height="724" alt=""></div>' : '<img width="640" height="640" alt="">';
    img = $('img', figure);
  }
  function showFrame() {
    const name = frame === 0 ? 'Inicio' : (frame === current().frames.length - 1 ? 'Final' : 'Recorrido');
    if (img) {
      img.src = current().frames[frame]; img.alt = `${current().title}: ${name.toLowerCase()}`;
      img.style.transform = current().sprite ? `translateX(-${frame * 100 / current().frames.length}%)` : '';
    }
    phase.textContent = video ? 'Movimiento en bucle' : `${frame + 1} / ${current().frames.length} · ${name}`;
  }
  function advance() {
    frame += direction;
    if (frame === current().frames.length - 1 || frame === 0) direction *= -1;
    showFrame();
  }
  async function load() {
    if (ready || disposed) return;
    const version = ++loadVersion;
    try {
      if (video) {
        if (!video.getAttribute('src')) { video.src = current().video; video.load(); }
      } else {
        await Promise.all(current().frames.map((src) => { const image = new Image(); image.src = src; return image.decode(); }));
      }
      if (disposed || version !== loadVersion) return;
      ready = true; $('.media-error', figure).hidden = true; refresh();
    } catch {
      if (!disposed) { $('.media-error', figure).hidden = false; toggle.disabled = true; next.disabled = true; }
    }
  }
  function refresh() {
    clearInterval(timer); timer = null;
    const playing = mayPlay();
    toggle.textContent = playing ? 'Pausar' : 'Reproducir';
    toggle.setAttribute('aria-label', `${playing ? 'Pausar' : 'Reproducir'} demostración de ${current().title}`);
    toggle.setAttribute('aria-pressed', String(playing));
    if (video) {
      if (playing) video.play().catch(() => { paused = true; refresh(); });
      else video.pause();
    } else if (playing) {
      timer = setInterval(advance, 1150);
    }
  }
  toggle.onclick = () => {
    if (mayPlay()) { paused = true; }
    else { paused = false; manualPlay = true; if (globalPaused) { globalPaused = false; $('#pause-all').textContent = 'Pausar demostraciones'; players.forEach((player) => player.refresh()); } }
    load(); refresh();
  };
  next.onclick = () => {
    paused = true;
    if (video && Number.isFinite(video.duration)) video.currentTime = (video.currentTime + video.duration / 4) % video.duration;
    else if (img && ready) advance();
    refresh();
  };
  if (partSelect) partSelect.onchange = () => {
    part = Number(partSelect.value); frame = 0; direction = 1; ready = false; manualPlay = false;
    const m = current(); $('.movement-title', article).textContent = m.title;
    $('.movement-steps', article).innerHTML = m.steps.map((step) => `<li>${escape(step)}</li>`).join('');
    $('.cue span', article).textContent = m.cue;
    $('.attribution', article).innerHTML = `${escape(m.author)} · ${escape(m.license)}<br><a href="creditos.html">Fuente y créditos ${externalIcon}</a>`;
    displayType(); showFrame(); refresh(); load();
  };
  const observer = new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting && entries[0].intersectionRatio >= .2;
    if (visible) load();
    refresh();
  }, { threshold: [0, .2] });
  observer.observe(figure);
  const motionChange = () => { manualPlay = false; refresh(); };
  reduced.addEventListener('change', motionChange);
  document.addEventListener('visibilitychange', refresh);
  if (video) video.addEventListener('error', () => { $('.media-error', figure).hidden = false; });
  if (current().sprite) displayType();
  if (!video) showFrame();
  refresh();
  return { refresh, destroy() { disposed = true; loadVersion++; clearInterval(timer); if (video) { video.pause(); video.removeAttribute('src'); video.load(); } observer.disconnect(); reduced.removeEventListener('change', motionChange); document.removeEventListener('visibilitychange', refresh); } };
}

document.addEventListener('click', (event) => {
  const link = event.target.closest('a[data-route]');
  if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault(); go(link.getAttribute('href'));
});
window.addEventListener('popstate', () => {
  // Un ancla al ejercicio cambia el fragmento, no la rutina o el día.
  if (catalog && location.search !== renderedQuery) render(true);
});
$('#routine-search').addEventListener('input', (event) => { search = event.target.value; renderCatalog(); });
document.querySelectorAll('[data-category]').forEach((button) => button.onclick = () => {
  category = button.dataset.category;
  document.querySelectorAll('[data-category]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
  renderCatalog();
});
async function boot() {
  try {
    const data = await Promise.all(['data/routines.json', 'data/movements.json'].map(async (url) => {
      const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json();
    }));
    [catalog, library] = data;
    if (!Array.isArray(catalog.routines) || !library.mapping || !library.movements) throw new Error('Catálogo inválido');
    $('#loading').hidden = true; $('#catalog-view').hidden = false;
    render();
  } catch {
    $('#loading').hidden = true; $('#load-error').hidden = false;
  }
}
boot();
