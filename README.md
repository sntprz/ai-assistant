# Asistente Inteligente de Conocimiento Corporativo — MVP 2 Semanas

## Resumen Ejecutivo

**Nombre del proyecto:** Asistente inteligente de conocimiento corporativo — MVP 2 semanas (RAG + 2 agents + Agent Manager)

### Visión Breve
Construir en 10 días laborables un MVP demostrable que permita a un usuario subir documentos, consultar sobre ellos con respuestas basadas en evidencia (RAG), y disponer de dos agentes orquestados por un Agent Manager capaz de ejecutar agentes de forma individual o encadenada (chain). El objetivo es validar el flujo end-to-end: ingestión → indexado → retrieval → generación → orquestación de agentes → trazabilidad y feedback. Todo debe ser reproducible localmente (Docker) y documentado para continuar su evolución.

### Por Qué es Importante

- Resuelve un problema real y transversal: encontrar y estructurar conocimiento dentro de documentos largos y poco estructurados.
- Enseña las habilidades prácticas más demandadas de un AI Engineer orientado a producto: integración con modelos, indexación vectorial, APIs, UI, orquestación (agents), evaluación y prácticas mínimas de MLOps.
- Entrega artefactos accionables (código reproducible, demo, métricas y backlog) que pueden escalarse en sprints posteriores.

### Valor Entregable en 2 Semanas

- Demo funcional (UI + API) que responde preguntas con evidencia y permite invocar dos agentes: Summarizer & Action-Extractor y Email Drafter.
- Agent Manager que registra, selecciona y encadena agentes, con trazabilidad y métricas básicas.
- Corpus inicial (~20 documentos) y pipeline reproducible para extracción, chunking, embeddings y FAISS local.
- Scripts de evaluación y criterios cuantitativos que demuestran el rendimiento mínimo aceptable.
- Código dockerizado y documentación para reproducir la demo en otra máquina.

## Alcance (Detallado)

### 1) Entregables Funcionales (qué SÍ está incluido)

#### Datos y Pipeline
- Corpus inicial de ~20 documentos (formatos txt/md; PDFs opcionales) con metadata básica (doc_id, title, author, date, category).
- Scripts reproducibles de ingestión: extracción de texto → limpieza → chunking (p. ej. 500 tokens por chunk) → generación de embeddings → indexado local en FAISS.
- Repository con estructura, requirements.txt/pyproject.toml, y Dockerfile.

#### Búsqueda y RAG
- Recuperador top-K sobre FAISS (función `retrieve(query, k)`).
- Componente RAG (función `answer_query(query)`) que:
  - Recupera top-K, construye prompt con contexto y metadatos.
  - Llama a un LLM (API o local) para generar respuesta.
  - Devuelve: `{ answer: str, sources: [{doc_id, chunk_id, score}], latency_ms }`.

#### Agentes y Agent Manager
- **Agent A (Summarizer & Action-Extractor)**: recibe doc_id o text y devuelve `{ summary: str, actions: [str], sources: [...] }`.
- **Agent B (Email Drafter)**: recibe `{ summary, actions, recipient_name, tone }` y devuelve `{ subject: str, body: str, suggested_edits: [str] }`.
- **Agent Manager (FastAPI)**:
  - **Endpoints:**
    - `GET /agents` — lista de agentes disponibles y metadatos.
    - `POST /run_agent/{name}` — ejecutar un agente con payload JSON.
    - `POST /run_chain` — ejecutar una cadena predefinida (ej.: Summarizer → Email Drafter).
    - `GET /traces/{trace_id}` — recuperar trazas de ejecución.
  - Registro de trazas (persistencia en SQLite o JSON): inputs, outputs, pasajes usados, tiempos, feedback.
  - Capacidad de chaining (pipeline de agentes) con manejo básico de errores y retries limitados.

