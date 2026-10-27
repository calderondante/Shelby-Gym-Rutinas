# QA de las rutinas reales · 27/10/2026

## Estado comprobado

14 rutinas, 40 días/sesiones, 301 entradas de la planilla, sin contar dos veces el
índice. **255 entradas tienen demostración; 46 apariciones, correspondientes a 36
nombres distintos, siguen sin secuencia correspondiente.** Esos ejercicios permanecen
visibles con dosis y fuente; no se sustituyen silenciosamente por otros.

La navegación y el desarrollo están operativos. El contenido visual completo y los
descansos generales todavía requieren cerrar REVISION_ENTRENADOR.md. No se presenta
la web como una entrega con todas las demostraciones terminadas.

## Cambios de interfaz

| Before | After | Motivo |
| --- | --- | --- |
| Una muestra de cuatro ejercicios | Catálogo del PDF, filtros, búsqueda, rutina y día compartibles por URL | Llegar al plan asignado sin registro |
| Dosis en HTML fijo | JSON con orden y página de origen; series simples y secuencias numéricas legibles | Mantener fidelidad y facilitar correcciones |
| GIF sin pausa | MP4 originales y visor secuencial con pausa y paso manual | Consultar la técnica con control del movimiento |
| Recursos siempre en bucle | Reproducción al entrar en pantalla y pausa fuera de ella o al ocultar pestaña | Evitar movimiento y trabajo innecesario |
| Sin seguimiento | Marcas locales, reinicio y deshacer; revisión de fuente separa avances viejos | Orientar durante la sesión sin cuentas ni DB |
| Demostraciones sin atribución nueva | Fuente por movimiento y página de créditos con licencia | Distinguir plan del gimnasio, fuente externa e ilustración nueva |

Las animaciones recorren las posiciones en ida y vuelta, sin interpolar cuerpos ni
equipos. Con movimiento reducido quedan quietas; la reproducción solo se inicia si
la persona la solicita. Se ve una única demostración por ejercicio, también en las
combinaciones, cuyo componente se elige mediante un selector.

## Verificaciones ejecutadas

- `python scripts/import-routines.py`: 14 rutinas, 40 sesiones, 301 dosis; ninguna línea
  desconocida ignorada. La importación conserva incluso dosis partidas entre páginas.
- `node scripts/check.mjs`: cantidades del PDF, nombres/páginas, dosis complejas
  representativas, correspondencias, archivos, fuentes, licencias y SVG sin contenido activo.
- `node --check public/app.js` y `git diff --check`: correctos.
- `python scripts/qa-browser.py`: navegación de las 40 sesiones, 301 nombres en orden,
  filtros (6 femeninas, 7 masculinas), búsqueda, estado vacío, marcado persistente,
  reinicio/deshacer, reproducción, pausa, paso manual, sprite de una posición por vez,
  pausa fuera de pantalla, movimiento reducido, combinación y MP4 sin sonido.
- Chromium a **375, 390, 768, 1024 y 1440 px**: sin overflow horizontal, medios de los
  recorridos probados decodificados, enlace de salto operable con teclado, sin errores JS.
- axe-core **4.11.0** en inicio, adaptación, un día con combinaciones y créditos:
  cero infracciones y cero comprobaciones incompletas bajo los tags WCAG A/AA 2/2.1/2.2
  incluidos por esa versión. No se presenta como certificación completa de WCAG.
- Casos adicionales: error al cargar JSON con alternativa PDF; almacenamiento bloqueado
  con avance de sesión explícito; selección y marcado con touch emulado en Chromium;
  dosis `20-15-12-10-8-6-4` presentada como siete series ordenadas.
- Revisión visual de las cinco anchuras en montaje, inicio y ejercicios en escritorio,
  controles e indicaciones en móvil, hojas de posiciones de Everkinetic y cada secuencia
  generada utilizada. Se corrigieron correspondencias y orden de posiciones detectados
  durante esa revisión. Tras la última corrección de medios se volvió a renderizar el
  tríceps con mancuerna de pie y se repitió la validación de archivos/datos.
- El checkout `/workspace/Shelby-Gym` conserva el árbol de trabajo sin cambios.

Resultados y capturas actuales: `docs/qa/current/`. Las capturas anteriores de
`docs/qa/` pertenecen a la extracción inicial, no a estas pruebas.

## Límites y publicación

No hay un build ni typecheck de framework: el sitio usa HTML/CSS/JavaScript estático,
sin dependencias de producción. Playwright y axe son herramientas de QA, fuera del
bundle. No se probaron lectores de pantalla, Safari/WebKit ni dispositivos Android o
iPhone físicos; WebKit no está instalado en el entorno. Touch y viewport son emulados.

La auditoría automática no valida la técnica deportiva ni completa instrucciones que
no existen en el PDF. Los descansos no escritos permanecen como «Consultar». Las
ilustraciones nuevas se revisaron visualmente y tienen procedencia diferenciada; no
se afirma una aprobación posterior del entrenador.

`netlify.toml` publica solo `public/`, sin el stack o variables del administrador.
No se crearon sitios remotos, commits nuevos de implementación, push ni despliegues.
La configuración de publicación no prueba una publicación en Netlify ni restauración
en una tarea nueva. El historial público filtrado y el trabajo actual están locales.

## Exportación para presentación

Se preparó un HTML autocontenido y un ZIP del sitio público mediante
`scripts/package-demo.py`. El HTML se renderizó con la red desconectada y se verificaron
catálogo, rutina/día, secuencias, pausa, marcado, video y enlaces al PDF embebido.
La política del navegador del entorno bloquea navegar a `file://`; se cargó el contenido
del HTML como documento para esa prueba, sin atribuirle una prueba directa de apertura
como archivo local. ZIP con CRC correcto, solo archivos públicos y cabeceras.

Se corrigió además la navegación a anclas para que cambiar de fragmento dentro de un
día no vuelva a renderizar la rutina ni devuelva el foco al título. Se comprobaron las
anclas y Atrás del navegador por separado. No se publicó una URL de Netlify ni se
modificó la administración para entregar esta presentación.
