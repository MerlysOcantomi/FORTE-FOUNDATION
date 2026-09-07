> **Documento histórico, no normativo.**
>
> Este es el handoff original con el que se creó el repositorio (septiembre de 2026), conservado tal cual para recordar por qué existe Foundation y qué queríamos al principio.
>
> **No es la fuente de verdad vigente.** La autoridad actual es: [`docs/decisions/`](decisions/README.md) (ADRs) + [`spec/`](../spec/block.md) + [`spec/schemas/`](../spec/schemas/block.schema.json) + el estado actual de [`registry/catalog.yaml`](../registry/catalog.yaml). Si algo de este documento contradice a esos archivos, ganan ellos.

---

# FORTE FOUNDATION — HANDOFF COMPLETO

## 1. Qué es Forte Foundation

Forte Foundation es la capa interna de bloques reutilizables, patrones, scaffolds, contratos y capacidades que sirve para construir los productos del ecosistema sin tener que resolver una y otra vez los mismos problemas técnicos y de producto.

No es un producto que el cliente final use directamente.
No es 7F.
No es Mission Control.
No es SKINA.

Foundation es la base reutilizable de construcción que puede alimentar a todos ellos.

La idea central es:

> Cuando construimos una capacidad bien resuelta una vez, debemos poder reutilizarla de forma controlada en futuros productos sin copiar manualmente conocimiento, arquitectura y errores una y otra vez.

## 2. Principio fundamental: reutilización por copia, no por dependencia compartida

La decisión más importante tomada para Foundation es que los productos deben permanecer aislados entre sí.

NO queremos que todos los productos dependan en runtime de una gran librería central que, si cambia o falla, pueda afectar simultáneamente a:

* 7F
* Finesse
* SKINA
* Mission Control
* ProSound
* futuros SaaS
* futuros verticales

Foundation funciona principalmente mediante:

templates + scaffolds + bloques versionados + generación/copia controlada.

Ejemplo:

```text
Forte Foundation
      │
      ├── auth v3
      ├── workspace v2
      ├── permissions v4
      ├── CI v1
      ├── recovery v2
      ├── calendar v3
      └── regional/es-invoicing v1
                │
                ▼
       Mission Control selecciona
                │
                ▼
         copia al producto
                │
                ▼
      producto posee su versión
```

Una vez copiado:

El producto controla esa implementación.

Una actualización de Foundation NO debería romper automáticamente los productos existentes.

## 3. Por qué elegimos este modelo

El objetivo es evitar una arquitectura donde:

```text
Foundation rompe
       ↓
7F rompe
Finesse rompe
SKINA rompe
otros productos rompen
```

Preferimos:

```text
Foundation v4
       ↓ copia/versionado

7F → posee su copia
Finesse → posee su copia
Producto X → posee su copia
```

Esto permite:

* independencia entre productos;
* actualización controlada;
* rollback;
* auditoría;
* versiones diferentes cuando sea necesario;
* personalización por producto;
* menor blast radius;
* evolución de Foundation sin obligar a migraciones simultáneas.

## 4. Foundation no debe convertirse en un cajón de componentes

No queremos meter cualquier cosa reutilizable en Foundation.

Un bloque debería entrar cuando exista evidencia de que representa una capacidad o patrón suficientemente general.

La pregunta no es:

> "¿Podemos reutilizar este código?"

La pregunta es:

> "¿Esto representa una capacidad estable que varios productos podrían necesitar y cuya reutilización nos ahorra resolver de nuevo arquitectura, seguridad, edge cases y operación?"

Foundation puede contener tanto código como:

* contratos;
* patrones;
* schemas;
* templates;
* tests;
* políticas;
* configuración;
* documentación;
* migraciones;
* generadores;
* instrucciones de integración.

## 5. Mission Control es quien debe usar Foundation inteligentemente

La visión NO es que Merlys tenga que entrar en Foundation y seleccionar manualmente:

* Auth
* Workspace
* Calendar
* Billing
* CI
* Recovery
* Email
* etc.

La selección debe ser principalmente automática mediante IA.

