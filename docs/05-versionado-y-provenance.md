# Versionado, provenance, upgrades y compatibilidad

Origen: handoff §23, §31–§34. Decisión: [ADR-0005](decisions/ADR-0005-versionado-semver-y-manifest.md). Formatos normativos: [`spec/block.md`](../spec/block.md), [`spec/manifest.md`](../spec/manifest.md).

## Versionado de bloques

Cada bloque tiene su propia versión semver. Distintos productos pueden usar distintas versiones del mismo bloque sin que nadie esté obligado a actualizar:

```text
calendar@1.0.0   → Product A
calendar@2.0.0   → Product B
auth@3.2.0
workspace@2.1.0
region-es-invoicing@1.4.0
```

Reglas de incremento y tipos de upgrade (`automático`, `asistido`, `manual`) en [`spec/block.md`](../spec/block.md#versionado).

## Provenance

Mission Control debe poder afirmar: "este código fue copiado o adaptado desde Foundation, bloque X, versión Y, commit Z". No mediante dependencia runtime, sino mediante metadata: el `foundation.manifest.yaml` de cada producto.

```yaml
blocks:
  - { id: auth,         version: 3.2.0, variant: core,      source_commit: "...", customized: false }
  - { id: workspace,    version: 2.1.0, variant: core,      source_commit: "...", customized: false }
  - { id: ci,           version: 1.0.0, variant: core,      source_commit: "...", customized: false }
  - { id: appointments, version: 2.4.0, variant: core,      source_commit: "...", customized: true }
  - { id: region-es,    version: 1.3.0, variant: region:es, source_commit: "...", customized: false }
```

Con los manifests de todos los productos, Mission Control puede saber qué productos usan cada bloque, detectar versiones antiguas, proponer upgrades, revisar seguridad y comparar cambios.

## Upgrades

Una versión nueva de un bloque **nunca** actualiza automáticamente los productos. El flujo:

```text
Foundation publica auth@4.0.0
          ↓
Mission Control lee los manifests
          ↓
detecta: Finesse usa auth@3.2.0
          ↓
lee CHANGELOG: tipo de upgrade y migración
          ↓
propone upgrade (explica qué cambia)
          ↓
crea rama en el repo de Finesse
          ↓
aplica migración · ejecuta tests
          ↓
PR → revisión → aprobación
          ↓
actualiza foundation.manifest
```

Si la entrada del manifest tiene `customized: true`, el upgrade siempre requiere revisión humana, aunque el CHANGELOG lo declare automático.

## Compatibilidad entre bloques

Los bloques declaran qué otros bloques necesitan y en qué rango:

```yaml
# appointments
requires: { workspace: ">=2", notifications: ">=3" }

# region-es-invoicing
requires: { region-es: ">=1", billing: ">=4" }
```

Mission Control resuelve el grafo; Merlys no tiene que conocerlo. El catálogo comprueba que toda referencia apunta a un bloque existente ([`spec/catalog.md`](../spec/catalog.md#reglas-de-integridad)). Un motor de resolución de dependencias no forma parte del bootstrap; hasta que exista, la resolución la hace Mission Control con el catálogo como entrada.

## Secretos y entornos

Foundation y sus bloques solo **nombran** variables de configuración; nunca contienen valores. Los valores viven en la gestión de secretos por producto y entorno, que es responsabilidad de Mission Control y del bloque candidato `secrets-env-management`:

```text
Producto X
 ├── development
 ├── preview
 └── production
```

Requisitos: control de permisos, separación de entornos, trazabilidad, protección contra exposición accidental y acceso estable para Builders autorizados. Los secretos no acaban en prompts, commits ni logs.
