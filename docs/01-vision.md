# Visión: qué es Forte Foundation

Origen: handoff §1, §9, §12, §15, §39, §40, §43, §46, §47 ([`00-handoff.md`](00-handoff.md), no normativo). Decisiones vigentes: [`decisions/`](decisions/README.md).

## Qué es

Forte Foundation es la biblioteca interna de **bloques reutilizables y versionados** del ecosistema Forte. Un bloque es una capacidad resuelta bien una vez (auth, workspace, CI, recovery, facturación española...) empaquetada para que Mission Control la **copie** en un producto, con procedencia registrada, sin que el producto dependa de Foundation en runtime.

Foundation existe para que cada producto nuevo cueste menos construir que el anterior sin repetir bugs, decisiones inseguras ni edge cases, y para que Mission Control pueda ensamblar productos con cada vez menos intervención manual.

## Qué NO es

- No es un producto que use un cliente final.
- No es 7F, ni Mission Control, ni SKINA.
- No es una librería compartida en runtime ni un paquete npm central ([ADR-0002](decisions/ADR-0002-productos-aislados-sin-runtime-central.md)).
- No es un cajón donde va todo lo reutilizable ([`06-criterios-de-admision.md`](06-criterios-de-admision.md)).
- No pertenece a 7F. 7F será uno de sus mayores consumidores, pero no su dueño conceptual.

## Posición en el ecosistema

```text
                         SKINA
              empresa / marca / portal comercial
                         │
                    comercializa
                         │
          ┌──────────────┼──────────────┐
          │              │              │
         7F          verticales       agentes
          │
          ├──────── Finesse (Beauty, España)
          └──────── futuros verticales


                 FORTE MISSION CONTROL
              construye / coordina / audita
                         │
          ┌──────────────┼──────────────┐
          │              │              │
         7F            SKINA       otros productos


                  FORTE FOUNDATION
             biblioteca interna reutilizable
      alimenta Mission Control y todos los productos
```

En una línea cada pieza:

| Pieza | Papel |
|-------|-------|
| **Foundation** | Piezas: bloques versionados que se copian. |
| **Mission Control** | Fábrica, dirección y coordinación: consulta Foundation, selecciona bloques, delega en especialistas, revisa y audita. |
| **7F** | Business Operating System horizontal para pequeñas empresas. Una plataforma técnica, varias experiencias. |
| **Finesse** | Experiencia vertical Beauty construida sobre 7F. Primer laboratorio comercial (España). |
| **SKINA** | Empresa, marca y portal comercial desde donde se venden 7F, verticales, agentes y otros productos. |

Foundation está **debajo** de todos ellos. Mission Control está **encima** como sistema de construcción.

## Capas: Foundation → plataforma → vertical

```text
Foundation          appointments (core)      pieza general, sin sector ni país
      ↓
7F                  incorpora el motor a su arquitectura empresarial
      ↓
Finesse             "Próxima clienta", "Mi Agenda", "Rebooking": semántica y UX Beauty
```

La UI exacta de "Mi Agenda" pertenece a Finesse. El motor de citas, la abstracción de calendario, el motor de recordatorios y las fichas de cliente pueden ser bloques de Foundation.

## Efecto compuesto

Foundation solo tiene valor porque el ecosistema tiene varios productos. Con el primero se construye casi todo; con el segundo se reutiliza una parte; con el décimo gran parte de la infraestructura ya está resuelta. Eso exige mantener calidad, versionado, provenance, documentación, compatibilidad, tests y aislamiento. Sin esas condiciones, Foundation se convierte en duplicación con otro nombre.

## Resultado que buscamos

Poder decir "construye un nuevo producto para el sector X en España" y que Mission Control entienda, planifique, consulte Foundation, seleccione bloques, configure región y providers, cree el repo, implemente, pruebe, despliegue y audite, conservando siempre repos independientes, productos aislados, decisiones auditables, versiones y revisión humana donde importa.

## Fuente de verdad

Este documento explica la visión. La autoridad sobre cómo funciona Foundation hoy es:

1. [`decisions/`](decisions/README.md): los ADRs.
2. [`spec/`](../spec/block.md): especificaciones de bloque, manifest y catálogo.
3. [`spec/schemas/`](../spec/schemas/block.schema.json): schemas validables.
4. [`registry/catalog.yaml`](../registry/catalog.yaml): estado actual del inventario.

El handoff original es un snapshot histórico. Si contradice a lo anterior, pierde.