Ejemplo:

Merlys dice:

> "Quiero construir una aplicación para pequeños salones de uñas en España con agenda, WhatsApp, clientes, recordatorios y facturación."

Mission Control debería inferir:

```text
Necesita:
✓ auth
✓ workspace
✓ client-records
✓ calendar
✓ appointments
✓ notifications
✓ WhatsApp provider
✓ reminders
✓ permissions
✓ CI
✓ audit
✓ Spain regional layer
✓ EUR
✓ Spanish locale
✓ Spanish invoicing rules
```

Después debe:

1. identificar los bloques necesarios;
2. seleccionar versiones compatibles;
3. resolver dependencias;
4. seleccionar variantes regionales;
5. copiarlos al repo correspondiente;
6. configurar la integración;
7. ejecutar tests;
8. explicar qué seleccionó;
9. permitir revisión/corrección humana;
10. registrar de dónde procede cada bloque.

Merlys puede revisar o corregir la selección.

Pero no debería tener que marcar repetidamente cada bloque a mano.

## 6. Mission Control + Foundation

Esta relación es central.

### Forte Mission Control

Mission Control es el sistema desde donde Merlys/Mr Forte:

* define productos;
* define misiones;
* delega trabajo;
* coordina especialistas;
* revisa trabajo;
* aprueba;
* construye;
* audita;
* mantiene proyectos.

### Forte Foundation

Foundation es la biblioteca de capacidades reutilizables disponibles para esos productos.

Por tanto:

```text
Merlys
   ↓
Mission Control
   ↓
Mr Forte
   ↓
entiende el producto
   ↓
consulta Foundation
   ↓
elige bloques
   ↓
Builder / especialistas
   ↓
crean o modifican producto
```

A largo plazo Mission Control debería "conocer" Foundation profundamente.

## 7. Foundation también aprende de los productos

La relación debe funcionar en ambos sentidos.

No solamente:

```text
Foundation → productos
```

También:

```text
productos → descubrimientos → Foundation
```

Ejemplo:

En Forte MC resolvemos correctamente:

* idempotencia;
* recuperación de operaciones;
* concurrencia;
* leases;
* CI;
* procesamiento de voz;
* transcripciones durables.

Si esa solución resulta suficientemente general, no debemos volver a inventarla en 7F.

Debemos evaluar:

> ¿Puede convertirse en un bloque reusable de Foundation?

Por tanto Forte MC también funciona como uno de nuestros laboratorios arquitectónicos.

Lo mismo puede ocurrir con 7F, Finesse, SKINA o cualquier producto.

## 8. Foundation no implica copiar automáticamente cualquier implementación

Es importante distinguir:

**Patrón específico**
Algo diseñado exclusivamente para un producto.

**Capacidad generalizable**
Algo que realmente puede reutilizarse.

Ejemplo:

La UI exacta de "Mi Agenda" de Finesse puede pertenecer únicamente a Finesse.

Pero:

```text
Appointment Engine
Calendar Provider abstraction
Reminder Engine
Customer Records
Recurring Jobs
```

sí pueden convertirse en capacidades Foundation.

## 9. Arquitectura global que queremos

Conceptualmente:

```text
                     FORTE FOUNDATION
                reusable capabilities
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
       Mission Control   7F      otros productos
             │           │
             │           ├───────────────┐
             │           │               │
             │        Finesse       otros verticales
             │
             ▼
       construye/mantiene
        todo el ecosistema
```

Foundation está debajo del ecosistema.

Mission Control está por encima como sistema de construcción, coordinación y mantenimiento.

## 10. Relación con 7F

7F es el Business Operating System.

Es una plataforma empresarial horizontal para pequeñas empresas.

La intención es que reúna capacidades como:

* clientes;
* comunicación;
* marketing;
* agenda;
* operaciones;
* archivos;
* proyectos;
* tareas;
* equipos;
* agentes;
* integraciones;
* presencia;
* automatizaciones;
* finanzas;
* IA.

Conceptualmente:

> 7F representa el sistema operativo de la empresa.

