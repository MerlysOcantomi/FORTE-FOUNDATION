# ADR-0004: Región (mercado) separada de locale (idioma)

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §19, §20, §36

## Contexto

Es tentador tratar la internacionalización como traducción. Pero España, Suiza, Alemania y Estados Unidos pueden compartir funciones e idioma parcialmente y aun así diferir en pagos, facturación, numeración, impuestos, consentimiento, retención, providers e infraestructura. Suiza usa varios idiomas con un mismo marco legal.

## Decisión

1. El perfil de producto y el manifest tienen dos campos independientes: `market` (país/mercado: `ES`, `CH`, `EU`, `GLOBAL`) y `locale` (idioma: `es-ES`, `de-CH`).
2. Los bloques regionales se identifican por país, con `variant: region:<código>`, nunca por idioma.
3. Las capas regionales se apilan por herencia declarada: `region-global` → `region-eu` → `region-es` → `region-es-invoicing`. El bloque global nunca se altera para satisfacer un país.
4. Un bloque `core` no contiene reglas de país ni de sector. Las reglas llegan por variantes `region:*` y `vertical:*` que declaran `extends`.
5. Mission Control selecciona las capas regionales a partir de `market`, no de `locale`.

## Consecuencias

- Un mismo producto puede cambiar de idioma sin cambiar de bloques regionales, y de mercado sin cambiar de idioma.
- Añadir un país nuevo significa añadir bloques `region-<código>` sin tocar el core.
- Requiere disciplina: lo que es legal o fiscal va a `regions`, lo que es texto va a locale.

## Alternativas rechazadas

- **Un único campo `language`**: confunde idioma y mercado; no puede expresar Suiza.
- **Reglas de país dentro del bloque core con `if market == ES`**: convierte el core en un monolito de casos especiales y rompe el aislamiento de variantes.
