# Regionalización

Origen: handoff §19, §20, §36. Decisión: [ADR-0004](decisions/ADR-0004-region-separada-de-locale.md).

## Idioma no es región

Foundation separa dos dimensiones que suelen confundirse:

| Dimensión | Campo del manifest | Ejemplos | Qué afecta |
|-----------|--------------------|----------|------------|
| **Locale** (idioma) | `profile.locale` | `es`, `es-ES`, `de-CH`, `en` | Textos, traducciones, formato de presentación. |
| **Market** (país/mercado) | `profile.market` | `ES`, `CH`, `DE`, `US`, `EU`, `GLOBAL` | Pagos, facturación, fiscalidad, compliance, infraestructura, formatos legales. |

España, Suiza, Alemania y Estados Unidos pueden compartir funciones y tener necesidades distintas. Suiza puede operar en alemán, francés o italiano con las mismas reglas de mercado. Por eso un bloque regional se identifica por país, nunca por idioma.

## Qué cubre una capa regional

| Área | Ejemplos |
|------|----------|
| Pagos | Proveedores disponibles, métodos locales, monedas. |
| Facturación | Formatos, numeración, impuestos, requisitos legales. |
| Fiscalidad y compliance | Reglas locales, consentimiento, retención, documentación. |
| Infraestructura | Providers regionales, hosting, comunicaciones. |
| Formatos | Fecha, moneda, teléfono, direcciones. |

## Capas apiladas

Las capas regionales se componen por herencia declarada con `extends`, sin alterar nunca el bloque global:

```text
region-global
   └── region-eu
         └── region-es
               └── region-es-invoicing   (requiere billing)
   └── region-ch
```

Un producto en España recibe `Foundation Global + EU + España + integración del vertical`. Otro en Suiza recibe `Global + Suiza + CHF + integraciones suizas`. El bloque global es el mismo en ambos.

## Selección automática

Mission Control infiere el perfil y selecciona las capas:

```text
Producto: Finesse
Mercado:  ES        →  region-global, region-eu, region-es
Idioma:   es-ES     →  locale (no selecciona bloques regionales)
Moneda:   EUR
Sector:   beauty    →  variantes vertical:beauty
Necesita facturación →  region-es-invoicing (requiere billing >=1)
```

## Composición core + vertical + región

Un mismo bloque de dominio puede existir en tres capas que el producto combina con su propia UX:

```text
appointments            core            sin sector ni país
appointments-beauty     vertical:beauty extends appointments
appointments-es         region:es       extends appointments
```

```text
Core + Vertical + Región + UX del producto
```

Esto es más potente que construir una aplicación aislada por sector y por país. Las reglas de variantes están en [`spec/block.md`](../spec/block.md).

## Reglas

1. Un bloque `core` nunca contiene reglas de país ni de sector.
2. Un bloque regional declara `variant: region:<código ISO 3166-1 alpha-2 en minúsculas>` (`region:global` y `region:eu` son los dos valores especiales).
3. Un bloque regional que amplía otro lo declara con `extends` y lo exige en `requires`.
4. El manifest del producto registra cada capa regional copiada como entrada independiente.
