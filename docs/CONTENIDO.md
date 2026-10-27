# Fuente de las rutinas

El usuario aportó `RUTINAS.pdf` en esta conversación y confirmó la aprobación del
material del gimnasio. El archivo se conserva en `public/source/RUTINAS.pdf`.
Su texto extraído está en `docs/source/RUTINAS.txt`; el importador produce
`public/data/routines.json`.

Documento: 38 páginas, 14 rutinas (adaptación, 6 femeninas y 7 masculinas),
40 días/sesiones, 301 entradas y 187 nombres escritos de maneras distintas.
Se importaron las 301 indicaciones de repeticiones, una sola vez cada una.

Se conservan nombres, orden, combinaciones, series descendentes, observaciones
incluidas en las dosis y página de procedencia. El índice del PDF no se importa como
contenido duplicado. Una dosis que comienza en la página siguiente se asocia a su
mismo ejercicio.

La interfaz separa series y repeticiones simples y explica secuencias numéricas
sin modificar el JSON literal. No se infieren pesos, descansos, niveles, objetivos,
días de la semana ni variantes que no aparecen en el documento. La clasificación
masculina/femenina se conserva como nombre de origen y no se usa para restringir acceso.

El PDF no define descansos generales. Un remo indica expresamente `s/descanso`,
que se muestra como tal. Las demás entradas indican que debe consultarse al entrenador.
Las preguntas todavía abiertas están en REVISION_ENTRENADOR.md.

Las indicaciones técnicas y demostraciones son una capa separada del PDF, con fuente
identificada en la biblioteca. No se atribuyen al entrenador textos de terceros o
ilustraciones nuevas. La aprobación del PDF no se usa como prueba de revisión humana
posterior de cada recurso nuevo.
