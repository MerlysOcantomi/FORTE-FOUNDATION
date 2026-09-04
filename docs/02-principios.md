# Principios

Origen: handoff §2, §3, §4, §18, §37. Cada principio remite al ADR que lo fija.

## 1. Reutilización por copia, no por dependencia compartida

Los productos permanecen aislados. Foundation entrega bloques que se copian o generan dentro del repo de cada producto; a partir de ahí el producto posee y controla esa implementación. Una actualización de Foundation nunca rompe automáticamente un producto existente. → [ADR-0001](decisions/ADR-0001-reutilizacion-por-copia.md), [ADR-0002](decisions/ADR-0002-productos-aislados-sin-runtime-central.md).

```text
Foundation v4
       ↓ copia/versionado
7F        → posee su copia
Finesse   → posee su copia
Producto X → posee su copia
```

Lo que esto compra: independencia, actualización controlada, rollback, auditoría, versiones distintas por producto, personalización, menor blast radius y evolución de Foundation sin migraciones simultáneas.

## 2. Foundation no es un cajón de componentes

La pregunta no es "¿podemos reutilizar este código?" sino "¿esto representa una capacidad estable que varios productos necesitarán y cuya reutilización nos ahorra resolver de nuevo arquitectura, seguridad, edge cases y operación?". Un bloque entra con evidencia, no con expectativa. → [`06-criterios-de-admision.md`](06-criterios-de-admision.md), [ADR-0006](decisions/ADR-0006-crecimiento-incremental.md).

## 3. Crecimiento incremental desde productos reales

No se detienen los productos para construir un Foundation perfecto. La capacidad se construye bien en un producto, se valida en contexto real, se evalúa su generalización y solo entonces se extrae. Foundation emerge de necesidades reales con arquitectura deliberada. → [ADR-0006](decisions/ADR-0006-crecimiento-incremental.md).

## 4. La IA selecciona; el código determinista garantiza

La IA (Mission Control) interpreta necesidades, elige bloques, propone configuración, analiza compatibilidad y genera adapters. El código determinista controla permisos, migraciones, schemas, constraints, validaciones, invariantes, retries, idempotencia y ejecución crítica. Todo bloque declara su `decision_mode`. → [ADR-0003](decisions/ADR-0003-seleccion-automatica-por-mission-control.md), [`spec/block.md`](../spec/block.md).

## 5. Región separada de idioma

`market` y `locale` son dimensiones distintas. España, Suiza, Alemania y Estados Unidos comparten funciones pero difieren en pagos, facturación, fiscalidad, infraestructura y formatos. → [ADR-0004](decisions/ADR-0004-region-separada-de-locale.md), [`04-regionalizacion.md`](04-regionalizacion.md).

## 6. Todo bloque tiene versión y procedencia

Semver por bloque, manifest por producto. Mission Control siempre puede saber qué producto usa qué bloque en qué versión y si lo personalizó. → [ADR-0005](decisions/ADR-0005-versionado-semver-y-manifest.md).

## 7. Providers intercambiables

Cuando existe una abstracción razonable, la capacidad de dominio no se acopla a un proveedor concreto. Foundation aporta interfaz, contrato, errores, tests y adapters; el producto elige provider. → [ADR-0008](decisions/ADR-0008-providers-intercambiables.md).

## 8. CI por defecto; el resto según perfil

Todo producto serio recibe una red mínima de seguridad (install → lint → typecheck → build → tests). Capacidades como Recovery se seleccionan solo cuando el perfil del producto lo justifica. → [ADR-0007](decisions/ADR-0007-ci-por-defecto-recovery-opcional.md).

## 9. Los secretos nunca viven en Foundation

Los bloques solo nombran variables; los valores viven en la gestión de secretos por producto y entorno. Nada de secretos en prompts, commits ni logs.

## Qué queremos evitar

| Anti-patrón | Por qué es peligroso |
|-------------|----------------------|
| **Mega monolito compartido** | Un fallo en Foundation rompe todos los productos a la vez. |
| **Duplicación descontrolada** | Copiar sin saber origen, versión ni diferencias. Por eso existe el manifest. |
| **Selección manual repetitiva** | Marcar veinte módulos a mano en cada producto nuevo. Por eso selecciona Mission Control. |
| **Sobregeneralización** | Convertir en Foundation algo que solo sirve a un producto. |
| **Abstracciones prematuras** | Construir frameworks internos antes de tener evidencia real. |
| **Actualizaciones globales peligrosas** | Cambiar Foundation y romper productos existentes sin PR ni revisión. |