Existe además una IA transversal/Copilot.

En definiciones anteriores:

```text
7F = sistema
Copilot = inteligencia transversal
```

También se ha manejado una organización conceptual del producto alrededor de áreas como:

**Flow** — Operaciones. Ejemplos: Inbox, clientes, solicitudes, proyectos, tareas, calendario, archivos, departamentos.

**Forge** — Creación y producción. Ejemplos: contenido, media, branding, diseño.

**Funds** — Finanzas y facturación.

**Future** — Estrategia, inteligencia, Agents, AI Engine.

**System** — Configuración.

No hay que asumir que esos nombres sean necesariamente definitivos, pero reflejan la organización conceptual existente.

## 11. Arquitectura de 7F: una plataforma, varias experiencias

Una decisión arquitectónica importante de 7F es:

> UNA plataforma técnica, varios productos/verticales/experiencias.

No queremos duplicar innecesariamente backend, auth, clientes, agenda, etc. para cada vertical.

Dentro de 7F existe la cadena conceptual:

```text
Entitlements
     ↓
Capabilities
     ↓
Tools
```

Es decir:

**Entitlements** — Qué tiene contratado/habilitado el workspace.

**Capabilities** — Qué puede hacer el sistema para ese cliente.

**Tools** — Qué herramientas concretas puede utilizar la persona o agente.

Esto permite que dos clientes utilicen experiencias distintas sobre una misma plataforma.

## 12. Foundation y 7F NO son lo mismo

Este límite es importante.

7F puede contener muchas capacidades compartidas entre sus verticales.

Pero Foundation vive un nivel más abajo.

Ejemplo:

```text
Foundation
   ↓
Calendar Engine
   ↓
7F
   ↓
Finesse calendar experience
```

O:

```text
Foundation
   ↓
Provider abstraction
   ↓
7F communication
   ↓
Finesse WhatsApp workflow
```

Foundation contiene la pieza general.
7F la incorpora a su arquitectura.
El vertical adapta la experiencia a su mercado.

## 13. Verticales de 7F

La estrategia comercial definida es:

> Core horizontal + entrada vertical.

No intentar vender inicialmente "un sistema operativo para cualquier empresa" sin contexto.

Podemos entrar mediante productos/experiencias diseñados para sectores concretos.

El primer laboratorio comercial importante es:

**Finesse** — Vertical Beauty.

Dirigido inicialmente a:

* manicura/uñas;
* peluquería;
* estética;
* barbería;
* independientes;
* pequeños salones.

Mercado inicial considerado: España.

## 14. Finesse como ejemplo de relación Foundation → 7F → vertical

Finesse necesita capacidades concretas:

* calendario;
* citas;
* clientes;
* recordatorios;
* WhatsApp;
* rebooking;
* reseñas;
* notas;
* alergias;
* fotos;
* presencia web;
* Inbox;
* agenda;
* Marketing;
* IA;
* My Finesse/PWA.

Pero no todo eso tiene que escribirse exclusivamente para Beauty.

Ejemplo:

```text
Foundation
  ├── appointments
  ├── customer-records
  ├── reminders
  ├── WhatsApp-provider
  ├── notifications
  └── CI
          ↓
          7F
          ↓
        Finesse
          ↓
"Próxima clienta"
"Mi Agenda"
"Rebooking"
"Recordatorio de cita"
```

Foundation aporta la capacidad.
7F aporta el sistema empresarial.
Finesse aporta semántica, UX y workflows específicos de Beauty.

## 15. SKINA

Existe otro nivel distinto:

SKINA es empresa/marca/portal comercial.

Una definición anterior importante fue:

> SKINA es la empresa/marca/portal comercial; 7F es el software empresarial; agentes y verticales pueden ser productos/funciones vendidos desde SKINA.

Por tanto no debemos confundir:

```text
SKINA ≠ 7F
```

Conceptualmente:

```text
SKINA
│
├── comercializa productos
├── presenta soluciones
├── puede vender agentes
├── puede vender verticales
└── puede vender productos SaaS

           ↓

          7F
Business Operating System

           ↓

 verticales / experiencias
```

