---
name: comensemos
description: Entry-point workflow for starting a new Power BI and Fabric modeling iteration. Use when the user wants Codex to begin a model, decide whether to start from Fabric, from known tables, or from an existing PBIX / TMDL, and route the work into the BI analytics-engineering flow.
---

# /comensemos

Trabaja en espanol por defecto.

## Purpose

Usa esta skill como puerta de entrada unica al sistema.

Su trabajo no es modelar en detalle, sino arrancar bien el proceso y encaminarlo hacia `BI_ENGINEER`.

## What this skill must do

1. Detectar el modo de inicio:
   - `fabric_discovery`: el usuario quiere que propongas tablas o fuentes desde Fabric.
   - `import_specific_tables`: el usuario ya te dice que tablas de Fabric quiere importar.
   - `model_existing_imports`: el usuario ya tiene tablas importadas en el PBIX o un TMDL y quiere revisar estrella, relaciones y medidas.
2. Crear o ubicar el proyecto del model factory en `projects/<project_slug>/`.
3. Asegurar que exista `brief.yaml`, `semantic_spec.yaml`, `artifacts/` y `logs/`.
4. Traducir la peticion libre del usuario a un `brief.yaml` inicial.
5. Validar el brief y generar un `semantic_spec.yaml` base si aun no existe o si esta vacio.
6. Continuar inmediatamente con el flujo de `BI_ENGINEER`.
7. Si se aplican cambios tecnicos, cerrar indicando que despues debe correr `BI_GOVERNANCE`.

## Routing rules

### Mode 1. fabric_discovery

Usa este modo cuando el usuario diga cosas como:

- "quiero que me propongas las tablas"
- "no se que fuentes coger"
- "busca en Fabric lo necesario"

Acciones:

- inspeccionar `dictionary/`
- revisar catalogo local y Fabric si esta disponible
- proponer dominio canonico y tablas candidatas
- despues pasar a `BI_ENGINEER`

### Mode 2. import_specific_tables

Usa este modo cuando el usuario ya diga que tablas usar.

Acciones:

- registrar las tablas pedidas en el brief
- marcar `source_domains` y restricciones
- pasar a `BI_ENGINEER` para import, modelado y medidas

### Mode 3. model_existing_imports

Usa este modo cuando el usuario diga que las tablas ya estan importadas o ya tiene un TMDL.

Acciones:

- inspeccionar primero el PBIX abierto o el TMDL disponible
- no volver a proponer import salvo que haga falta
- pasar a `BI_ENGINEER` para diagnostico, estrella, relaciones y medidas

## Required next step

Despues del intake, lee y sigue:

- `../bi-engineer/SKILL.md`

Si hubo cambios tecnicos o manuales relevantes que deban documentarse, termina recomendando:

- `../bi-governance/SKILL.md`

## Minimum output

Antes de pasar al flujo de `BI_ENGINEER`, deja claro:

- modo detectado
- proyecto elegido o creado
- objetivo de negocio resumido
- fuentes o tablas iniciales
- si el PBIX o TMDL ya trae imports o no
- supuestos criticos
