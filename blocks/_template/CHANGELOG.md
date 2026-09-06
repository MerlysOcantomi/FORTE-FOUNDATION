# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado: semver (ver `spec/block.md`).

Cada versión debe indicar el tipo de upgrade desde la anterior. Ninguno elimina el PR ni la revisión humana en el producto; describe cuánto puede preparar Mission Control por su cuenta (definiciones en `spec/block.md`):

- **automático**: Mission Control prepara, aplica y valida el cambio en una rama y abre el PR. Revisar y fusionar sigue siendo humano.
- **asistido**: Mission Control prepara la rama siguiendo la migración documentada aquí; alguien completa los pasos marcados como decisión del producto antes de la revisión.
- **manual**: Mission Control solo abre un PR de aviso con este CHANGELOG; el cambio lo aplica una persona.

Si el producto tiene `customized: true` para este bloque, el upgrade es siempre manual.

## [Unreleased]

## [0.1.0] - AAAA-MM-DD

### Added
- Primera versión del bloque, extraída de <producto>.

Upgrade desde: n/a.
