# <Nombre del bloque>

> Plantilla. Sustituye este contenido al crear `blocks/<id>/`.

## Qué resuelve

Una o dos frases: la capacidad, el problema que evita resolver de nuevo y qué productos la necesitan.

## Qué NO resuelve

Límites explícitos. Lo que sigue siendo responsabilidad del producto (UX, semántica de sector, configuración local).

## Contenido del bloque

| Ruta | Tipo | Descripción |
|------|------|-------------|
| `block.yaml` | descriptor | Identidad, versión, compatibilidad, procedencia |
| `integration.md` | integration-guide | Cómo copiarlo e integrarlo en un producto |
| `tests/` | test | Cómo se prueba de forma independiente |
| `...` | code / contract / schema / ... | |

## Invariantes

Lista de invariantes que el bloque garantiza y que el producto no debe romper al personalizar.

## Variantes

- `core`: ...
- `vertical:<nombre>`: ...
- `region:<código>`: ...

## Personalización permitida

Qué puede cambiar el producto sin perder la posibilidad de recibir upgrades razonables.

## Procedencia

Producto de origen, fecha, decisión (ADR) que justificó la promoción a Foundation.