SKINA puede ser la superficie empresarial/comercial desde la que se presentan distintas soluciones.

7F es una de las plataformas/software fundamentales.

## 16. Relación Foundation ↔ SKINA

SKINA también puede consumir capacidades de Foundation.

Por ejemplo:

```text
Foundation
 ├── auth
 ├── billing
 ├── subscriptions
 ├── customer portal
 ├── permissions
 ├── analytics
 ├── notifications
 └── CI
        ↓
       SKINA
```

Pero SKINA no debe depender directamente en runtime de los mismos módulos que otro producto.

Igual que los demás: recibe una implementación versionada/copiada/configurada para su repo.

## 17. Agentes y especialistas

En la visión del ecosistema existe también un modelo de agentes.

Una concepción anterior de 7F contempla:

* una IA coordinadora;
* especialistas/agentes;
* espacios propios para ciertos agentes;
* posibilidad de que aparezcan también en una conversación central;
* agentes verticales que incluso puedan monetizarse separadamente.

A nivel de Mission Control, la dirección evoluciona hacia:

```text
Merlys
   ↓
Mr Forte / coordinador
   ↓
especialistas
   ├── Builder
   ├── Reviewer
   ├── Researcher
   ├── etc.
   ↓
acciones reales
```

Foundation puede proporcionar capacidades y herramientas para esos especialistas.

Pero los agentes son una capa distinta de Foundation.

## 18. La selección Foundation debe considerar IA vs código determinista

No todo debe ser resuelto mediante LLM.

Para cada capacidad conviene decidir:

```text
¿Esto requiere IA?
¿Esto debe ser código determinista?
¿Es una combinación?
```

Por ejemplo:

**IA** puede decidir:

* qué bloques seleccionar;
* interpretar necesidades del producto;
* proponer configuración;
* analizar compatibilidad;
* generar adapters.

**Código determinista** debe controlar cosas como:

* permisos;
* migrations;
* schemas;
* constraints;
* validaciones;
* invariantes;
* retries;
* idempotencia;
* ejecución crítica.

La IA puede decidir y coordinar.
Los invariantes importantes deben permanecer verificables.

## 19. Regionalización

Foundation NO debe limitarse a idiomas.

Esta es una decisión importante.

Debemos separar:

```text
Language / Locale
```

de:

```text
Country / Market / Region
```

Porque España, Suiza, Alemania o Estados Unidos pueden compartir funciones, pero tener necesidades diferentes.

Foundation debe poder proporcionar bloques regionales.

Ejemplos:

**Pagos** — proveedores disponibles; métodos locales; monedas.

**Facturación** — formatos; numeración; impuestos; requisitos legales.

**Fiscalidad/compliance** — reglas locales; consentimiento; retención; documentación.

**Infraestructura** — providers regionales; hosting; comunicaciones.

**Formatos** — fecha; moneda; teléfono; direcciones.

## 20. Selección regional automática

La IA debe poder inferir algo como:

```text
Producto:
Finesse

Mercado:
España

Idioma:
español

Moneda:
EUR

Sector:
Beauty
```

Y seleccionar:

```text
Foundation Global
    +
Foundation EU
    +
Foundation Spain
    +
Beauty-specific integration
```

Otro producto en Suiza podría recibir:

```text
Foundation Global
    +
Foundation Switzerland
    +
CHF
    +
Swiss regional integrations
```

Sin alterar el bloque global.

## 21. Separación recomendada

Conceptualmente Foundation puede acabar organizándose mediante capas como:

```text
foundation/
   core/
   capabilities/
   providers/
   patterns/
   operations/
   regions/
   templates/
   testing/
```

No considerar esta estructura de carpetas como una especificación definitiva.

Es una representación conceptual.

## 22. Providers intercambiables

Una filosofía existente tanto en 7F como en Mission Control es utilizar abstracciones de provider cuando tenga sentido.

Ejemplo:

