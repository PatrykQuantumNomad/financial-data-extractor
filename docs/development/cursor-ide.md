---
layout: default
title: Cursor IDE Configuration
description: Cursor rules, VS Code settings, debug configurations, and development tasks
parent: Development Tools
nav_order: 1
---

# Cursor IDE Configuration

This guide explains the Cursor IDE and VS Code configuration for the Financial Data Extractor project, including AI assistant rules, editor settings, debug configurations, and development tasks.

## Overview

The project uses **Cursor IDE**, an AI-powered code editor built on VS Code, with custom rules and configurations to:

- Guide AI-assisted code generation with domain-specific rules
- Provide consistent formatting and linting across Python and TypeScript
- Enable easy debugging for FastAPI, Celery workers, and Next.js
- Streamline common development tasks

## Cursor Rules

Cursor uses rule files in the `.cursor/rules/` directory to guide AI behavior during code generation and assistance. These rules ensure consistency, follow best practices, and align with project-specific requirements.

### Rule Files Overview

The project includes **15 rule files** organized by domain and layer:

#### Global Rules

- **[Global Coding Guidelines](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/00-global.mdc)** (`00-global.mdc`)
  - Always applied to all code generation
  - General principles: SOLID, DRY, KISS
  - Naming conventions, function design, error handling
  - Code organization and formatting standards

- **[Context7 Documentation Integration](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/01-context7-doc.mdc)** (`01-context7-doc.mdc`)
  - Always applied for documentation lookup
  - Automatically fetches latest library documentation
  - Ensures accurate API references and examples

#### Backend Rules

- **[FastAPI Backend Architecture](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/10-backend-fastapi.mdc)** (`10-backend-fastapi.mdc`)
  - FastAPI best practices and patterns
  - Async/await patterns, dependency injection
  - Microservices and serverless architecture
  - Applied to: `backend/**/*.py`, `services/**/*.py`

- **[Celery Task Processing](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/11-backend-celery.mdc)** (`11-backend-celery.mdc`)
  - Celery task design and configuration
  - Task queues, retries, error handling
  - Applied to: `backend/**/*.py` (task-related files)

- **[Database Architecture](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/12-backend-db.mdc)** (`12-backend-db.mdc`)
  - SQLAlchemy patterns, connection pooling
  - Repository pattern, migrations
  - Applied to: `backend/**/*.py` (database-related files)

- **[API Design](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/13-api-design.mdc)** (`13-api-design.mdc`)
  - REST API design principles
  - Endpoint naming, JSON shape, HTTP semantics
  - Error handling (RFC 7807 Problem Details)
  - Applied to: `backend/**/*.py` (API endpoints)

#### Frontend Rules

- **[Next.js & Tailwind](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/20-frontend-nextjs-tailwind.mdc)** (`20-frontend-nextjs-tailwind.mdc`)
  - Next.js 15 App Router patterns
  - Tailwind CSS 4.0 usage
  - React 19 best practices
  - Applied to: `frontend/**/*.{ts,tsx,js,jsx}`

- **[UI Components](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/21-ui.mdc)** (`21-ui.mdc`)
  - shadcn/ui component usage
  - UI/UX best practices
  - Tailwind CSS patterns
  - Applied to: `frontend/**/*.{ts,tsx,js,jsx}` (UI components)

#### Infrastructure Rules

- **[Containerization](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/30-containerization.mdc)** (`30-containerization.mdc`)
  - Docker and Docker Compose patterns
  - Container orchestration
  - Applied to: `**/Dockerfile`, `**/docker-compose*.yml`, `infrastructure/**`

- **[Monitoring & Observability](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/40-monitoring.mdc)** (`40-monitoring.mdc`)
  - Prometheus metrics, Grafana dashboards
  - Logging and observability patterns
  - Applied to: Monitoring configuration files

#### Quality & Documentation

- **[Testing & Quality](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/50-testing-quality.mdc)** (`50-testing-quality.mdc`)
  - Pytest patterns for backend
  - Vitest patterns for frontend
  - Test coverage and quality standards
  - Applied to: `**/*test*.py`, `**/*.test.{ts,tsx}`, `**/*.spec.{ts,tsx}`

