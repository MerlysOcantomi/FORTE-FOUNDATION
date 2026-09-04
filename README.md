# Forte Foundation

Biblioteca interna de **bloques reutilizables y versionados** del ecosistema Forte. Un bloque es una capacidad resuelta bien una vez (auth, workspace, CI, recovery, facturación española...) que Mission Control **copia** en cada producto con procedencia registrada. Ningún producto depende de Foundation en runtime.

## Qué es y qué no es

| Es | No es |
|----|-------|
| La base reutilizable con la que se construyen Mission Control, 7F, Finesse, SKINA, ProSound y futuros productos. | Un producto que use un cliente final. |
| Bloques con código, contratos, patrones, schemas, templates, tests, políticas, migraciones y guías de integración. | 7F, Mission Control ni SKINA. |
| Un lenguaje común (catálogo, descriptor, manifest) para que Mission Control seleccione y copie bloques. | Una librería o paquete compartido en runtime. |
| Algo que crece desde productos reales. | Un cajón donde va todo lo reutilizable. |

## Principio central

**Reutilización por copia controlada, no por dependencia compartida.** Foundation entrega bloques versionados; Mission Control los copia al repo del producto; el producto posee su copia y la registra en su `foundation.manifest.yaml`. Una actualización de Foundation nunca rompe un producto por sí sola. Detalle en [`docs/02-principios.md`](docs/02-principios.md).

```text
Forte Foundation                Mission Control                 Producto
  auth@3.2.0        ──►  entiende el producto      ──►   copia en su repo
  workspace@2.1.0   ──►  consulta el catálogo      ──►   foundation.manifest.yaml
  ci@1.0.0          ──►  selecciona y explica      ──►   posee su versión
  region-es@1.3.0
```

## Cómo se usa

Quien usa Foundation es **Mission Control**, no una persona marcando módulos a mano:

1. Infiere el perfil del producto (tipo, mercado, idioma, moneda, vertical).
2. Lee [`registry/catalog.yaml`](registry/catalog.yaml) y selecciona bloques, versiones y variantes (vertical, región), incluidos los marcados `default_for: all-products`.
3. Copia cada bloque siguiendo su `integration.md`, ejecuta sus tests y registra la entrada en el manifest del producto ([`spec/manifest.md`](spec/manifest.md)).
4. Explica la selección; Merlys revisa o corrige.

Ejemplo de manifest resultante: [`examples/finesse-es.foundation.manifest.yaml`](examples/finesse-es.foundation.manifest.yaml).

## Cómo se añade un bloque

Un bloque entra cuando un producto real lo necesita y supera los siete [criterios de admisión](docs/06-criterios-de-admision.md). Se registra como `candidate` en el catálogo, se extrae a `blocks/<id>/` a partir de [`blocks/_template/`](blocks/_template/block.yaml) como `draft`, y llega a `stable` cuando tiene tests independientes, guía de integración y al menos un producto que lo usa. Todo por PR a `main`.

## Mapa del repositorio

```text
README.md                      este archivo
docs/
  00-handoff.md                handoff original (histórico, no normativo)
  01-vision.md … 07-glosario.md  visión, principios, relaciones, regionalización,
                               versionado, criterios de admisión, glosario
  decisions/                   ADRs (normativos)
spec/
  block.md · manifest.md · catalog.md    especificaciones (normativas)
  schemas/                     JSON Schemas de block.yaml, manifest y catálogo
registry/catalog.yaml          inventario vigente de bloques y su estado
blocks/
  README.md                    vacío por diseño
  _template/                   plantilla de bloque
examples/                      manifest de ejemplo (Finesse, España)
```

## Fuente de verdad

La autoridad sobre cómo funciona Foundation es, en este orden: [`docs/decisions/`](docs/decisions/README.md) (ADRs) + [`spec/`](spec/block.md) + [`spec/schemas/`](spec/schemas/block.schema.json) + el estado actual de [`registry/catalog.yaml`](registry/catalog.yaml). El [handoff](docs/00-handoff.md) es un snapshot histórico; si lo contradicen, ganan ellos.

## Estado actual

- Visión, principios y ocho decisiones de arquitectura fijadas.
- Formatos de bloque, manifest y catálogo especificados y validables por schema.
- Catálogo con las capacidades candidatas identificadas, todas en estado `candidate`.
- **Cero bloques implementados.** El primer bloque previsto es `ci` ([ADR-0007](docs/decisions/ADR-0007-ci-por-defecto-recovery-opcional.md)).
- Sin tooling propio todavía. Hasta que exista, valida los YAML contra los schemas antes de abrir un PR (por ejemplo con Python `jsonschema` + `pyyaml`).

## Reglas de trabajo

- Todo cambio entra por PR a `main` con revisión.
- Identificadores en inglés (ids, campos, carpetas); prosa en español.
- Fechas y hashes de commit siempre entre comillas en YAML.
- Nunca secretos ni valores de configuración de un producto en este repositorio.
