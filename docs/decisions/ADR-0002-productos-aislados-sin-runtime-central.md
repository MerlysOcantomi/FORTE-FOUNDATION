# ADR-0002: Productos aislados: sin librería runtime central

- Estado: aceptado
- Fecha: 2026-09-04
- Origen: handoff §2, §3, §16, §24, §37.A, §37.F

## Contexto

Complementa a [ADR-0001](ADR-0001-reutilizacion-por-copia.md). Además del mecanismo de reutilización, hay que fijar qué **no** puede compartirse entre productos para que el aislamiento sea real y no solo una intención.

## Decisión

1. Ningún producto depende de Foundation en runtime: ni paquete importado, ni servicio compartido, ni base de datos común.
2. Cada producto tiene su propio repositorio, su propia base de datos y sus propios entornos (development, preview, production) y secretos.
3. Foundation no publica paquetes ni expone APIs. Sus bloques son archivos que se copian.
4. Dos productos que copian el mismo bloque no comparten estado ni código en ejecución, aunque las copias sean idénticas.
5. Foundation no cambia un producto existente por sí sola; cualquier cambio en un producto entra por PR en el repo de ese producto.

## Consecuencias

- Un fallo en Foundation no puede tumbar productos en producción.
- Los productos pueden estar en versiones distintas de un mismo bloque durante el tiempo que necesiten.
- El coste es la duplicación física de código entre repos. Se acepta porque queda auditada por el manifest.
- Foundation no tiene runtime propio que operar ni desplegar.

## Alternativas rechazadas

- **Base de datos compartida multi-producto**: rompe el aislamiento por producto y multiplica el radio de un incidente.
- **Servicio Foundation central (API de capacidades)**: convierte Foundation en un runtime del que depende todo. Es exactamente el mega monolito que queremos evitar.
