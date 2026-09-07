# Bloques

Esta carpeta está **vacía por diseño**. Contiene únicamente [`_template/`](_template/block.yaml), la plantilla que se copia a `blocks/<id>/` cuando un bloque pasa de `candidate` a `draft`.

Ningún bloque del catálogo tiene implementación todavía. Eso es deliberado ([ADR-0006](../docs/decisions/ADR-0006-crecimiento-incremental.md)): un bloque entra cuando un producto real lo necesita y supera los [criterios de admisión](../docs/06-criterios-de-admision.md), no para rellenar Foundation.

## Cuándo aparece el primer bloque

El primer bloque previsto es **`ci`** ([ADR-0007](../docs/decisions/ADR-0007-ci-por-defecto-recovery-opcional.md)): una plantilla de integración continua adaptable al stack (install → lint → typecheck → build → tests). Es pequeño, de bajo riesgo y permite probar por primera vez el ciclo completo:

```text
crear bloque → copiar a un producto → registrar en foundation.manifest
      → provenance → adaptar → validar
```

## Cómo se crea un bloque

1. Confirmar que existe como `candidate` en [`registry/catalog.yaml`](../registry/catalog.yaml) y que cumple los siete criterios.
2. Copiar `_template/` a `blocks/<id>/` y rellenar `block.yaml`, `README.md`, `integration.md`, `CHANGELOG.md` y `tests/`.
3. Validar `block.yaml` contra [`spec/schemas/block.schema.json`](../spec/schemas/block.schema.json).
4. Actualizar el catálogo: `status: draft`, `latest_version`, `path`.
5. Abrir PR a `main` con la evidencia de uso real.

Estructura y campos: [`spec/block.md`](../spec/block.md).
