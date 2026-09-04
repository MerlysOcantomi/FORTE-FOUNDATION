# Integración de <id>@<versión>

Guía que sigue Mission Control (o una persona) para copiar este bloque en un producto.

## Requisitos previos

- Bloques requeridos y versiones (deben coincidir con `requires` en `block.yaml`).
- Stack asumido (lenguaje, framework, base de datos) y cómo adaptarlo si difiere.

## Pasos

1. Copiar los archivos listados en el README a `<ruta en el producto>`.
2. Ajustar configuración: variables de entorno necesarias (solo nombres, nunca valores).
3. Ejecutar migraciones/generadores si aplica.
4. Ejecutar los tests del bloque dentro del producto.
5. Registrar la entrada en `foundation.manifest` del producto (ver `spec/manifest.md`).

## Configuración

| Variable / opción | Obligatoria | Descripción |
|-------------------|-------------|-------------|
| `EXAMPLE_SETTING` | sí | ... |

## Verificación

Cómo comprobar que la integración es correcta (comandos, tests, comprobaciones manuales).

## Upgrade

Qué cambia entre versiones y cómo migrar. Enlazar al CHANGELOG.
