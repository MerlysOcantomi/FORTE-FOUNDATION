# ADR-0007: CI por defecto en todo producto; Recovery bajo demanda; CI es el primer bloque

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §26, §27, §28, §29, §30; revisión del plan de bootstrap

## Contexto

La experiencia con Forte Mission Control identificó dos capacidades de una misma familia, Operational Safety, con perfiles de adopción distintos. CI (install → lint → typecheck → build → tests en cada PR) es una red mínima de seguridad que todo producto serio necesita y que hoy se reescribe a mano en cada repo. Recovery (detectar operaciones interrumpidas y continuarlas sin duplicar trabajo) exige estado durable, idempotencia, leases y scheduler, y solo la necesitan productos con procesos asíncronos o duraderos.

Además, Foundation necesita un primer experimento que valide el mecanismo completo (crear bloque → copiar → manifest → provenance → adaptar → validar) con una pieza pequeña y de bajo riesgo.

## Decisión

1. `ci` tiene `default_for: all-products`. Mission Control lo incluye en todo producto salvo exclusión explícita.
2. `recovery` tiene `default_for: on-demand` y `requires` `idempotency`, `retry` y `scheduler`. Se selecciona cuando el perfil del producto incluye operaciones asíncronas o duraderas (envíos masivos, webhooks, integraciones, pagos, agentes).
3. Ambos pertenecen a la familia `operational-safety`, junto con retry, idempotency, scheduler, health-checks, error-reporting, backups, migration-safety y observability. La familia se conserva como categoría descubierta; no implica construirlo todo.
4. **El primer bloque real de Foundation será `ci`**, no Recovery, Auth ni Calendar. Su promoción a `draft` es el primer follow-up del bootstrap y servirá para probar el ciclo completo en Mission Control, 7F y SKINA.
5. Recovery no es backup. Backups es otro bloque de la misma familia.

## Consecuencias

- Ningún producto nuevo debería llegar a `main` sin CI desde el primer día.
- El bloque `ci` debe ser una plantilla adaptable al stack (Node, Python, etc.), no un workflow fijo.
- Recovery y sus dependencias se extraerán de Forte Mission Control cuando un segundo producto (previsiblemente 7F o Finesse) las necesite.

## Alternativas rechazadas

- **Empezar por Auth o Calendar como primer bloque**: mayor superficie, más riesgo y más acoplamiento con decisiones de producto aún abiertas.
- **Recovery por defecto**: impone infraestructura de estado durable a productos que no la necesitan.
