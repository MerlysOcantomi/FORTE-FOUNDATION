# ADR-0008: Abstracciones de provider intercambiables

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §22, §24

## Contexto

7F y Mission Control ya usan abstracciones de proveedor (EmailProvider con Resend o SendGrid, StorageProvider con Vercel o S3, AIProvider con OpenAI o Anthropic). Acoplar una capacidad de dominio a un proveedor concreto impide cambiarlo por coste, región o disponibilidad y hace que las reglas regionales (providers locales) sean imposibles de aplicar.

## Decisión

1. Cuando exista una abstracción razonable, las capacidades de dominio de Foundation dependen de un **contrato de provider**, nunca de un proveedor concreto.
2. Un bloque de la familia `providers` aporta: interfaz, contrato, catálogo de errores, tests de contrato, adapters disponibles (campo `providers` del descriptor) y criterios de selección.
3. El producto elige el adapter al integrar; la elección se registra en su configuración, no en el bloque.
4. Los bloques regionales pueden restringir o recomendar providers para un mercado (p. ej. pasarelas de pago locales) sin modificar el contrato.
5. Lo mismo aplica a persistencia: la dirección actual del ecosistema es Neon + PostgreSQL, pero el bloque `postgres-setup` abstrae lo reutilizable y no copia la configuración exacta de 7F.

## Consecuencias

- Cambiar de proveedor es un cambio de adapter y configuración, no de dominio.
- Cada abstracción exige tests de contrato que todos los adapters deben pasar; es parte del coste del bloque.
- No se crea una abstracción hasta que exista al menos un segundo proveedor plausible o una necesidad regional; en caso contrario es abstracción prematura (§37.E).

## Alternativas rechazadas

- **SDK del proveedor usado directamente desde el dominio**: rápido al principio, imposible de regionalizar o sustituir después.
- **Un único proveedor "bendecido" por capacidad para todo el ecosistema**: contradice la regionalización y crea dependencia comercial.
