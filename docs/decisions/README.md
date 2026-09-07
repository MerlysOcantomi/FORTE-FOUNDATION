# Decisiones de arquitectura (ADRs)

Los ADRs son **normativos**: junto con [`spec/`](../../spec/block.md), [`spec/schemas/`](../../spec/schemas/block.schema.json) y el estado actual de [`registry/catalog.yaml`](../../registry/catalog.yaml) forman la fuente de verdad vigente de Foundation. El handoff original ([`docs/00-handoff.md`](../00-handoff.md)) es histórico; si contradice a un ADR, gana el ADR.

## Índice

| ADR | Decisión | Estado |
|-----|----------|--------|
| [0001](ADR-0001-reutilizacion-por-copia.md) | Reutilización por copia controlada, no por dependencia compartida | aceptado |
| [0002](ADR-0002-productos-aislados-sin-runtime-central.md) | Productos aislados: sin librería runtime central | aceptado |
| [0003](ADR-0003-seleccion-automatica-por-mission-control.md) | La selección de bloques la hace Mission Control (IA) con invariantes deterministas | aceptado |
| [0004](ADR-0004-region-separada-de-locale.md) | Región (mercado) separada de locale (idioma) | aceptado |
| [0005](ADR-0005-versionado-semver-y-manifest.md) | Semver por bloque y `foundation.manifest` por producto | aceptado |
| [0006](ADR-0006-crecimiento-incremental.md) | Foundation crece incrementalmente desde productos reales | aceptado |
| [0007](ADR-0007-ci-por-defecto-recovery-opcional.md) | CI por defecto en todo producto; Recovery bajo demanda; CI es el primer bloque | aceptado |
| [0008](ADR-0008-providers-intercambiables.md) | Abstracciones de provider intercambiables | aceptado |

## Cuándo escribir un ADR

- Se añade, elimina o renombra una familia del catálogo.
- Cambia un formato normativo (`block.yaml`, manifest, catálogo) de forma incompatible.
- Un bloque pasa a `deprecated`.
- Se toma una decisión que afecta a cómo Mission Control selecciona, copia o actualiza bloques.
- Se descarta una alternativa que alguien volverá a proponer.

Un ADR no se edita para cambiar la decisión: se escribe uno nuevo que lo sustituye y el antiguo pasa a estado `sustituido por ADR-XXXX`.

## Plantilla

```markdown
# ADR-NNNN: Título en forma de decisión

- Estado: propuesto | aceptado | sustituido por ADR-XXXX
- Fecha: AAAA-MM-DD
- Origen: secciones del handoff, producto o PR donde surgió

## Contexto
Qué problema o fuerza motiva la decisión.

## Decisión
Qué decidimos, en presente y de forma verificable.

## Consecuencias
Qué gana y qué cuesta. Qué obliga a hacer a partir de ahora.

## Alternativas rechazadas
Qué se consideró y por qué no.
```