#### UI / UX
- **Streamlit app** con:
  - Upload de documentos y listado / visualización.
  - Chat/QA: campo de consulta, muestra de respuesta + fuentes.
  - Panel de Agentes: botones Run Summarizer, Run Email Drafter, Run Chain.
  - Panel de trazas: ver inputs, pasajes recuperados, outputs y botón de feedback 👍/👎.
  - Dashboard de métricas básicas (latencia, thumbs-up ratio, success_rate por agente).

#### Observabilidad y Evaluación
- Logging de eventos (queries, agent runs, feedback) persistido.
- **Scripts de evaluación:**
  - Set de 20 Q/A para evaluar RAG.
  - 10 casos de prueba para cada agente (Agent A y B) con criterios de aceptación.
  - Reporte automático (CSV/JSON) con métricas: % respuestas con cita, latency p50/p95, thumbs-up ratio.

#### Empaquetado y Reproducibilidad
- Dockerfile que construye una imagen con backend + UI ejecutables localmente.
- README y playbook: instrucciones para levantar local, cómo añadir docs y ejecutar demo.
- Issues y backlog priorizado para siguientes pasos (Pinecone, deploy cloud, agents adicionales, fine-tuning).

### 2) Fuera de Alcance (qué NO está incluido en este sprint)

- Despliegue en Kubernetes, infra como código (Terraform) o cloud managed vector DB (a excepción de pruebas opcionales si hay tiempo).
- Integración con servicios de correo real o ticketing (solo mocks/simulación).
- Fine-tuning a escala (solo experimentos ligeros si hay tiempo).
- Hardening de seguridad empresarial, auditoría legal o cumplimiento GDPR completo (se aplican prácticas mínimas: tokens, no exponer datos reales).

### 3) Suposiciones Operativas (qué damos por hecho)

- Tendrás acceso a una máquina con Python 3.9+, Docker, y espacio suficiente para instalar dependencias de modelos (o una API key de OpenAI/Azure si prefieres external LLM).
- No se utilizarán datos sensibles reales en el corpus inicial; si decides usar datos reales, tú aseguras permisos y anonimización.
- Las latencias objetivo (ej. p95 < 3s) son realistas solo con modelos/modo API pequeños; en local, depende del hardware.
- El alcance de los agentes está limitado a la generación de texto y estructuras JSON; integración con sistemas externos queda para sprints posteriores.

## Objetivos (Extensos, Medibles y Ordenados)

### 1) Objetivos del Proyecto (High Level)

- **Entregar un MVP funcional**: Desplegar localmente (Docker) una aplicación que permita upload de documentos, QA con evidencia y ejecución de agentes (A y B) orquestados por un Agent Manager.
- **Proveer trazabilidad**: Cada ejecución de agente y consulta debe quedar registrada con inputs, pasajes recuperados, outputs, tiempos y feedback.
- **Habilitar evaluación reproducible**: Scripts y data para correr benchs automáticos y cuantificar desempeño.
- **Documentar y entregar backlog**: README, playbook de operación mínima y lista priorizada de mejoras.

### 2) Objetivos Operacionales y Métricas (SMART)

#### MVP Operativo Localmente
- **Meta**: App levantada y accesible en localhost con Docker.
- **Éxito**: ✅ `docker run` arranca backend + UI y demo reproducible en ≤ 5 min.

#### Agent A: Summarizer & Action-Extractor
- **Meta**: Entregar summary (1–3 frases) y lista de actions (0–10 items) con fuentes.
- **Medida**: En conjunto de pruebas (n=10), en ≥ 8/10 casos se considera output aceptable por criterio humano (claridad + relevancia).
- **KPI adicional**: % de outputs con al menos una fuente citada ≥ 90%.

#### Agent B: Email Drafter
- **Meta**: Generar email profesional (subject + body) que incluya contexto y acciones.
- **Medida**: En n=10 casos, ≥ 8/10 emails considerados utilizables sin grandes correcciones (evaluación humana).
- **KPI adicional**: 80% de emails deben mencionar al menos 1 acción extraída.

