# SECRETFLYING_MONITOR

Alerta por Telegram de las ofertas de secretflying.com/europe-flight-deals/ cuyo título menciona Barcelona, Valencia o Madrid.

## Cómo funciona
- `secretflying_monitor.py`: Python 3.13 + cloudscraper + BeautifulSoup. Cloudflare da 403 a `requests` a secas.
- launchd a las 9:00, 14:00 y 20:00: `~/Library/LaunchAgents/com.gerardo.secretflying.plist`. Tiene el token y el chat_id de Telegram: nunca versionarlo.
- Logs: `~/Library/Logs/secretflying.log` y `secretflying.err`.
- `seen.json` = `{url: última_fecha_iso}`, no se sube al repo. SecretFlying republica la misma URL con fecha nueva, por eso la dedup no va por URL sola.
- Repo: `kiwi8891/secretflying-monitor` (push por SSH, HTTPS no autentica).
- Para añadir ciudades: lista `CITIES`. El filtro mira todo el título, así que también casa con destinos ("London to Barcelona").

## Estado (2026-11-04)
Funciona de nuevo tras dos meses de fallo mudo. Verificado: ejecución real por launchd con exit 0, envío a Telegram aceptado, dedup y aviso de web rota (este último en simulación).

Cambios sin commit a fecha de hoy: `secretflying_monitor.py` y este `CLAUDE.md`.

## Qué falló (sep-nov 2026)
La web cambió las fechas a `Nov 4, 2026` (el parser esperaba el mes completo) y los títulos de `h2` a `h3`. El script descartaba todas las ofertas y escribía "Sin novedades" con exit 0, igual que un día normal. Última alerta real: 2026-09-09.

Por qué no se vio:
- launchd seguía en verde y el log parecía sano.
- "Sin novedades" significaba a la vez "no hay ofertas" y "no he podido leer ninguna".

Qué se cambió:
- Si la página no da ninguna oferta legible, lanza `LayoutChanged` y avisa por Telegram.
- Se aceptan los dos formatos de fecha y `h2` o `h3`.
- Si Telegram falla, el envío da error y la oferta no se marca como vista. Antes se marcaba igual y se perdía.
- Los títulos se escapan para el HTML de Telegram.

## Gotchas
- Para saber si funciona, no basta con el log: mirar la fecha más reciente en `seen.json` (es normal que tenga días, no meses) y si `fetch_deals` lee ofertas.
- Los `article` de publicidad no llevan fecha ni enlace: es normal que se salten.
- La portada solo trae unas 9 ofertas (día y medio). Con el Mac apagado varios días se pierden las intermedias. Sin resolver: se podría leer también la página 2.
- Errores de red ocasionales en `.err` (12 hasta oct-2026): no son graves, se reintenta en la siguiente pasada. El timeout subió de 15 a 30 s.

## Siguiente sesión empieza por
Hacer commit y push si siguen pendientes, y comprobar que `seen.json` tiene alguna oferta posterior a 2026-11-04.
