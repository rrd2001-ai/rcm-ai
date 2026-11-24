
# Hospital RCM Agentic AI

An agentic AI service for a Hospital Revenue Cycle Management (RCM) platform. It uses a shared agent runtime and declarative YAML configurations to create specialized AI agents for insurance verification, authorization, billing audits, coding review, claims preparation, denial management, settlement reconciliation, and revenue intelligence.

## 1. Project Overview

Hospitals often manage insurance-related revenue cycle operations through manual processes involving multiple departments, insurers, and Third-Party Administrators (TPAs).

These processes can involve:

- Insurance and policy verification
- Preauthorization and cashless approvals
- Hospital bill and charge audits
- Clinical documentation and coding reviews
- Insurance claim preparation
- TPA queries and denial management
- Settlement reconciliation
- Insurance accounts receivable tracking
- Revenue leakage and performance analysis

The objective of this project is to introduce specialized AI agents that assist hospital RCM teams in performing these operations more efficiently, consistently, and transparently.

This repository contains the Agentic AI service, which is one component of the broader Hospital RCM platform.

## 2. Project Objectives

- Build multiple specialized AI agents using a single shared codebase.
- Use declarative YAML configurations to define agent personas, models, tools, and guardrails.
- Use a shared runtime instead of maintaining separate implementations for each agent.
- Integrate local LLM inference through Ollama.
- Provide controlled access to hospital RCM tools and services.
- Validate tool inputs using Pydantic schemas.
- Enforce agent-specific permissions and operational guardrails.
- Maintain human oversight for sensitive operations.
- Support local hospital server deployment.

## 3. Agent Architecture

The system currently defines eight specialized agents.

| Agent | Responsibilities |
|---|---|
| Insurance & Payer Verification | Verify patient insurance information, policy details, insurer and applicable TPA mappings. |
| Authorization & Payer Contract | Interpret payer contracts, tariffs, coverage conditions and preauthorization requirements. |
| Charge Capture & Billing Audit | Identify potential missed charges, duplicate charges and discrepancies between services and HMIS bills. |
| Coding & Documentation Review | Review clinical documentation, coding consistency and payer documentation requirements. |
| Claim Preparation & Submission | Validate claim information and prepare payer-specific claim packages. |
| Claims Follow-up & Denial Management | Track claim status, classify TPA queries, analyze denials and prepare follow-up drafts. |
| Settlement & Accounts Receivable | Reconcile claim amounts, settlement advice, payments and outstanding receivables. |
| Revenue Intelligence & Controls | Analyze revenue performance, denial trends, receivables and potential revenue leakage. |

Each agent has its own YAML configuration but uses the common runtime and shared tool infrastructure.

## 4. Architecture Approach

### Declarative Agent Configuration

Each agent is defined through a YAML configuration file.

Configurations specify:

- Agent identity and name
- Persona and objective
- LLM provider and model
- Temperature
- Allowed tools
- Operational guardrails
- Expected output schema

This separates agent behavior and configuration from the underlying runtime implementation.

### Shared Agent Runtime

The shared runtime is responsible for:

- Loading and validating agent configurations
- Creating configured agent instances
- Initializing the selected LLM
- Building agent system prompts
- Managing registered agents
- Providing controlled access to tools

### Shared Tool Registry

Agents use a common tool registry.

Each tool can define:

- Unique tool name
- Python handler
- Description
- Pydantic input schema
- Capability classification
- Required authorization guardrail, where applicable

The registry checks agent allowlists and validates tool inputs before execution.

Tool capability classifications:

- READ
- ANALYZE
- INTERNAL_WRITE
- EXTERNAL_ACTION
- FINANCIAL_ACTION

Capability metadata and enforcement are being developed incrementally. Sensitive actions must remain protected by application-level authorization and human approval.

## 5. Hospital RCM Integration Boundaries

The existing HMIS remains the source of truth for:

- Patient registration
- Admission and encounter records
- Clinical records
- Original hospital bills
- Payment collection

The RCM platform consumes relevant HMIS information and manages insurance-related workflows and claim lifecycle data.

The Agentic AI service is designed to:

- Read relevant HMIS information through approved integrations.
- Analyze bills, services, clinical documentation and insurance requirements.
- Prepare claim packages and internal worklists.
- Track claims, queries, denials and settlements.
- Provide revenue intelligence and recommendations.