#### Chain Summarizer → Email
- **Meta**: Ejecutar chain desde UI y obtener email final en ≤ 5 minutos por usuario novel.
- **Medida**: Demo reproducible; test end-to-end exitoso en 5 ejecuciones consecutivas.

#### RAG (QA con Evidencia)
- **Meta**: Responder preguntas citando pasajes.
- **Medida**: % respuestas con cita correcta (la cita contiene la información relevante) ≥ 80% en set de 20 Q/A.

#### Métricas de Rendimiento
- **Latency** (target realista en local con modelos pequeños/API): p50 ≤ 500 ms para retrieval; p95 ≤ 3 s para RAG completo. (Si usas API cloud, documentar facturación estimada).
- **Feedback positive ratio**: ≥ 70% thumbs-up en pruebas internas (n≥30 interacciones).

#### Trazabilidad y Logging
- **Meta**: Cada run produce un registro con campos mínimos (see sección DB schema).
- **Medida**: 100% de ejecuciones (en prueba) quedan registradas y consultables.

### 3) Objetivos de Aprendizaje (Personales y Concretos)

Al completar el sprint deberías ser capaz de:

- Explicar en detalle y ejecutar el flujo RAG: chunking → embeddings → indexado → retrieval → prompt design → generación con evidencia.
- Construir y desplegar una API que expone agentes y orquesta chains (conceptos de agent manager).
- Diseñar prompts efectivos para extracción de acciones y generación de correos.
- Implementar y analizar métricas básicas de evaluación (precision-like, coverage, feedback).
- Dockerizar una aplicación y preparar instrucciones para correrla reproduciblemente.

### 4) Definition of Done (DoD) — Criterios de Aceptación Técnicos

El sprint se considerará completado si TODAS estas condiciones se cumplen:

- [x] **Código**: Repo con estructura clara, requirements.txt o pyproject.toml, y Dockerfile.
- [x] **Ejecución**: `docker build` + `docker run` levanta la UI y backend en localhost.
- [x] **Funcionalidad RAG**: Endpoint `/query` o la UI responde preguntas y devuelve `{answer, sources}`.
- [x] **Agentes**:
  - `POST /run_agent/summarizer` y `POST /run_agent/email` funcionan con payloads documentados.
  - `POST /run_chain` devuelve resultado completo con trazas.
- [x] **UI**: Streamlit con upload, QA, panel agentes, trazas y feedback.
- [x] **Persistencia**: Logs/trazas almacenados en SQLite/JSON y consultables por trace_id.
- [x] **Evaluación**: Scripts que generan reporte con métricas (Q/A coverage, agent success counts).
- [x] **Documentación**: README con pasos para reproducir demo y playbook de operación (cómo añadir docs, cómo evaluar).
- [x] **Backlog**: Issues priorizados para mejoras críticas (despliegue cloud, Pinecone, retries avanzados, etc.).
- [x] **Demo**: Grabación o script para demo que ejecuta chain y muestra resultados.

## Especificaciones Técnicas

### A. Esquemas de Datos / Formatos

## A. Esquemas de Datos / Formatos

### Documento (entrada)

- **doc_id** (str, único)
- **title** (str)
- **author** (str / opcional)
- **date** (ISO 8601 / opcional)
- **category** (str; e.g., "HR", "IT", "Policy")
- **content** (str) — texto extraído

### Chunk / Passage (generado)

- **chunk_id** (str) — {doc_id}#chunk_{n}
- **doc_id** (str)
- **text** (str)
- **start_char** (int)
- **end_char** (int)
- **embedding** (float[]) — vector embedding

### RAG Response

```json
{ 
  "answer": str, 
  "sources": [ 
    { 
      "doc_id": str, 
      "chunk_id": str, 
      "score": float 
    } 
  ], 
  "latency_ms": int 
}
```

### Agent A Output (Summarizer)

