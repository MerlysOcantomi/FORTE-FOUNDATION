# ADR-0006: Foundation crece incrementalmente desde productos reales

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §4, §7, §8, §21, §37.D, §37.E, §38, §44, §45

## Contexto

El riesgo opuesto al monolito es el framework prematuro: dedicar meses a construir Foundation sin productos, generalizar cosas que solo sirven a un producto y crear veinte carpetas vacías por familia. El handoff identifica muchas capacidades candidatas (auth, workspace, calendar, CI, recovery...) pero ninguna está implementada como bloque.

## Decisión

1. Foundation no se construye por adelantado. Una capacidad entra cuando un producto real la necesita, se construye bien allí, se valida en contexto y supera los siete criterios de admisión ([`docs/06-criterios-de-admision.md`](../06-criterios-de-admision.md)).
2. El catálogo ([`registry/catalog.yaml`](../../registry/catalog.yaml)) registra los candidatos como `candidate`, sin versión ni carpeta, para que Mission Control pueda razonar sobre ellos sin fingir que existen.
3. Ciclo de vida: `candidate` → `draft` → `stable` → `deprecated`, con requisitos de entrada definidos en [`spec/catalog.md`](../../spec/catalog.md).
4. Las familias son un campo del catálogo, no una estructura de carpetas. Solo existe `blocks/<id>/` cuando hay implementación. No se crean directorios `core/`, `capabilities/`, `providers/`, `regions/` ni `operations/`.
5. Fuera del alcance mientras no haya evidencia que lo pida: interfaz web de Foundation, base de datos, API, dashboard, motor de dependencias, agente Foundation, generador completo, publicación npm, paquete compartido.
6. El bootstrap inicial es documentación, decisiones, especificaciones, schemas, catálogo y plantilla. Cero bloques implementados. El primer bloque es `ci` ([ADR-0007](ADR-0007-ci-por-defecto-recovery-opcional.md)).

## Consecuencias

- Foundation empieza siendo un lenguaje común para describir bloques, no una librería. Eso es deliberado.
- Cada bloque llega con evidencia de uso real, lo que reduce sobregeneralización.
- Habrá periodos en los que el catálogo tenga muchos candidatos y pocos bloques; es el estado esperado, no una deuda.

## Alternativas rechazadas

- **Construir todos los candidatos del handoff antes de usarlos**: seis meses sin productos reales (§45).
- **Crear la estructura de carpetas conceptual de §21 como esqueleto**: carpetas vacías que invitan a rellenar sin evidencia; el propio handoff dice que no es una especificación.
