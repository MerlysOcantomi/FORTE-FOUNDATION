# ADR-0001: Reutilización por copia controlada, no por dependencia compartida

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §2, §3, §37.A, §37.B

## Contexto

Foundation debe permitir reutilizar capacidades bien resueltas (auth, workspace, CI, recovery, facturación regional) en varios productos: Mission Control, 7F, Finesse, SKINA, ProSound y futuros SaaS. La forma habitual de hacerlo es una librería compartida que cada producto importa en runtime. Esa forma crea un único punto de fallo: un cambio o un error en la librería afecta a todos los productos a la vez y obliga a migraciones simultáneas.

## Decisión

Foundation reutiliza mediante **templates, scaffolds, bloques versionados y generación o copia controlada**. Mission Control selecciona un bloque, lo copia al repositorio del producto y a partir de ahí el producto posee y controla esa implementación. Toda copia queda registrada en el `foundation.manifest` del producto con bloque, versión y commit de origen ([ADR-0005](ADR-0005-versionado-semver-y-manifest.md)).

Una actualización de Foundation no modifica nunca un producto por sí sola.

## Consecuencias

- Independencia entre productos, actualización controlada, rollback, auditoría, versiones distintas por producto, personalización y menor blast radius.
- Foundation puede evolucionar sin obligar a migraciones simultáneas.
- El coste es que la propagación de mejoras no es automática: cada upgrade es una propuesta que pasa por rama, tests, PR y revisión en el producto.
- Es obligatorio mantener provenance; copiar sin manifest es duplicación descontrolada y está prohibido.

## Alternativas rechazadas

- **Librería o paquete npm central compartido en runtime**: blast radius total, migraciones forzadas. Rechazada ([ADR-0002](ADR-0002-productos-aislados-sin-runtime-central.md)).
- **Monorepo con todos los productos y Foundation**: acopla ciclos de release y despliegue; contradice repos independientes.
- **Copia manual sin registro**: barata al principio, imposible de auditar o actualizar después.