```json
{ 
  "summary": str, 
  "actions": [ 
    { 
      "id": int, 
      "action": str, 
      "confidence": float, 
      "sources": [...] 
    } 
  ], 
  "sources": [...] 
}
```

### Agent B Output (Email Drafter)

```json
{ 
  "subject": str, 
  "body": str, 
  "suggested_edits": [str], 
  "sources": [...] 
}
```

### Trace Record (persistencia)

- **trace_id** (uuid)
- **timestamp** (ISO)
- **type** ("query" | "agent_run" | "chain")
- **user_id** (optional)
- **input** (JSON)
- **retrieved_passages** ([{doc_id, chunk_id, score}])
- **agent_outputs** (JSON)
- **latency_ms** (int)
- **feedback** (null | "up" | "down")
- **notes** (optional)

## B. Endpoints API (FastAPI Minimal Spec)

- `GET /health` — devuelve status.
- `POST /ingest` — payload `{ doc_id, title, content, metadata }` → ingesta + chunking + embeddings + indexado. Respuesta: `{ ok: true, doc_id }`.
- `GET /documents` — lista docs.
- `GET /documents/{doc_id}` — obtiene doc y chunks.
- `POST /query` — payload `{ query: str, top_k: int (opt) }` → devuelve RAG response.
- `GET /agents` — listado agentes `{ name, description, inputs_schema }`.
- `POST /run_agent/{name}` — ejecutar agente, payload depende del agente; devuelve trace_id.
- `POST /run_chain` — payload `{ chain: "summarize_email", doc_id, recipient, tone }` → devuelve trace_id y final outputs.
- `GET /traces/{trace_id}` — recuperar trace.
- `POST /feedback/{trace_id}` — `{ feedback: "up"|"down", comment: str }`.

*(Cada endpoint debe validar payload y devolver códigos HTTP estándar.)*

## C. Prompt Design (esquemas, no verbatim para evitar sesgo)

### RAG Prompt Template (answer_query)

**Context:** "You are an assistant. Use the following excerpts to answer the user question. Provide a concise answer and reference the excerpts used."

Insert top-K passages each with `[[source: doc_id#chunk_id]] TEXT`.

**Instruction:** "Answer in max N tokens. Start with the answer, then a section Sources: listing doc_id#chunk_id and short excerpt if necessary."

### Agent A Prompt (summarizer)

**Provide:** title, relevant passages (top-K), user instruction: "Create a short (3–4 sentence) summary and extract a list of actionable items (imperative sentences). For each action include reference(s) to sources. Output as JSON: `{ summary: str, actions: [{action_id, text, sources: [] }] }`."

### Agent B Prompt (email drafter)

**Inputs:** `{ summary, actions }`, plus recipient_name, tone and optional subject_hint.

**Instruction:** "Write a professional email with subject and body. Include context (1–2 lines), bullet points for actions, and a polite closing line. Keep email length under X words. Output as JSON `{ subject, body }`."

*(Durante el sprint debes iterar prompts y registrar resultados en un pequeño experimento para elegir la mejor plantilla.)*

## D. Métricas y Definición Operacional (precisas)

- **Coverage de cita (RAG):** % de respuestas que contienen al menos una fuente entre las top-K recuperadas. Fórmula: `count(responses_with_source) / total_responses`. **Objetivo:** ≥ 80%.

- **Agent A success rate:** % casos (de 10) evaluados manualmente como "summary + actions aceptables". **Objetivo:** ≥ 80% (8/10).

- **Agent B success rate:** % emails (de 10) aceptables sin grandes cambios. **Objetivo:** ≥ 80%.

- **Latency retrieval:** p50, p95 en ms. **Objetivo:** retrieval p95 ≤ 500 ms (local con embeddings cached).

- **Latency RAG end-to-end:** p50/p95. **Objetivo:** p95 ≤ 3 s (depende HW/API).

