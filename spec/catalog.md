# Especificación: catálogo de bloques

**Normativo.** Archivo: [`registry/catalog.yaml`](../registry/catalog.yaml). Schema: [`schemas/catalog.schema.json`](schemas/catalog.schema.json). Decisión: [ADR-0006](../docs/decisions/ADR-0006-crecimiento-incremental.md).

## Propósito

El catálogo es el índice que Mission Control consulta para saber **qué bloques existen, en qué estado están y cómo se relacionan**. Es la única fuente vigente sobre el inventario de Foundation. Los candidatos viven aquí aunque no tengan implementación, para que la selección automática pueda razonar sobre necesidades futuras sin fingir que ya están resueltas.

## Estructura

```yaml
catalog_version: 1
updated_at: "AAAA-MM-DD"
families:            # definición de cada familia permitida
  core: { description: ... }
  ...
blocks:              # una entrada por bloque
  - id: ci
    name: Continuous Integration
    family: operational-safety
    status: candidate
    variant: core
    description: ...
    default_for: all-products
    decision_mode: deterministic
    origin: { product: forte-mission-control }
    handoff_sections: [26, 28]
```

Una entrada del catálogo es un **subconjunto** de `block.yaml`: lo necesario para descubrir y seleccionar. Cuando un bloque tiene implementación, `block.yaml` en `blocks/<id>/` es la fuente detallada y el catálogo añade `latest_version` y `path`.

## Familias

| Familia | Contenido |
|---------|-----------|
| `core` | Identidad y multi-tenancy: auth, workspace, roles, permisos, aislamiento. |
| `capabilities` | Capacidades de dominio generalizables con posibles variantes vertical/región. |
| `providers` | Abstracciones de proveedor: contrato + errores + tests + adapters. |
| `patterns` | Patrones arquitectónicos documentados que se copian como guía o esqueleto. |
| `operational-safety` | CI, recovery, retry, idempotencia, scheduler, health, observabilidad, backups, migraciones seguras. |
| `persistence` | Scaffolds de base de datos. Cada producto conserva su propia base de datos. |
| `platform` | Capacidades para construir y operar productos: secretos, entornos, configuración. |
| `regions` | Capas regionales por país/mercado, separadas del idioma. |
| `templates` | Scaffolds de producto o repositorio que combinan bloques. |
| `testing` | Utilidades y patrones de testing. |

Las familias son campos del catálogo, **no carpetas**. Solo `blocks/<id>/` existe como directorio, y solo cuando hay implementación.

## Ciclo de vida de un bloque

```text
candidate ──► draft ──► stable ──► deprecated
```

| Estado | Significado | Requisitos para entrar |
|--------|-------------|------------------------|
| `candidate` | Identificado como capacidad probable. Sin versión ni carpeta. | Aparecer en el catálogo con `origin` y descripción. |
| `draft` | Extraído de un producto real. Tiene carpeta, `block.yaml` y versión `0.x`. Puede cambiar de contrato. | Cumplir los 7 criterios de [`docs/06-criterios-de-admision.md`](../docs/06-criterios-de-admision.md). ADR o PR con evidencia. |
| `stable` | Contrato estable, versión `>=1.0.0`, tests independientes, guía de integración, usado por al menos un producto con entrada en su manifest. | PR revisado + al menos un manifest que lo referencia. |
| `deprecated` | Sustituido o retirado. Sigue en el catálogo para que los manifests antiguos resuelvan. | ADR indicando sustituto y plan de migración. |

Un bloque nunca se borra del catálogo; se marca `deprecated`. El schema liga estado y versión: `draft` exige `latest_version` `0.x` y `stable` exige `>=1.0.0`.

## Qué puede hacer Mission Control con cada estado

El estado decide si un bloque puede **copiarse** a un producto. `default_for` solo describe el perfil por defecto; nunca convierte un candidato en instalable.

| Estado | ¿Copiable a un producto? | Qué puede hacer Mission Control |
|--------|--------------------------|----------------------------------|
| `candidate` | **No, nunca.** | Recomendarlo, detectar que un producto lo necesita y proponer su extracción. Si un producto necesita la capacidad ya, se construye en el producto ([`docs/06-criterios-de-admision.md`](../docs/06-criterios-de-admision.md)). |
| `draft` | Sí, experimentalmente, con aprobación explícita en el PR del producto. | Copiarlo señalando que el contrato puede cambiar. |
| `stable` | Sí. | Seleccionarlo normalmente; los `default_for: all-products` entran por defecto. |
| `deprecated` | **No para una instalación nueva.** Una copia ya existente sigue siendo válida en su manifest mientras se prepara la migración. | Mantener las copias existentes y proponer la migración al sustituto indicado en su ADR. |

Dos preguntas distintas: **"¿puede Mission Control seleccionarlo para un producto nuevo?"** (solo `draft` y `stable`) y **"¿es válido en el manifest de un producto que ya lo tiene?"** (`draft`, `stable` y `deprecated`). `scripts/validate.py` aplica la segunda: rechaza un `candidate` en cualquier manifest y acepta un `deprecated` como copia existente. La prohibición de seleccionar `deprecated` pertenece a la lógica de selección nueva, no a la validación histórica. Los manifests de `examples/` quedan exentos de la regla de estado porque ilustran un estado futuro.

## Reglas de integridad

1. `id` único en todo el catálogo.
2. Todo `requires` y todo `extends` apunta a un `id` existente en el catálogo.
3. Toda variante (`vertical:*`, `region:*`) declara `extends`; la única excepción es `region:global`, raíz de la familia `regions`. Un bloque `core` no puede declararlo. El schema lo exige.
4. Un `candidate` no tiene `latest_version`, `path` **ni directorio en `blocks/`**: cualquier archivo bajo `blocks/<id>/` para un candidato es implementación invisible y se rechaza.
5. Cualquier otro estado tiene `latest_version` y `path`, y `path` es exactamente `blocks/<id>` con un `block.yaml` cuyo `id` coincide. Todo directorio de `blocks/` (salvo `_template`) corresponde a una entrada no candidate.
6. Todo `extends` aparece también en `requires` con un rango de versión.
7. `decision_mode` es obligatorio en toda entrada: los candidatos no tienen `block.yaml`, así que el catálogo es la única fuente de ese dato.
8. Un bloque implementado de la familia `providers` declara al menos un adapter en `providers`.
9. `stable` exige `latest_version >= 1.0.0` con precedencia SemVer real (`1.0.0-rc.1` no vale). Solo dígitos ASCII.
10. La entrada del catálogo y el `block.yaml` del bloque no divergen en los campos de selección (ver [`block.md`](block.md#invariantes-que-todo-bloque-debe-cumplir)).
11. `family` pertenece a la lista de familias definida en el propio catálogo y en el schema. Añadir una familia requiere ADR y cambio en los tres schemas.
12. Un archivo YAML con claves duplicadas es inválido; el validador no deja que la última ocurrencia sobrescriba en silencio a la anterior.

Las reglas que el schema no puede expresar las comprueba `scripts/validate.py`; ejecutarlo es obligatorio antes de abrir un PR (ver README). Sus pruebas viven en `scripts/test_validate.py`.
