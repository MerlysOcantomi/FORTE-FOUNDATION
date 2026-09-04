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

Un bloque nunca se borra del catálogo; se marca `deprecated`.

## Reglas de integridad

1. `id` único en todo el catálogo.
2. Todo `requires` y todo `extends` apunta a un `id` existente en el catálogo.
3. Una variante (`vertical:*`, `region:*`) declara `extends`, salvo los bloques raíz de la familia `regions`.
4. Un `candidate` no tiene `latest_version` ni `path`; cualquier otro estado tiene ambos.
5. `family` pertenece a la lista de familias definida en el propio catálogo y en el schema. Añadir una familia requiere ADR y cambio en los tres schemas.

Hasta que exista tooling propio, estas reglas se comprueban con un script ad hoc antes de cada PR (ver README).