```text
EmailProvider
 ├── Resend
 ├── SendGrid
 └── otro

StorageProvider
 ├── Vercel
 ├── S3
 └── otro

AIProvider
 ├── OpenAI
 ├── Anthropic
 └── otro
```

Foundation puede proporcionar:

* interfaz;
* contrato;
* errores;
* tests;
* adapters;
* selección.

El producto puede elegir provider.

No debemos acoplar capacidades del dominio a un proveedor concreto cuando exista una abstracción razonable.

## 23. Seguridad de secretos y entornos

Queremos que Mission Control disponga de una manera segura de manejar configuración y secretos necesarios para construir y operar productos.

Ejemplos:

* API keys;
* tokens;
* URLs de bases de datos;
* claves OAuth;
* credenciales de providers;
* variables de entorno.

Debe existir:

* control de permisos;
* separación de entornos;
* trazabilidad;
* protección contra exposición accidental;
* acceso estable para Builders cuando esté autorizado.

Idealmente Mission Control sabe:

```text
Producto X
 ├── Development
 ├── Preview
 └── Production
```

y qué secretos/configuración existen en cada ambiente.

Los secretos NO deben acabar escritos en prompts, commits o logs.

## 24. Databases

Foundation puede contener también patrones y scaffolds de persistencia.

No significa compartir una base de datos entre todos los productos.

Cada producto debe conservar aislamiento.

Foundation puede ofrecer:

```text
Postgres setup
Prisma setup
Migration safety
Workspace isolation
Testing
Seed patterns
Backup/restore
```

Actualmente existe una dirección importante en otros productos del ecosistema hacia:

> Neon + PostgreSQL.

Pero Foundation debe abstraer adecuadamente lo reusable y no convertirse simplemente en "copiar la configuración exacta de 7F".

## 25. Multi-tenancy

7F tiene como concepto importante:

```text
Workspace
```

con roles como:

* OWNER
* ADMIN
* MEMBER
* VIEWER

Foundation puede proporcionar los primitives multi-tenant reutilizables:

```text
Workspace
Membership
Role
Permission
Tenant isolation
```

No significa que todos los productos deban exponer exactamente los mismos roles.

El producto puede especializar.

## 26. CI como bloque Foundation

A raíz de la experiencia con Mission Control se identificó una capacidad nueva que debería formar parte de Foundation:

**Continuous Integration / CI**

Todos los productos serios deberían recibir por defecto una red mínima de seguridad.

Ejemplo:

```text
Pull Request
     ↓
install
     ↓
lint
     ↓
typecheck
     ↓
build
     ↓
tests
```

Objetivo: impedir que código obviamente roto llegue a main o producción.

Foundation debería poder proporcionar una plantilla/configuración de CI adaptable al stack del producto.

No deberíamos volver a escribir manualmente el workflow en cada repo.

## 27. Recovery como bloque Foundation

Otra capacidad identificada mediante Forte MC:

**Recovery**

Recovery NO significa backup.

Significa: detectar operaciones que empezaron correctamente pero quedaron interrumpidas y continuar/reconciliar su estado sin duplicar trabajo.

Ejemplo:

```text
Job empieza
 ↓
paso 1 completado
 ↓
paso 2 completado
 ↓
servidor se interrumpe
 ↓
Recovery
 ↓
detecta estado
 ↓
continúa desde paso 3
```

Esto requiere normalmente conceptos como:

* durable state;
* retries;
* idempotencia;
* leases;
* concurrencia;
* estados explícitos;
* reconciliación;
* scheduler.

No todos los productos necesitan Recovery inicialmente.

Por tanto:

**CI** — Default para prácticamente todos los productos serios.

**Recovery** — Capability seleccionada cuando el producto tenga procesos asíncronos o duraderos susceptibles de quedar incompletos.

## 28. Operational Safety

Lo anterior revela una posible familia importante dentro de Foundation:

**Operational Safety**

Podría contener capacidades como:

```text
CI
Recovery
Retry
Idempotency
Health checks
Schedulers / cron
Error reporting
Backups
Migration safety
Observability
```

Esto NO significa construir todo inmediatamente.

