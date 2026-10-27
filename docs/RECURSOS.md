# Recursos, correspondencias y permisos

## Shelby Gym original

Logo, cuatro GIF y doce WebP recuperados únicamente de `Shelby-Gym/rutinas/images/`,
commit `26928e586b39004cb1b1df5c797b675c70f67e2b`. El usuario confirmó aprobación y
verificación de este material. No se declara dominio público ni una licencia Creative Commons
para esos archivos. El logo sigue siendo el recorte CSS de la captura original.

Se usan el remo a un brazo y el puente de glúteos donde coinciden con la planilla,
convertidos a MP4 H.264 sin sonido para ofrecer pausa real. Los GIF originales se
conservan. Sentadilla al banco y flexión inclinada no se sustituyen por otros ejercicios
por parecido: se conservan como material de la muestra, fuera del catálogo real.

## Everkinetic

Fuente: https://github.com/everkinetic/data
Versión: `446bb9a3d0c3beb6b84f7c9d77dfc8af707a2ab6`.
Autor: Greg Priday / Everkinetic. Licencia **CC BY-SA 4.0**, copiada completa en
`public/licenses/everkinetic-CC-BY-SA-4.0.txt`. La web muestra atribución y enlace a los
créditos, con procedencia por movimiento en `public/data/movements.json`.

Se copiaron SVG o PNG existentes sin alterar sus píxeles/trazados. Las indicaciones se
adaptaron al español y se ofrecen bajo esa misma licencia. No se presupone que esta
licencia cubre el logo, las rutinas ni los recursos originales de Shelby.

Para regenerar los recursos con Git, Python y FFmpeg instalados:

```sh
git clone https://github.com/everkinetic/data.git /tmp/shelby-everkinetic
git -C /tmp/shelby-everkinetic checkout 446bb9a3d0c3beb6b84f7c9d77dfc8af707a2ab6
python scripts/prepare-media.py /tmp/shelby-everkinetic
node scripts/check.mjs
```

No hace falta ejecutarlo para arrancar ni desplegar: los medios preparados están en el
repositorio. `scripts/build.mjs` actualiza las correspondencias sin el checkout externo.

La revisión visual detectó discrepancias entre algunas descripciones de la biblioteca
y sus dibujos (por ejemplo, dorsalera al pecho representada a la nuca). No se usaron
esas correspondencias incorrectas. Se prepararon secuencias específicas para pecho,
nuca y abdominal corto con los pies en el piso. Las variantes de equipo no definidas
se registran para revisión y no se sustituyen silenciosamente.

## Ilustraciones nuevas

Se crearon hojas secuenciales mediante image_gen, con tres paneles cuadrados por
movimiento, manteniendo la misma persona, encuadre, apoyos y equipo. Se inspeccionaron
los paneles antes de integrarlos. El registro de originales está en
`docs/source/GENERATED_MEDIA.json`; los PNG originales permanecen en
`/workspace/generated_images`. En el sitio se usan versiones WebP optimizadas con
FFmpeg, conservando la hoja completa y sin inventar cuadros intermedios.

El visor recorta un panel por vez mediante CSS, recorre inicio → recorrido → final →
recorrido → inicio y permite pausa y avance manual. No se presenta como filmación
continua ni se interpola anatomía. La primera prensa horizontal generada se rechazó
porque el recorrido de la plataforma no acompañaba a las piernas; se corrigió y se
volvió a inspeccionar antes de usarla.

Estas ilustraciones no provienen del PDF. Su inspección visual en esta tarea no se
presenta como una nueva aprobación del entrenador ni como una prueba en dispositivos físicos.

## Frontend y skills

Se consultaron las Web Interface Guidelines oficiales de Vercel:
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
Pausa, movimiento reducido, carga diferida y controles accesibles se aplican sin
librerías de reproducción ni fuentes externas.

Se reutilizaron únicamente las skills `emil-design-eng` y `web-design-guidelines` del
origen; no se copiaron skills de administración, auth, DB o despliegue Next.
La licencia y autoría de Emil se conservan en THIRD_PARTY_NOTICES.md.
