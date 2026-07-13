# Sistema visual ejecutivo configurable

## Principios

- Diseñar para A4 vertical y lectura ejecutiva rápida.
- Usar jerarquía editorial fuerte, espacios amplios y pocos colores simultáneos.
- Mantener una franja de color primario en el borde izquierdo de páginas interiores.
- Reservar el color de tinta para conclusiones, mensajes de cierre y contraste.
- Usar un tono de panel claro para tarjetas; evitar sombras y degradados en impresión.

## Tokens predeterminados

- Primario: `#d82032`
- Tinta: `#0b0d0e`
- Panel: `#f0f0f0`
- Texto secundario: `#666666`
- Blanco: `#ffffff`
- Positivo: `#328b3a`
- Cautela: `#d97706`
- Negativo: `#d82032`

Configurar `report.brand.primary`, `report.brand.ink` y `report.brand.panel` para adaptar el tema. Aceptar solo colores hexadecimales. Configurar `report.logo_path` con una ruta relativa al pack; el renderizador lo incrusta y nunca consulta recursos externos.

## Componentes

- Portada: logotipo opcional arriba a la derecha, título grande, periodo en primario y bloque cromático dominante.
- KPI: etiqueta primaria, número grande, delta y nota de base pequeños.
- Sección: título, introducción corta y paneles claros.
- Conclusión: banda de tinta con texto blanco y un máximo de tres ideas.
- Alerta: usar negativo solo para riesgo real; usar cautela para baja muestra o cobertura.
- Tabla: cabecera de tinta, cuerpo claro, números alineados a la derecha.
- Pie: fuente, fecha, clasificación y número de página.

## Privacidad de recursos

No empaquetar logotipos, fotografías, fuentes propietarias ni nombres de clientes dentro de la skill pública. Mantener esos recursos en el proyecto privado que genera el informe y verificar su autorización antes de publicar el resultado.

