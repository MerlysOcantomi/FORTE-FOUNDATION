# Relaciones de Foundation con el resto del ecosistema

Origen: handoff §5–§8, §10–§17, §35, §41, §42.

## Foundation ↔ Mission Control

Es la relación central. Mission Control es el sistema desde el que Merlys y Mr Forte definen productos y misiones, delegan trabajo, coordinan especialistas, revisan, aprueban, construyen, auditan y mantienen. Foundation es la biblioteca que Mission Control consulta para hacerlo.

```text
Merlys
   ↓
Mission Control / Mr Forte
   ↓ entiende el producto
   ↓ consulta registry/catalog.yaml
   ↓ elige bloques, versiones y variantes
   ↓
Builder / especialistas
   ↓
producto (con foundation.manifest actualizado)
```

Lo que Mission Control debe hacer con Foundation, en orden ([ADR-0003](decisions/ADR-0003-seleccion-automatica-por-mission-control.md)):

1. Inferir el perfil del producto (tipo, mercado, idioma, moneda, vertical).
2. Identificar los bloques necesarios; incluir los `default_for: all-products` que tengan versión copiable. Un bloque `candidate` solo puede recomendarse, nunca copiarse ([`spec/catalog.md`](../spec/catalog.md#qué-puede-hacer-mission-control-con-cada-estado)).
3. Seleccionar versiones compatibles resolviendo `requires` y copiar también cada dependencia, registrándola en el manifest (dependency closure).
4. Seleccionar variantes vertical y regional.
5. Copiar los bloques al repo del producto.
6. Configurar la integración siguiendo cada `integration.md`.
7. Ejecutar los tests del bloque dentro del producto.
8. Explicar qué seleccionó y por qué.
9. Permitir revisión y corrección humana.
10. Registrar la procedencia en `foundation.manifest`.

Frontera de autonomía: las decisiones reversibles y rutinarias se ejecutan solas; las de alto impacto piden aprobación.

## Productos → Foundation (el sentido inverso)

La relación funciona en ambos sentidos. Cada producto es un laboratorio arquitectónico: cuando Forte Mission Control resuelve bien idempotencia, recovery, leases, concurrencia o CI, o cuando Finesse resuelve bien citas y recordatorios, se evalúa si la solución es generalizable y, si lo es, se extrae como bloque ([`06-criterios-de-admision.md`](06-criterios-de-admision.md)).

```text
producto necesita capacidad → se construye bien → se valida en real
        → se evalúa generalización → se extrae a Foundation
```

Distinguir siempre **patrón específico** (solo sirve a un producto: la UI de "Mi Agenda") de **capacidad generalizable** (Appointment Engine, Reminder Engine, Customer Records).

## Foundation ↔ 7F

7F es el Business Operating System: plataforma empresarial horizontal para pequeñas empresas (clientes, comunicación, marketing, agenda, operaciones, archivos, proyectos, tareas, equipos, agentes, integraciones, presencia, automatizaciones, finanzas, IA), con una IA transversal (Copilot) y una organización conceptual por áreas (Flow, Forge, Funds, Future, System; nombres no definitivos).

Decisión clave de 7F: **una plataforma técnica, varias experiencias**, mediante la cadena `Entitlements → Capabilities → Tools` (qué tiene contratado el workspace → qué puede hacer el sistema → qué herramientas usa la persona o el agente).

Foundation vive un nivel más abajo que 7F. 7F puede compartir muchas capacidades entre sus verticales; eso no las convierte en bloques de Foundation. Solo lo son las piezas generales que también servirían fuera de 7F.

```text
Foundation   →  Calendar Engine        →  7F  →  experiencia de calendario de Finesse
Foundation   →  Provider abstraction   →  7F communication  →  workflow WhatsApp de Finesse
```

## Foundation ↔ verticales (Finesse)

Estrategia comercial: core horizontal + entrada vertical. Finesse es el primer laboratorio: Beauty (uñas, peluquería, estética, barbería, independientes, pequeños salones), mercado inicial España.

Finesse necesita calendario, citas, clientes, recordatorios, WhatsApp, rebooking, reseñas, notas, alergias, fotos, presencia web, Inbox, marketing, IA y PWA. Nada de eso se escribe exclusivamente para Beauty cuando existe una capacidad general:

```text
Foundation: appointments, customer-records, reminders, whatsapp-provider, notifications, ci
      ↓
7F: sistema empresarial
      ↓
Finesse: "Próxima clienta", "Mi Agenda", "Rebooking", "Recordatorio de cita"
```

Ver el manifest de ejemplo en [`examples/finesse-es.foundation.manifest.yaml`](../examples/finesse-es.foundation.manifest.yaml).

## Foundation ↔ SKINA

SKINA es la empresa, marca y portal comercial. No es 7F. Desde SKINA se comercializan 7F, verticales, agentes y otros productos SaaS.

SKINA consume Foundation igual que cualquier producto (auth, billing, subscriptions, customer-portal, permissions, analytics, notifications, ci) y con la misma regla: recibe copias versionadas en su propio repo, nunca comparte módulos en runtime con otro producto.

## Foundation ↔ agentes

El ecosistema contempla una IA coordinadora, especialistas (Builder, Reviewer, Researcher...) y agentes verticales que incluso pueden monetizarse. Foundation puede aportar capacidades y herramientas a esos agentes, pero **los agentes son una capa distinta**: no viven en Foundation ni Foundation depende de ellos.

## Mission Control como consumidor de sí mismo

A largo plazo Mission Control podrá usar Foundation y sus Builders para mantener partes del propio Mission Control bajo las mismas reglas que aplica a otros productos (detectar necesidad → consultar Foundation → crear cambio → Builder → Review → aprobación). Debe hacerse con controles fuertes; no es objetivo del bootstrap.

## Productos futuros

Cuando aparezca una idea nueva, Mission Control debería derivar un perfil de producto y una lista de necesidades sin que nadie marque bloques a mano:

```text
PRODUCT PROFILE
type: saas · market: ES · vertical: legal · users: small firms
needs: auth, workspace, billing, calendar, files, email, ai, audit, ci, region-es
```

Foundation aporta las piezas; los Builders producen lo específico.
