# Especificación: `foundation.manifest`

**Normativo.** Schema: [`schemas/manifest.schema.json`](schemas/manifest.schema.json). Ejemplo: [`examples/finesse-es.foundation.manifest.yaml`](../examples/finesse-es.foundation.manifest.yaml). Decisión: [ADR-0005](../docs/decisions/ADR-0005-versionado-semver-y-manifest.md).

## Propósito

El manifest vive en la raíz del repositorio de **cada producto** (nombre de archivo: `foundation.manifest.yaml`). Registra qué bloques de Foundation se copiaron, en qué versión, desde qué commit y si el producto los modificó. Es la pieza de **provenance**: sustituye a la dependencia runtime como forma de saber qué usa cada producto.

Con él Mission Control puede responder:

- ¿Qué versión de `ci` utiliza Finesse?
- ¿Qué productos usan `appointments@2`?
- ¿Qué producto tiene una copia personalizada que un upgrade no puede tocar a ciegas?
- ¿Quién necesita actualizarse cuando sale `auth@4`?

## Estructura

```yaml
manifest_version: 1
product: finesse                      # id kebab-case del producto
repo: MerlysOcantomi/FINESSE

profile:                              # perfil que Mission Control usa para inferir bloques
  type: vertical                      # saas | platform | vertical | internal-tool | portal | agent
  platform: 7f                        # opcional: plataforma base si es un vertical
  vertical: beauty                    # opcional
  market: ES                          # país/mercado (ISO 3166-1 alpha-2, EU o GLOBAL)
  locale: es-ES                       # idioma, independiente del mercado
  currency: EUR                       # ISO 4217

foundation:                           # opcional: de dónde se copió
  repo: MerlysOcantomi/FORTE-FOUNDATION
  catalog_commit: "<sha>"

blocks:
  - id: ci
    version: 1.0.0
    variant: core
    copied_at: "2026-09-04"
    source_commit: "<sha de Foundation>"
    customized: false
    path: .github/workflows/ci.yml    # opcional: dónde vive la copia en el producto
    notes: ...                        # opcional
```

## Campos de cada entrada de `blocks`

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `id` | sí | Id del bloque en el catálogo. |
| `version` | sí | Versión copiada (semver). |
| `variant` | sí | Variante copiada (`core`, `vertical:beauty`, `region:es`...). |
| `copied_at` | sí | Fecha de copia, entre comillas. |
| `source_commit` | sí | Commit de Foundation de origen, entre comillas. |
| `customized` | sí | `true` si el producto modificó la copia. |
| `path` | no | Ruta de la copia dentro del producto. |
| `notes` | no | Qué se personalizó y por qué. |

## Reglas

1. **Una entrada por bloque copiado**, incluidas las variantes (el core y su adapter son entradas separadas).
2. `market` y `locale` son campos distintos a propósito ([ADR-0004](../docs/decisions/ADR-0004-region-separada-de-locale.md)).
3. `customized: true` obliga a revisión humana en cualquier upgrade de ese bloque, sea cual sea el tipo declarado en el CHANGELOG.
4. El manifest se actualiza en el mismo commit en que se copia o actualiza un bloque. Un bloque copiado sin entrada en el manifest es duplicación descontrolada (§37.B del handoff).
5. El manifest no contiene secretos ni configuración de entorno.
6. `manifest_version` permite evolucionar el formato; un cambio incompatible incrementa el número y se documenta en un ADR.

## Flujo de upgrade (resumen)

```text
Foundation publica auth@4.0.0
        ↓
Mission Control lee los manifests de los productos
        ↓
detecta: finesse usa auth@3.2.0, customized: false
        ↓
lee el CHANGELOG: upgrade "asistido"
        ↓
crea rama, aplica migración, ejecuta tests
        ↓
PR → revisión → aprobación → actualiza manifest
```

Nunca se actualiza un producto sin PR ni sin actualizar su manifest.
