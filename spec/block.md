# Especificación: bloque de Foundation

**Normativo.** Schema: [`schemas/block.schema.json`](schemas/block.schema.json). Plantilla: [`blocks/_template/`](../blocks/_template/block.yaml). Decisiones que lo justifican: [ADR-0001](../docs/decisions/ADR-0001-reutilizacion-por-copia.md), [ADR-0005](../docs/decisions/ADR-0005-versionado-semver-y-manifest.md).

## Qué es un bloque

Un bloque es la unidad de reutilización de Foundation: una capacidad resuelta una vez, empaquetada con su descriptor, su guía de integración, sus tests y su historial de versiones, lista para ser **copiada** a un producto. Un bloque no se importa en runtime desde Foundation; el producto posee su copia.

Un bloque puede contener código, contratos, patrones, schemas, templates, tests, políticas, configuración, documentación, migraciones, generadores o guías de integración. El campo `kind` declara qué contiene.

## Anatomía de `blocks/<id>/`

```text
blocks/<id>/
  block.yaml        descriptor (obligatorio, validado contra el schema)
  README.md         qué resuelve, qué no, invariantes, variantes, personalización
  CHANGELOG.md      historial por versión y tipo de upgrade
  integration.md    pasos para copiar e integrar en un producto
  tests/            cómo se prueba de forma independiente
  ...               contenido del bloque (código, schemas, templates...)
```

Solo existe carpeta cuando el bloque tiene implementación (`status` distinto de `candidate`). Los candidatos viven únicamente en [`registry/catalog.yaml`](../registry/catalog.yaml).

## Campos de `block.yaml`

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `id` | sí | Identificador kebab-case en inglés. Inmutable una vez publicado. |
| `name` | sí | Nombre legible. |
| `version` | sí | Semver `MAJOR.MINOR.PATCH`. Ver reglas abajo. |
| `family` | sí | Una de: `core`, `capabilities`, `providers`, `patterns`, `operational-safety`, `persistence`, `platform`, `regions`, `templates`, `testing`. |
| `kind` | sí | Lista de tipos de contenido: `code`, `contract`, `pattern`, `schema`, `template`, `test`, `policy`, `config`, `docs`, `migration`, `generator`, `integration-guide`. |
| `status` | sí | `candidate` → `draft` → `stable` → `deprecated`. Ver [catalog.md](catalog.md). |
| `description` | sí | Una frase. |
| `variant` | sí | `core`, `vertical:<nombre>`, `region:<código>`, `region:global` o `region:eu`. |
| `extends` | si variante | Id del bloque base que esta variante especializa. |
| `requires` | no | Mapa `id → rango semver`. Compatibilidad entre bloques. |
| `provides` | no | Capacidades o contratos que aporta. |
| `providers` | no | Solo bloques de abstracción de provider: adapters disponibles. |
| `decision_mode` | sí | `deterministic`, `ai` o `mixed`. Ver abajo. |
| `default_for` | sí | `all-products` o `on-demand`. |
| `origin` | no | `product`, `date`, `notes`: dónde se resolvió por primera vez. |
| `integration` | no | Ruta a la guía de integración. |
| `tests` | no | Ruta a los tests o a su descripción. |
| `owners` | no | Responsables. |
| `notes` | no | Texto libre. |

Convención YAML: fechas y hashes de commit siempre entre comillas (`"2026-09-04"`, `"a1b2c3d"`) para que ningún parser los convierta en tipos nativos.

## Versionado

Semver aplicado al **contrato que el producto ve**, no a la implementación interna:

- `PATCH`: corrección sin cambio de contrato ni de configuración. Upgrade automático.
- `MINOR`: nueva capacidad compatible. Upgrade automático o asistido.
- `MAJOR`: cambio de contrato, de schema o de invariantes. Upgrade asistido o manual, con migración documentada en el CHANGELOG.

Cada entrada del CHANGELOG declara el tipo de upgrade (`automático`, `asistido`, `manual`). Mission Control usa esa etiqueta y el campo `customized` del manifest del producto para decidir si puede proponer el upgrade sin revisión humana.

## Variantes y composición

Un bloque `core` es global y no contiene semántica de sector ni de país. Las variantes lo especializan mediante `extends`:

```text
appointments            variant: core
appointments-beauty     variant: vertical:beauty   extends: appointments
appointments-es         variant: region:es         extends: appointments
```

El producto combina `core + vertical + región + UX propia`. Una variante nunca sustituye al core: lo requiere.

## `decision_mode`

Declara quién decide dentro del bloque:

- `deterministic`: el bloque encapsula invariantes verificables por código (permisos, migraciones, idempotencia, validaciones). Nunca delega en un LLM.
- `ai`: el bloque es una guía o un prompt para que un agente decida (p. ej. selección de bloques).
- `mixed`: la IA propone, el código verifica.

La selección **de** bloques es tarea de Mission Control (IA); los invariantes **dentro** de los bloques deben ser deterministas.

## `default_for`

- `all-products`: Mission Control lo incluye por defecto en todo producto serio salvo que se excluya explícitamente (p. ej. `ci`, `auth`, `workspace`).
- `on-demand`: solo cuando el perfil del producto lo requiere (p. ej. `recovery`, `region-ch`).

## Invariantes que todo bloque debe cumplir

1. Puede copiarse a un producto sin traer consigo el resto de Foundation.
2. Puede probarse aislado del producto.
3. No contiene secretos ni valores de configuración de un producto concreto; solo nombres de variables.
4. Documenta qué puede personalizar el producto sin perder la posibilidad de upgrade.
5. Su `id` no cambia nunca; un cambio de identidad es un bloque nuevo y el antiguo pasa a `deprecated`.