- **[Documentation](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/60-documentation.mdc)** (`60-documentation.mdc`)
  - Markdown documentation standards
  - API documentation patterns
  - Applied to: `docs/**/*.md`, `**/*.md`

#### Domain-Specific Rules

- **[PDF Processing](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/70-pdf-processing.mdc)** (`70-pdf-processing.mdc`)
  - PDF scraping and classification
  - PyMuPDF, pdfplumber patterns
  - Applied to: PDF processing code

- **[LLM Extraction](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/71-llm-extraction.mdc)** (`71-llm-extraction.mdc`)
  - OpenRouter integration
  - LLM prompt engineering
  - Structured extraction patterns
  - Applied to: LLM extraction code

- **[Financial Normalization](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.cursor/rules/72-financial-normalization.mdc)** (`72-financial-normalization.mdc`)
  - Financial data normalization
  - Line item deduplication
  - Multi-year compilation
  - Applied to: Normalization and compilation code

### How Rules Work

1. **Auto-Attachment**: Rules with `autoAttach: true` are automatically applied when editing matching files
2. **Glob Patterns**: Rules with `globs` are applied when files match the pattern
3. **Always Applied**: Rules with `alwaysApply: true` are always active
4. **Requestable**: Some rules can be explicitly requested during conversations

### Viewing Rules in Cursor

- Rules are visible in the Cursor sidebar under "Rules"
- You can request specific rules during AI conversations
- Rules are automatically applied based on file context