Es una categoría descubierta que conviene conservar.

Mission Control debería poder inferir cuáles necesita cada producto.

## 29. Ejemplo: 7F y Recovery

7F probablemente terminará siendo un consumidor importante de esta familia porque manejará operaciones como:

* WhatsApp;
* emails;
* facturas;
* recordatorios;
* integraciones;
* agentes;
* documentos;
* sincronizaciones;
* webhooks;
* automatizaciones;
* pagos.

Ejemplo:

```text
Enviar 300 recordatorios
        ↓
173 enviados
        ↓
ejecución interrumpida
        ↓
Recovery
        ↓
continúa los restantes
```

sin enviar otra vez los primeros 173.

## 30. Ejemplo: Finesse y Recovery

Una cita puede iniciar varias operaciones:

```text
crear cita
   ↓
actualizar agenda
   ↓
enviar WhatsApp
   ↓
programar recordatorio
   ↓
registrar seguimiento
```

Si se interrumpe:

Recovery debe saber qué pasos ya sucedieron y cuáles faltan.

Eso evita tanto tareas perdidas como duplicados.

## 31. Versionado de bloques

Foundation necesita conceptualmente un registro de versiones.

Ejemplo:

```text
calendar@1.0
calendar@2.0

auth@3.2

workspace@2.1

region-es-invoicing@1.4
```

Un producto debería poder registrar algo como:

```text
Product A
calendar@1.0

Product B
calendar@2.0
```

Sin obligar a Product A a actualizar.

## 32. Provenance

Mission Control debería saber:

> Este código fue generado/copied/adaptado desde Foundation bloque X versión Y.

No necesariamente mediante dependencia runtime.

Pero sí mediante metadata.

Ejemplo conceptual:

```text
foundation.manifest
```

con:

```text
auth: 3.2
workspace: 2.1
ci: 1.0
appointments: 2.4
region-es: 1.3
```

Esto permitiría:

* saber qué productos usan cada bloque;
* detectar versiones antiguas;
* proponer upgrades;
* revisar seguridad;
* comparar cambios.

## 33. Upgrades de Foundation

Una nueva versión de un bloque NO debe actualizar automáticamente todos los productos.

El flujo deseado es algo como:

```text
Foundation auth v4 disponible
          ↓
Mission Control detecta:
Finesse utiliza auth v3
          ↓
analiza cambios
          ↓
propone upgrade
          ↓
crea branch
          ↓
aplica migration
          ↓
tests
          ↓
review
          ↓
aprobación
```

Esto mantiene aislamiento y control.

## 34. Compatibilidad entre bloques

A medida que Foundation crezca necesitaremos poder expresar compatibilidad.

Ejemplo:

```text
appointments@3
requiere:
workspace >=2
notifications >=3

Spain-invoicing@2
requiere:
billing >=4
```

Mission Control debe resolver esto automáticamente.

No queremos que Merlys tenga que conocer grafos de dependencias.

## 35. Foundation y autonomía de Mission Control

Una aspiración importante es que Mission Control pueda hacer gran parte del trabajo repetitivo de forma autónoma.

Ejemplo:

Merlys: "Construye este nuevo SaaS."

Mission Control:

1. entiende problema;
2. clasifica producto;
3. detecta mercado;
4. consulta Foundation;
5. selecciona stack;
6. selecciona bloques;
7. crea repo/scaffold;
8. configura environments;
9. genera integración;
10. ejecuta pruebas;
11. delega trabajo;
12. presenta decisiones importantes.

Pero debe existir una frontera clara entre:

**Decisiones reversibles/rutinarias** — Puede ejecutarlas automáticamente.

**Decisiones de alto impacto** — Debe pedir aprobación.

## 36. Foundation y especialización

Un bloque puede tener:

**core global**

```text
appointments-core
```

**adapter sectorial**

```text
appointments-beauty
```

**adapter regional**

```text
appointments-es
```

Y el producto combina:

```text
Core
+
Vertical
+
Region
+
Product UX
```

Esto es mucho más potente que construir una aplicación aislada desde cero para cada sector.

