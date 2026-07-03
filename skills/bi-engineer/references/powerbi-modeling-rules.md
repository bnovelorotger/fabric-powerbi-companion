# Power BI modeling rules

## Naming

- Medidas visibles con nombres de negocio claros.
- Tablas nuevas de hechos con prefijo `fact_`.
- Tablas nuevas de dimensiones con prefijo `dim_`.
- Evitar nombres tecnicos para medidas visibles.
- Usar carpetas por dominio cuando aporten claridad.

## DAX

- Priorizar medidas simples y componibles.
- Usar `VAR` cuando mejore claridad.
- Usar `DIVIDE` para ratios.
- Controlar `BLANK`.
- Evitar `ALL` innecesario.
- No crear time intelligence sin revisar tabla calendario.

## Relationships

- Validar granularidad en ambos lados.
- Confirmar clave unica en la dimension.
- Confirmar cardinalidad y direccion de filtro.
- Revisar relaciones alternativas y riesgo de ambiguedad.
- Evitar `many-to-many` sin justificacion documentada.

## Power Query and upstream logic

- No romper pasos existentes.
- Validar tipos de datos.
- Preferir transformacion upstream en Fabric cuando vaya a reutilizarse.
- Evitar logica pesada en Desktop si debe vivir en Fabric.

## Safety

- No hacer cambios destructivos sin confirmacion.
- No renombrar objetos existentes sin advertir impacto.
