# Inspección inicial · 27/10/2026

Informe histórico de la extracción anterior al PDF. Para el estado actual ver QA_ACTUAL.md y README.md.

## Origen y separación

- Rama predeterminada remota: `gh-pages`, HEAD inspeccionado `b2f9d60`.
- Muestra pública: `rutinas/index.html`, `rutinas/style.css`, `rutinas/images/`.
- Sin AGENTS.md ni manifiesto de paquetes en gh-pages. Se leyeron AGENTS.md,
  README, diseño, skills pertinentes y configuración Netlify desde origin/main.
- `main` aloja la administración Next.js/Supabase y su despliegue Netlify; no se
  traslada su stack, plugin, funciones ni variables al sitio público.
- La muestra se publicaba en GitHub Pages según README; no se verificó configuración
  de la cuenta remota por API. No se modificó ningún despliegue.
- Historial público: un commit original, `26928e5`, filtrado como `76d3163` al
  retirar todo lo ajeno a rutinas. No hay `gestion`, `.env`, Supabase ni funciones
  administrativas entre los objetos alcanzables del destino.
- Destino local: `/workspace/Shelby-Gym-Rutinas`, origin ya apunta a
  `https://github.com/calderondante/Shelby-Gym-Rutinas.git`, rama main.
  No se hizo push ni se crearon nuevos commits de implementación.

## Qué se recupera

HTML y CSS ligeros, identidad negra/roja/blanca, logo del perro recortado desde
una captura, cuatro guías con instrucciones y dosis de ejemplo, cuatro GIF y
doce cuadros WebP. Tras mover a public/, todo se verificó byte a byte contra el origen.
El sitio no consulta datos privados y funciona sin instalación de paquetes.

## Revisión de interfaz y próximos cambios

| Antes (muestra recuperada) | Después propuesto, pendiente de implementación | Motivo |
| --- | --- | --- |
| Una rutina de ejemplo, fija | Catálogo real por rutina y día con URL compartible | Encontrar el entrenamiento correcto |
| Datos dentro del HTML | Datos estructurados y validados separados de plantillas | Actualizar sin editar presentación |
| Series y repeticiones; sin descansos | Dosis y descansos tomados de las planillas | Completar el entrenamiento sin adivinar |
| GIF en bucle sin pausa | Una demostración con pausa, reproducción en pantalla y alternativa estática | Control de movimiento y consumo |
| GIF de cuatro poses | Mantener los originales útiles; evaluar video autorizado y continuo | MP4 no repara saltos anatómicos |
| Logo desde una captura | Conservar identidad; incorporar original cuando esté disponible | Mejor nitidez |

No hay imágenes duplicadas debajo de las demostraciones en el HTML actual.
Los WebP 02/03 son archivos adicionales sin uso visible; no hace falta borrarlos
para eliminar duplicaciones en pantalla.

## Comprobaciones ejecutadas

Chromium headless del entorno, mediante Playwright y servidor HTTP estático:

| Ancho CSS | HTTP | Overflow horizontal | Imágenes rotas tras carga | Ancla a ejercicio | Foco en salto al contenido | Movimiento reducido |
| --- | --- | --- | --- | --- | --- | --- |
| 375 | 200 | No | 0 | Correcta | Correcto | WebP estático |
| 390 | 200 | No | 0 | Correcta | Correcto | WebP estático |
| 768 | 200 | No | 0 | Correcta | Correcto | WebP estático |
| 1024 | 200 | No | 0 | Correcta | Correcto | WebP estático |
| 1440 | 200 | No | 0 | Correcta | Correcto | WebP estático |

Cuatro ejercicios y cuatro demostraciones por viewport, sin errores JavaScript.
Capturas y resultados de esta sesión se conservan en `docs/qa/`. Se revisó el montaje
visual de cabeceras móvil/desktop e instrucciones y una hoja de todos los cuadros GIF.
El TOML se validó con `tomllib`; la ruta de publicación existe y excluye documentación.
El checkout de origen conserva `git status --porcelain` vacío.

No hay scripts de lint, typecheck, build ni tests en la muestra original. Estas
comprobaciones validan la extracción, no el catálogo ni el futuro flujo de entrenar.
No se probaron Safari/WebKit, equipos Android/iPhone físicos, lectores de pantalla,
temporizadores ni una publicación Netlify. La auditoría completa WCAG sigue pendiente;
el bucle sin pausa es un problema conocido de accesibilidad de la muestra.

## GIF frente a MP4: experimento local

Conversión H.264, CRF 23, yuv420p, faststart, sin sonido y relleno a dimensiones pares.
No se alteraron ni sustituyeron los recursos originales. Los MP4 de prueba quedaron
en `/tmp/shelby-video-benchmark/`, fuera del sitio.

| Ejercicio | GIF (bytes) | MP4 (bytes) |
| --- | --- | --- |
| Flexión inclinada | 260339 | 90261 |
| Puente de glúteos | 176544 | 51829 |
| Remo con mancuerna | 365340 | 111498 |
| Sentadilla al banco | 262316 | 85800 |

Total: 1064539 → 339388 bytes, reducción aproximada del 68 %. MP4 ofrece control de
pausa nativo y menor transferencia; se debe verificar calidad y reproducción en
Safari/iOS y Chrome/Android antes de adoptarlo. La secuencia sigue teniendo cuatro
poses: la compresión no crea continuidad de cuerpo, equipo ni apoyos.

## Pendientes que bloquean el contenido completo

Recibir el archivo de Drive o habilitar su dominio y verificar acceso; confirmar si
abarca todas las rutinas y cómo se agrupan. Ver CONTENIDO.md. La aprobación del usuario
de los materiales existentes queda registrada en RECURSOS.md.