## 37. Qué queremos evitar

**A. Mega monolito compartido** — Foundation no debe convertirse en un runtime central del que dependa todo.

**B. Duplicación descontrolada** — Copiar sin saber: origen; versión; diferencias.

**C. Selección manual repetitiva** — Merlys no debe tener que marcar veinte módulos cada vez que crea un producto.

**D. Sobregeneralización** — No convertir en Foundation una característica que solo sirve a un producto.

**E. Abstracciones prematuras** — No construir grandes frameworks internos antes de que exista evidencia real.

**F. Actualizaciones globales peligrosas** — Nunca cambiar Foundation y romper automáticamente productos existentes.

## 38. Cómo decidir si algo entra en Foundation

Antes de promover una implementación a Foundation, comprobar:

1. ¿Existe en más de un producto o probablemente existirá?
2. ¿Representa una capacidad real?
3. ¿Hay invariantes importantes que merece la pena resolver una vez?
4. ¿Puede parametrizarse sin convertirse en un framework inmanejable?
5. ¿El producto seguirá pudiendo personalizarla?
6. ¿Puede versionarse?
7. ¿Puede probarse de forma independiente?

Si la respuesta es sí, es candidata a Foundation.

## 39. Relación general del ecosistema

La forma más sencilla de entenderlo es:

```text
                         SKINA
              empresa / marca / portal
                         │
                    comercializa
                         │
          ┌──────────────┼──────────────┐
          │              │              │
         7F          verticales       agentes
          │
          ├──────── Finesse
          ├──────── futuros verticales
          │
          ▼
Business Operating System


                 FORTE MISSION CONTROL
                         │
                 construye / coordina
                         │
          ┌──────────────┼──────────────┐
          │              │              │
         7F            SKINA       otros productos
          │
          ▼
       Finesse


                  FORTE FOUNDATION
                         │
          biblioteca interna reusable
                         │
      alimenta Mission Control y productos
```

Otra forma:

```text
Foundation = piezas

Mission Control = fábrica + dirección + coordinación

7F = plataforma empresarial

Finesse = experiencia vertical Beauty sobre 7F

SKINA = empresa/marca/portal comercial que puede vender
        7F, verticales, agentes y otros productos
```

## 40. Forte Foundation no pertenece exclusivamente a 7F

Esto es crítico.

Foundation debe poder servir a:

* Forte Mission Control;
* 7F;
* SKINA;
* Finesse;
* ProSound;
* herramientas internas;
* nuevos SaaS;
* futuros productos.

No debemos diseñarlo exclusivamente alrededor de 7F.

7F será uno de sus mayores consumidores, pero no su dueño conceptual.

## 41. Forte Mission Control puede convertirse en consumidor de sí mismo

Una idea de largo plazo es que Mission Control pueda utilizar Foundation y sus Builders para trabajar también sobre el propio Mission Control.

Es decir:

```text
Mission Control
      ↓
detecta necesidad propia
      ↓
consulta Foundation
      ↓
crea cambio
      ↓
Builder
      ↓
Review
      ↓
aprobación
```

Esto permitiría que el sistema progresivamente pueda mantener partes de sí mismo bajo las mismas reglas que utiliza para otros productos.

Debe hacerse con controles fuertes.

## 42. Foundation y los futuros productos

Cuando aparezca una nueva idea, la experiencia ideal debería ser:

Merlys describe: Producto X.

Y Mission Control responde internamente:

```text
PRODUCT PROFILE

Type:
SaaS

Market:
Spain

Vertical:
Legal services

Users:
small firms

Needs:
auth
workspace
billing
calendar
files
email
AI
audit
CI
regional-es
```

Foundation provee las piezas.
Builders producen lo específico.

Así cada producto nuevo debería costar menos construir que el anterior.

Ese es uno de los grandes objetivos estratégicos de Foundation.

## 43. Efecto compuesto

Foundation tiene valor precisamente porque el ecosistema tiene varios productos.

Primer producto: construimos casi todo.
Segundo: reutilizamos una parte.
Décimo: gran parte de infraestructura ya está resuelta.

