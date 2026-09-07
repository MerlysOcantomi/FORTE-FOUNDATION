# ADR-0003: La selección de bloques la hace Mission Control (IA) con invariantes deterministas

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §5, §6, §18, §35, §37.C

## Contexto

Si cada producto nuevo exigiera que Merlys marcara a mano veinte bloques (auth, workspace, calendar, billing, CI, recovery, email...) Foundation no reduciría el trabajo repetitivo; solo lo cambiaría de sitio. Al mismo tiempo, no todo puede delegarse en un LLM: permisos, migraciones, schemas, constraints, validaciones, retries e idempotencia deben permanecer verificables.

## Decisión

1. La **selección** de bloques es responsabilidad de Mission Control y se hace principalmente mediante IA a partir del perfil del producto (tipo, mercado, idioma, moneda, vertical, stack). Merlys revisa y corrige; no selecciona a mano por defecto.
2. Mission Control debe: identificar bloques, seleccionar versiones compatibles, resolver `requires`, seleccionar variantes regionales y verticales, copiar, configurar la integración, ejecutar tests, explicar la selección, permitir corrección humana y registrar la procedencia.
3. Los bloques con `default_for: all-products` se incluyen siempre salvo exclusión explícita, **cuando tienen una versión copiable**. `default_for` describe el perfil por defecto; el estado del bloque decide si puede copiarse:
   - `candidate`: Mission Control puede recomendarlo y detectar la necesidad, pero **nunca copiarlo**. La capacidad se construye en el producto y, si supera los criterios de admisión, se extrae después.
   - `draft`: copiable experimentalmente, con aprobación explícita en el PR del producto.
   - `stable`: seleccionable normalmente.
   - `deprecated`: no para productos nuevos.
   Tabla completa en [`spec/catalog.md`](../../spec/catalog.md#qué-puede-hacer-mission-control-con-cada-estado).
4. Cada bloque declara `decision_mode`. Los invariantes dentro de un bloque son `deterministic`; la IA puede decidir y coordinar, no sustituir una comprobación.
5. Frontera de autonomía: decisiones reversibles y rutinarias se ejecutan sin preguntar; decisiones de alto impacto (crear repo, cambiar contrato, tocar producción, upgrade de un bloque personalizado) piden aprobación.
6. Para que la IA pueda seleccionar, Foundation mantiene un catálogo legible por máquina ([`spec/catalog.md`](../../spec/catalog.md)) con familias, estados, variantes, `requires` y `default_for`. Ese catálogo es el contrato entre Foundation y Mission Control.

## Consecuencias

- El catálogo y los schemas son la prioridad del bootstrap, por encima de cualquier bloque implementado.
- Mientras todos los bloques sean `candidate`, Mission Control no copia nada de Foundation: el catálogo le sirve para razonar y recomendar, no para instalar. Eso es el estado esperado hasta que `ci` pase a `draft` ([ADR-0007](ADR-0007-ci-por-defecto-recovery-opcional.md)).
- La calidad de la selección depende de la calidad de las descripciones y metadatos del catálogo; mantenerlos es obligatorio.
- Un motor determinista de resolución de dependencias es deseable a futuro, pero no bloquea: hasta entonces la IA resuelve con el catálogo como entrada y las reglas de integridad del catálogo evitan referencias rotas.

## Alternativas rechazadas

- **Selección manual mediante checklist**: repetitiva y propensa a olvidos (§37.C).
- **Todo por IA, incluidos invariantes**: no verificable; contradice §18.
- **Todo determinista mediante reglas fijas**: no interpreta necesidades de producto expresadas en lenguaje natural.
