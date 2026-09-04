# ADR-0005: Semver por bloque y `foundation.manifest` por producto

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §31, §32, §33, §34, §37.B

## Contexto

Con reutilización por copia ([ADR-0001](ADR-0001-reutilizacion-por-copia.md)) no hay un lockfile de dependencias que diga qué usa cada producto. Sin un sustituto, la copia se convierte en duplicación descontrolada: nadie sabe el origen, la versión ni las diferencias, y los upgrades son imposibles de proponer.

## Decisión

1. Cada bloque tiene versión **semver** propia, aplicada al contrato que ve el producto. `MAJOR` cambia contrato o invariantes; `MINOR` añade compatiblemente; `PATCH` corrige. Formato en [`spec/block.md`](../../spec/block.md).
2. Cada versión declara en su CHANGELOG el tipo de upgrade: `automático`, `asistido` o `manual`.
3. Cada producto mantiene en la raíz de su repo un `foundation.manifest.yaml` ([`spec/manifest.md`](../../spec/manifest.md)) con una entrada por bloque copiado: `id`, `version`, `variant`, `copied_at`, `source_commit`, `customized`.
4. El manifest se actualiza en el mismo commit en que se copia o actualiza un bloque.
5. Los bloques declaran compatibilidad con `requires: { id: rango }`. Mission Control resuelve el grafo.
6. Un upgrade nunca es automático a nivel de producto: Mission Control detecta la versión antigua leyendo el manifest, analiza el CHANGELOG, crea rama, aplica migración, ejecuta tests y abre PR. `customized: true` fuerza revisión humana siempre.
7. Los formatos llevan su propia versión (`manifest_version`, `catalog_version`) para poder evolucionar sin romper productos.

## Consecuencias

- Mission Control puede responder qué productos usan qué bloque, detectar versiones antiguas, proponer upgrades y revisar seguridad.
- Cada bloque necesita CHANGELOG disciplinado; es parte del coste de promover algo a Foundation.
- Los manifests de los productos son datos que Mission Control debe poder leer; un índice cruzado de manifests es un follow-up natural, no parte del bootstrap.

## Alternativas rechazadas

- **Versionar Foundation como un todo** (`foundation@7`): obliga a actualizar bloques que no cambiaron y no permite versiones distintas por producto.
- **Registrar provenance solo en comentarios de código**: se pierde al editar y no es legible por máquina.
- **Dependencia runtime con lockfile**: contradice [ADR-0001](ADR-0001-reutilizacion-por-copia.md).