La inversión acumulada aumenta la velocidad futura.

Pero solo funciona si mantenemos:

* calidad;
* versionado;
* provenance;
* documentación;
* compatibilidad;
* tests;
* aislamiento.

## 44. Estado conceptual actual

Foundation todavía no debe entenderse como una librería completamente implementada y terminada.

Tenemos principalmente:

**Visión definida**

✓ biblioteca reutilizable
✓ copia/scaffold, no dependencia runtime central
✓ productos aislados
✓ selección automática mediante IA
✓ versiones
✓ regionalización
✓ compatibilidad
✓ secretos/entornos
✓ providers
✓ integración con Mission Control
✓ relación con 7F y verticales

**Capacidades candidatas identificadas**

Entre otras:

* auth;
* workspace;
* permissions;
* multi-tenancy;
* providers;
* calendar;
* appointments;
* notifications;
* integrations;
* billing;
* regionalization;
* CI;
* Recovery;
* Retry;
* Idempotency;
* Scheduler;
* Health;
* Observability;
* Migration safety;
* secrets/env management.

No significa que todos esos bloques estén ya construidos como productos Foundation independientes.

## 45. Regla para trabajar ahora

No debemos detener nuestros productos actuales para construir primero un "Foundation perfecto".

La estrategia debe ser incremental:

```text
Producto necesita capacidad
        ↓
la construimos bien
        ↓
la validamos en contexto real
        ↓
evaluamos generalización
        ↓
si merece Foundation:
extraemos patrón/bloque
        ↓
Foundation crece
```

Evitar:

```text
6 meses construyendo Foundation
sin productos reales
```

Queremos que Foundation emerja de necesidades reales, con una arquitectura deliberada.

## 46. Prioridad estratégica

Foundation debe ayudarnos a conseguir tres cosas:

**1. Velocidad** — Construir nuevos productos mucho más rápido.

**2. Calidad** — No repetir bugs, decisiones inseguras y edge cases.

**3. Autonomía** — Permitir que Mission Control y sus agentes puedan ensamblar productos progresivamente con menos intervención manual.

## 47. Resultado final que buscamos

A largo plazo queremos poder decir algo como:

> "Construye un nuevo producto para X sector en España."

Y que Mission Control pueda:

```text
entender
↓
planificar
↓
consultar Foundation
↓
seleccionar bloques
↓
crear arquitectura
↓
configurar región
↓
configurar providers
↓
crear repo
↓
implementar
↓
probar
↓
desplegar
↓
auditar
```

sin comenzar desde cero.

Pero conservando siempre:

* repos independientes;
* productos aislados;
* decisiones auditables;
* versiones;
* revisión humana donde importa;
* capacidad de evolucionar cada producto independientemente.

## RESUMEN EJECUTIVO

Forte Foundation es la biblioteca interna reusable del ecosistema.

Su principio principal es: reutilizar conocimiento y capacidades mediante bloques versionados copiados/generados dentro de cada producto, no mediante una dependencia runtime central compartida.

Forte Mission Control debe ser el sistema inteligente que consulta Foundation, selecciona automáticamente los bloques adecuados y coordina su incorporación a cada producto.

7F es el Business Operating System horizontal.

Finesse es un vertical Beauty/experiencia especializada sobre 7F.

SKINA es la empresa/marca/portal comercial desde donde pueden comercializarse 7F, verticales, agentes y otros productos.

Foundation está por debajo de todos ellos y puede servir también a productos que no pertenezcan a 7F.

La selección de bloques debe considerar:

* tipo de producto;
* capacidades;
* stack;
* mercado;
* idioma;
* país/región;
* versiones;
* compatibilidad;
* seguridad;
* providers.

Mission Control debe automatizar esa selección.

Foundation debe crecer de forma incremental a partir de soluciones probadas en productos reales y no mediante una gran abstracción prematura.

La meta es que cada nuevo producto del ecosistema sea más rápido, seguro y barato de construir que el anterior, sin sacrificar independencia entre productos.