- **Feedback positive ratio:** thumbs_up / total_feedbacks. **Objetivo:** ≥ 70% durante pruebas internas.

- **Error rate:** % requests con error HTTP 5xx. **Objetivo:** < 1% en pruebas.

## E. Casos de Prueba Mínimos (para evaluación automática/manual)

### RAG (20 queries)

- 10 preguntas factuales (existente en documents).
- 10 preguntas formadas por contexto (requieren sintetizar múltiples chunks).
- **Métrica:** coverage de cita y evaluación humana por utilidad.

### Agent A (10 casos)

- 5 docs con procedimientos (extraer actions concretos).
- 3 docs narrativos (resumir y extraer acciones implícitas).
- 2 docs corta/no relevante (expectativa: indicar "No suficiente info").

### Agent B (10 casos)

- Entradas con summary + 3–5 actions → generar email con subject y bullets.
- Variación en tone (formal, informal).
- Cada caso tendrá un archivo con input.json y expected_heuristics para facilitar revisión.

## Plan de Evaluación y Ciclo de Mejora (Evaluation-Driven Development)

1. **Before start:** definir métricas (ya las tienes), crear datasets de evaluación (Q/A + agent tests).

2. **Durante el sprint:** ejecutar benchs cada vez que cambies prompt o chunking; documentar cambios (W&B o simple CSV).

3. **Post-implementación:** correr evaluación completa y generar reporte con: coverage, latencias, success rates, ejemplos de failure.

4. **Retro y priorización:** con resultados, crear backlog de mejoras (ej.: mejorar chunking, cambiar modelo de embeddings, ajustar prompts, añadir verificación humana).

5. **Loop:** priorizar top-3 mejoras para siguiente sprint de 1–2 semanas.

## Riesgos, Impacto y Mitigaciones (completo)

### Riesgo: No disponer de API Key para LLM o coste demasiado alto
- **Impacto:** retraso o latencias mayores.
- **Mitigación:** usar modelos locales pequeños (HF), reducir tamaño del corpus, usar caching agresivo.

### Riesgo: Hallucinations (respuestas incorrectas) en agentes
- **Impacto:** outputs no confiables.
- **Mitigación:** exigir siempre sources en outputs; si confidence baja, marcar para revisión humana; mostrar frases de evidencia completas.

### Riesgo: FAISS/embeddings consumen mucha RAM en máquina limitada
- **Impacto:** OOM y fallos.
- **Mitigación:** usar corpus reducido, embeddings de dimensión menor, persistir index en disco o usar Pinecone si hay tiempo.

### Riesgo: Chain largo produce latencias altas
- **Impacto:** mala UX.
- **Mitigación:** ejecutar agents de forma asíncrona con feedback de estado; optimizar prompt y caching.

### Riesgo: Errores en parsing (PDFs) generan mala indexación
- **Mitigación:** empezar con txt/markdown; agregar soporte PDF si sobra tiempo.

### Riesgo: Requisitos de seguridad/compliance si se usa data real
- **Mitigación:** anonimizar datos y no subir información sensible en el sprint; documentar políticas.

## Runbook Mínimo (qué hacer si algo falla durante demo)

### Backend no responde:
- Comprobar contenedor Docker `docker ps`; logs `docker logs <container>`.
- Si proceso crashed, ver stack trace y reiniciar `docker restart`.

### Index no encontrado / FAISS error:
- Ejecutar `python scripts/ingest.py --reindex` para regenerar index.
- Ver espacio disco/RAM.

### LLM API rate limit / 401:
- Verificar variable de entorno `OPENAI_API_KEY`.
- Si hay rate limit, activar modo de fallback a modelo local o mostrar mensaje al usuario.

### Agent chain falla:
- Consultar trace `GET /traces/{trace_id}`.
- Si error por timeout en LLM, reintentar con modo asíncrono o fallback (shorter prompt).

### Demostración en fallo:
- Tener vídeo pre-grabado (fallback) y explicar issues.