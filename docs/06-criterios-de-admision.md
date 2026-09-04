# Criterios de admisión: cuándo algo entra en Foundation

Origen: handoff §4, §8, §38, §45. Decisión: [ADR-0006](decisions/ADR-0006-crecimiento-incremental.md). Ciclo de vida formal: [`spec/catalog.md`](../spec/catalog.md#ciclo-de-vida-de-un-bloque).

## La pregunta correcta

No preguntamos "¿podemos reutilizar este código?". Preguntamos:

> ¿Esto representa una capacidad estable que varios productos podrían necesitar y cuya reutilización nos ahorra resolver de nuevo arquitectura, seguridad, edge cases y operación?

## Patrón específico vs capacidad generalizable

| Específico (se queda en el producto) | Generalizable (candidato a Foundation) |
|--------------------------------------|-----------------------------------------|
| La UI exacta de "Mi Agenda" de Finesse | Appointment Engine |
| El copy de un recordatorio de cita | Reminder Engine |
| La configuración concreta de la base de datos de 7F | Postgres setup + migration safety |
| El flujo "Próxima clienta" | Customer Records + Recurring Jobs |

## Los siete criterios

Antes de promover una implementación a `draft`, responder **sí** a todos:

1. **¿Existe en más de un producto, o probablemente existirá?**
2. **¿Representa una capacidad real**, no un fragmento de código conveniente?
3. **¿Hay invariantes importantes** que merece la pena resolver una sola vez (seguridad, concurrencia, idempotencia, aislamiento)?
4. **¿Puede parametrizarse** sin convertirse en un framework inmanejable?
5. **¿El producto seguirá pudiendo personalizarla** después de copiarla?
6. **¿Puede versionarse** con un contrato identificable?
7. **¿Puede probarse de forma independiente** del producto?

Un "no" en cualquiera significa que todavía no es candidato, o que hay que replantear el corte.

## Proceso incremental

No se detienen los productos para construir un Foundation perfecto. El camino es siempre:

```text
producto necesita capacidad
        ↓
la construimos bien en el producto
        ↓
la validamos en contexto real
        ↓
evaluamos generalización (siete criterios)
        ↓
si merece Foundation: extraemos patrón/bloque
        ↓
Foundation crece
```

Evitar el escenario contrario: seis meses construyendo Foundation sin productos reales.

## Cómo se promueve un bloque (procedimiento)

1. **Candidato**: añadir o actualizar la entrada en [`registry/catalog.yaml`](../registry/catalog.yaml) con `status: candidate`, `origin` y `handoff_sections` o referencia al producto donde se identificó. Un PR pequeño.
2. **Draft**: copiar [`blocks/_template/`](../blocks/_template/block.yaml) a `blocks/<id>/`, rellenar `block.yaml` (versión `0.x`), README, integration.md, tests y CHANGELOG; actualizar el catálogo con `status: draft`, `latest_version` y `path`. El PR incluye la evidencia de los siete criterios y, si la decisión es estructural, un ADR.
3. **Stable**: versión `>=1.0.0`, tests independientes, guía de integración probada y al menos un producto con la entrada en su manifest.
4. **Deprecated**: ADR con sustituto y plan de migración. Nunca se borra del catálogo.

Todo cambio en Foundation entra por PR a `main` con revisión.

## Primer bloque previsto

`ci` ([ADR-0007](decisions/ADR-0007-ci-por-defecto-recovery-opcional.md)). Es pequeño, de bajo riesgo y permite probar por primera vez el ciclo completo: crear bloque → copiar → manifest → provenance → adaptar → validar.
