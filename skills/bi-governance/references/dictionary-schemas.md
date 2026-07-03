# Dictionary schemas

## Table

```yaml
table:
  name:
  display_name:
  domain:
  source_system:
  source_object:
  grain:
  primary_key:
  date_column:
  owner:
  refresh_frequency:
  used_for:
  status:
  description:
  columns:
  relationships:
  last_reviewed:
```

## Column

```yaml
column:
  table:
  name:
  display_name:
  data_type:
  business_meaning:
  technical_meaning:
  is_key:
  is_hidden:
  is_sensitive:
  allowed_values:
  examples:
  status:
```

## Measure

```yaml
measure:
  name:
  table:
  folder:
  domain:
  business_definition:
  technical_definition:
  dax:
  dependencies:
  used_for:
  filters_assumptions:
  owner:
  status:
  created_by:
  last_modified:
  validation_status:
```

## Relationship

```yaml
relationship:
  from_table:
  from_column:
  to_table:
  to_column:
  cardinality:
  filter_direction:
  active:
  business_reason:
  grain_validation:
  risk_level:
  status:
```

## Semantic model

```yaml
semantic_model:
  name:
  workspace:
  domain:
  fact_tables:
  dimension_tables:
  key_measures:
  reports_using_it:
  refresh_schedule:
  owner:
  certification_status:
  description:
  status:
```
