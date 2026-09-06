# Glosario

Términos tal como se usan en este repositorio. Identificadores en inglés; explicaciones en español.

| Término | Definición |
|---------|------------|
| **Bloque** (block) | Unidad de reutilización de Foundation: una capacidad resuelta, con descriptor, guía de integración, tests y versiones, lista para copiarse a un producto. Ver [`spec/block.md`](../spec/block.md). |
| **Familia** (family) | Categoría del catálogo a la que pertenece un bloque: `core`, `capabilities`, `providers`, `patterns`, `operational-safety`, `persistence`, `platform`, `regions`, `templates`, `testing`. Es un campo, no una carpeta. |
| **Variante** (variant) | Especialización de un bloque core: `vertical:<nombre>` (sector) o `region:<código>` (país). Declara `extends` hacia su base. |
| **Catálogo** (catalog) | `registry/catalog.yaml`: inventario vigente de bloques y su estado. |
| **Estado** (status) | Ciclo de vida de un bloque: `candidate` → `draft` → `stable` → `deprecated`. |
| **Candidato** (candidate) | Bloque identificado como capacidad probable que aún no tiene implementación en Foundation. |
| **Manifest** (`foundation.manifest.yaml`) | Archivo en cada producto que registra qué bloques copió, en qué versión, desde qué commit y si los personalizó. Ver [`spec/manifest.md`](../spec/manifest.md). |
| **Provenance** | Capacidad de saber de qué bloque, versión y commit procede cada copia en un producto. Se materializa en el manifest. |
| **Copia controlada** | Mecanismo de reutilización de Foundation: el bloque se copia o genera en el repo del producto y el producto lo posee. Opuesto a dependencia runtime compartida. |
| **Perfil de producto** (profile) | Tipo, mercado, idioma, moneda, vertical y plataforma de un producto. Mission Control lo usa para inferir bloques y variantes. |
| **Market / Región** | País o mercado (`ES`, `CH`, `EU`, `GLOBAL`). Determina pagos, facturación, fiscalidad, infraestructura y formatos. Independiente del idioma. |
| **Locale** | Idioma y formato de presentación (`es-ES`, `de-CH`). No selecciona bloques regionales. |
| **`decision_mode`** | Quién decide dentro de un bloque: `deterministic` (código), `ai` (LLM) o `mixed`. |
| **`default_for`** | `all-products` (incluido por defecto en todo producto serio) u `on-demand` (según perfil). |
| **Upgrade automático / asistido / manual** | Etiqueta de cada versión en el CHANGELOG que indica cuánto puede preparar Mission Control por su cuenta (rama, aplicación, tests, PR). Ninguno elimina la revisión humana ni el merge por PR. |
| **Dependency closure** | Regla del manifest: si un bloque copiado declara `requires` o `extends`, cada uno de esos bloques tiene también su entrada, porque también se copió. |
| **Copiable** | Un bloque solo puede copiarse a un producto si está en `draft` (experimental) o `stable`. Un `candidate` solo puede recomendarse. |
| **Recovery** | Detectar operaciones que empezaron correctamente y quedaron interrumpidas, y continuarlas o reconciliar su estado sin duplicar trabajo. No es backup. |
| **Idempotencia** | Propiedad por la que reejecutar una operación no duplica sus efectos. Base de Recovery, reminders e integraciones. |
| **Lease** | Reserva temporal de un trabajo por un ejecutor para evitar que dos procesos lo hagan a la vez. |
| **Operational Safety** | Familia de bloques de red de seguridad operativa: CI, recovery, retry, idempotency, scheduler, health, error reporting, backups, migration safety, observability. |
| **Provider** | Abstracción de proveedor externo (email, storage, IA, WhatsApp, calendario) con contrato, errores, tests y adapters intercambiables. |
| **Workspace** | Unidad multi-tenant básica. Todo dato de producto pertenece a un workspace. Roles base: OWNER, ADMIN, MEMBER, VIEWER. |
| **Entitlements → Capabilities → Tools** | Cadena conceptual de 7F: qué tiene contratado el workspace → qué puede hacer el sistema → qué herramientas usa la persona o el agente. |
| **Mission Control** (Forte MC) | Sistema desde el que se definen productos y misiones, se delega en especialistas, se revisa, aprueba, construye y audita. Consumidor principal de Foundation. |
| **Mr Forte** | Coordinador IA dentro de Mission Control que entiende el producto, consulta Foundation y delega en especialistas. |
| **Especialistas** | Agentes con rol (Builder, Reviewer, Researcher...) que ejecutan acciones reales bajo coordinación. Capa distinta de Foundation. |
| **7F** | Business Operating System: plataforma empresarial horizontal para pequeñas empresas. Una plataforma técnica, varias experiencias. |
| **Finesse** | Vertical Beauty construido sobre 7F. Primer laboratorio comercial; mercado inicial España. |
| **SKINA** | Empresa, marca y portal comercial desde donde se venden 7F, verticales, agentes y otros productos. No es 7F. |
| **ADR** | Architecture Decision Record. Registro de una decisión, su contexto y consecuencias. Viven en [`docs/decisions/`](decisions/README.md) y son normativos. |
| **Handoff** | Documento original de septiembre de 2026 con la visión inicial. Histórico, no normativo. [`00-handoff.md`](00-handoff.md). |
