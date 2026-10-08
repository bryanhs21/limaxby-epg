# EPG automático L1 MAX — sin VPS

Este proyecto genera un EPG XMLTV para L1 MAX usando la página oficial de Liga1 Te Apuesto como fuente de programación.

## Fuente

https://liga1.pe/fixture-y-resultados-del-clausura-liga1-te-apuesto-2026/

La página oficial publica las fechas y horas confirmadas de los partidos. Las fechas futuras que solo aparecen como tentativas y sin hora se ignoran hasta que tengan horario.

## Hora

El script trabaja con `America/Lima`, UTC-05:00.

Ejemplo:

`2026-10-08 13:00 Perú` → `20261008130000 -0500`

No se realiza una conversión incorrecta desde la hora del navegador.

## Canal XMLTV

ID: `l1max.pe`

```xml
<channel id="l1max.pe">
  <display-name lang="es">L1 MAX</display-name>
</channel>
```

## Automatización

GitHub Actions ejecuta `epg.py` cada 6 horas y actualiza `epg.xml`.

## Publicarlo con GitHub Pages

1. Crea un repositorio llamado `l1max-epg`.
2. Sube todos los archivos de este proyecto.
3. Ve a Settings → Pages.
4. Selecciona `Deploy from a branch`.
5. Selecciona `main` y `/ (root)`.
6. Guarda.
7. Tu EPG quedará en:

`https://TU-USUARIO.github.io/l1max-epg/epg.xml`

También puedes usar la URL Raw de GitHub.

## Nota

Esta versión genera la EPG de los partidos de Liga 1 que tienen fecha y hora publicadas. No inventa programas de estudio, repeticiones o contenido no publicado por la fuente.