The agents must not independently modify original HMIS records or hospital bills.

OCR processing is handled by a separate service. RCM agents consume extracted document data and document references rather than performing OCR themselves.

## 6. TPA Interaction and Human Oversight

TPA interaction is manual in the initial implementation.

Hospital staff remain responsible for:

- Calling or contacting TPAs
- Using external TPA portals
- Submitting claims and documents
- Sending query responses
- Submitting appeals
- Recording external decisions and outcomes

Agents can prepare checklists, internal tasks, response drafts and follow-up recommendations.

Human approval is required for sensitive external actions and financial decisions.

The system must never report an external action as completed unless its outcome has been recorded and verified.

## 7. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application development |
| FastAPI | API framework |
| Pydantic | Configuration and input validation |
| YAML | Declarative agent configuration |
| LangChain | LLM and tool integration |
| LangGraph | Agent workflow orchestration |
| Ollama | Local LLM inference |
| Qwen3 4B | Initial configured LLM |
| PostgreSQL | Planned application persistence |
| SQLAlchemy | Database access |
| Alembic | Database migrations |
| Pytest | Automated testing |

The initial development environment uses a MacBook Air M1 with 8 GB RAM. Agent execution will initially favor sequential execution to manage memory consumption.

## 8. Current Implementation Status

### Completed

- Initial project structure created.
- Eight agent YAML configurations created.
- Pydantic schemas for agent configurations implemented.
- YAML configuration loader implemented.
- Shared agent factory implemented.
- Ollama model integration initialized.
- Agent registry implemented.
- Shared tool registry implemented.
- Agent-specific tool allowlist checks implemented.
- Patient lookup input schema implemented.
- Tool argument validation implemented.
- Tool capability metadata introduced.
- Initial automated test suite: 23 tests passing.

### In Progress

- Enforce tool capability restrictions.
- Define input schemas for all RCM tools.
- Implement actual RCM tool handlers.
- Build the LangChain tool adapter.
- Connect tools to configured LLM instances.
- Implement agent execution workflows.
- Introduce execution audit logging.

### Planned

- PostgreSQL persistence and repository layer.
- LangGraph orchestration and state management.
- HMIS integration adapters.
- OCR service integration.
- Claim lifecycle workflows.
- Human approval workflows.
- API endpoints for agent execution.
- Integration and end-to-end testing.
- Local hospital deployment configuration.

## 9. Repository Structure

```text
app/
├── api/
├── agents/
│   ├── configs/
│   └── prompts/
├── core/
├── integrations/
│   └── hmis/
├── models/
├── repositories/
├── runtime/
│   ├── agent_factory.py
│   ├── agent_loader.py
│   ├── registry.py
│   └── state.py
├── schemas/
├── services/
├── tools/
│   ├── capabilities.py
│   ├── permissions.py
│   ├── registry.py
│   └── schemas/
└── workflows/

migrations/
storage/
tests/
├── agents/
├── integration/
└── unit/
```

## 10. Development Setup

### Prerequisites

- Python 3.12
- PostgreSQL
- Ollama
- Git

### Clone the repository

```bash
git clone https://github.com/rrd2001-ai/rcm-ai.git
cd rcm-ai
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Pull the initial model

```bash
ollama pull qwen3:4b
```

Ensure the Ollama service is running before initializing agents.

### Run tests

```bash
python -m pytest -v
```

## 11. Development Principles

- One codebase, multiple configured agents.
- Shared runtime and reusable tools.
- Configuration-driven agent specialization.
- Deterministic services for calculations and exact validations.
- LLMs for reasoning, interpretation and recommendations.
- Least-privilege tool access.
- Read-only HMIS integration by default.
- Human oversight for sensitive actions.
- Local deployment and local document storage.
- Auditable agent execution and tool usage.

## 12. Project Status

This repository is currently in the agent infrastructure and foundation development phase.

The eight agent configurations and shared runtime foundations are in place. The next development phase focuses on implementing typed RCM tools, enforcing capability-level permissions, integrating tools with Ollama, and building the actual agent execution workflows.

The presence of a configured tool name does not imply that its underlying hospital business logic has already been implemented.