For the complete rule files, see the [`.cursor/rules/` directory on GitHub](https://github.com/PatrykQuantumNomad/financial-data-extractor/tree/main/.cursor/rules).

## VS Code / Cursor Settings

The `.vscode/` folder contains workspace-specific settings for Cursor (which is based on VS Code).

### `settings.json`

The workspace settings configure editor behavior, formatting, and language-specific options:

#### Editor Configuration

- **Format on Save**: Enabled for all file types
- **Tab Size**: 2 spaces (JavaScript/TypeScript), 4 spaces (Python)
- **Ruler**: 100 characters (helps maintain line length)
- **Word Wrap**: Enabled for Markdown (80 columns)

#### Language-Specific Settings

**Python:**
- **Formatter**: Ruff (`charliermarsh.ruff`)
- **Format on Save**: Enabled
- **Auto-fix**: Ruff fixes applied on save
- **Interpreter**: Points to `backend/.venv/bin/python`
- **Testing**: Pytest enabled for backend directory

**TypeScript/JavaScript:**
- **Formatter**: Prettier (`esbenp.prettier-vscode`)
- **Format on Save**: Enabled
- **Auto-imports**: Enabled with relative paths
- **Import Organization**: Auto-organize on save

**Markdown:**
- **Word Wrap**: 80 columns
- **Quick Suggestions**: Disabled (reduces noise)

#### File Management

- **Encoding**: UTF-8
- **Line Endings**: LF (Unix-style)
- **Final Newline**: Inserted automatically
- **Trailing Whitespace**: Trimmed automatically

#### Excluded Files

The following patterns are excluded from file explorer and search:

- `node_modules`
- `.next` (Next.js build output)
- `__pycache__`
- `.mypy_cache`
- `*.pyc`

**Full Settings File**: [`.vscode/settings.json`](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.vscode/settings.json)

### `launch.json`

Debug configurations for running and debugging the application:

#### Debug Configurations

1. **Python Debug (FastAPI)**
   - Debugs the FastAPI backend server
   - Entry point: `backend/run.py`
   - Environment: Loads `.env` file
   - Python path: Includes backend directory

2. **Python Debug (Celery Worker)**
   - Debugs Celery worker with all queues
   - Queues: `scraping`, `extraction`, `compilation`, `orchestration`, `default`
   - Useful for debugging background tasks

3. **Python Debug (Celery Worker - Single Queue)**
   - Debugs Celery worker with only `default` queue
   - Useful for focused task debugging

4. **Next.js: Debug Frontend**
   - Debugs the Next.js frontend application
   - Runs `npm run dev` in debug mode
   - Integrated terminal for output

**Usage:**

1. Open the Run and Debug panel (⌘⇧D / Ctrl+Shift+D)
2. Select a configuration from the dropdown
3. Press F5 or click the green play button
4. Set breakpoints in your code
5. The debugger will pause at breakpoints

**Full Launch File**: [`.vscode/launch.json`](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.vscode/launch.json)

### `tasks.json`

VS Code tasks for common development operations:

#### Available Tasks

1. **Jekyll: Serve**
   - Runs Jekyll server for documentation
   - Command: `bundle exec jekyll serve --livereload`
   - Working directory: `docs/`
   - Background task (runs continuously)
   - Auto-detects when server is ready

**Usage:**

1. Open Command Palette (⌘⇧P / Ctrl+Shift+P)
2. Type "Tasks: Run Task"
3. Select "Jekyll: Serve"
4. Task runs in background terminal
5. Documentation available at `http://localhost:4000`

**Full Tasks File**: [`.vscode/tasks.json`](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.vscode/tasks.json)

**For detailed Jekyll documentation development, see [GitHub Pages Documentation](github-pages.html).**

### `extensions.json`

Recommended VS Code extensions for the project:

- **Prettier** (`esbenp.prettier-vscode`) - Code formatter
- **Ruff** (`charliermarsh.ruff`) - Python linter and formatter

VS Code will prompt you to install these extensions when you open the workspace.

**Full Extensions File**: [`.vscode/extensions.json`](https://github.com/PatrykQuantumNomad/financial-data-extractor/blob/main/.vscode/extensions.json)

## Development Workflow

### Using Cursor Rules

1. **Automatic Application**: Rules are automatically applied based on file context
2. **Explicit Requests**: You can request specific rules in AI conversations:
   - "Use the FastAPI rules"
   - "Follow the testing guidelines"
   - "Apply the financial normalization rules"

3. **Rule Override**: Rules can be temporarily overridden by explicitly requesting different behavior

### Debugging

1. **Backend Debugging**:
   - Use "Python Debug (FastAPI)" to debug API endpoints
   - Set breakpoints in endpoint handlers, services, or repositories
   - Variables and call stack are visible in debug panel

2. **Celery Task Debugging**:
   - Use "Python Debug (Celery Worker)" to debug background tasks
   - Set breakpoints in task functions
   - Monitor task execution in real-time

3. **Frontend Debugging**:
   - Use "Next.js: Debug Frontend" to debug React components
   - Set breakpoints in component code
   - Use React DevTools for component inspection

### Formatting

- **Automatic**: Files are formatted on save
- **Manual**: Use "Format Document" (⇧⌥F / Shift+Alt+F)
- **Pre-commit**: Consider adding pre-commit hooks to ensure formatting

### Testing

- **Backend**: Pytest is configured in `settings.json`
- **Frontend**: Vitest is configured in `package.json`
- **Run Tests**: Use terminal or VS Code test runner

## Customization

### Adding New Rules

1. Create a new `.mdc` file in `.cursor/rules/`
2. Add front matter with metadata:
   ```yaml
   ---
   description: Rule description
   globs: ["**/*.py"]
   autoAttach: true
   ---
   ```
3. Write rule content in Markdown
4. Rules are automatically available in Cursor

### Modifying Settings

- Edit `.vscode/settings.json` for workspace-specific settings
- Settings apply to all users of the workspace
- Personal settings can override workspace settings

### Adding Debug Configurations

1. Edit `.vscode/launch.json`
2. Add a new configuration object
3. Follow VS Code debug configuration schema
4. Configuration appears in Run and Debug dropdown

## Best Practices

1. **Use Rules Consistently**: Let AI rules guide code generation for consistency
2. **Debug Early**: Use debug configurations to catch issues early
3. **Format on Save**: Keep code formatted automatically
4. **Review Rule Changes**: Ensure rule updates align with project goals
5. **Document Custom Rules**: If adding custom rules, document their purpose

## Additional Resources

- [Cursor IDE Documentation](https://cursor.sh/docs)
- [VS Code Debugging Guide](https://code.visualstudio.com/docs/editor/debugging)
- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [Cursor Rules Documentation](https://cursor.sh/docs/rules)

## Related Documentation

- [Getting Started Guide](../getting-started/installation.html) - Initial setup instructions
- [Backend Architecture](../backend/architecture.html) - Backend code structure
- [Frontend Architecture](../frontend/architecture.html) - Frontend code structure
- [Testing Guide](../testing/index.html) - Testing strategies and setup
