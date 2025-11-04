---
layout: default
title: Testing Overview
description: Overview of testing strategies for backend and frontend components
nav_order: 9
has_children: true
---

# Testing Overview

This guide provides an overview of testing strategies and implementation for both backend (pytest) and frontend (Vitest) components of the Financial Data Extractor.

## Overview

The project uses a comprehensive testing strategy across both backend and frontend:

### Backend Testing (pytest)

- API endpoints
- Middleware components
- Business logic
- Integration workflows
- Celery tasks

For detailed backend testing documentation, see **[Backend Testing](backend.html)**.

### Frontend Testing (Vitest + Playwright)

- **Unit Tests**: UI components, hooks, and utilities (Vitest)
- **Integration Tests**: Component + hooks integration (Vitest)
- **E2E Tests**: Complete user workflows (Playwright)
- **Coverage**: 100+ tests across all testing layers

For detailed frontend testing documentation, see **[Frontend Testing](frontend.html)**.

## Testing Principles

Our testing approach follows these core principles:

### 1. Test Behavior, Not Implementation

- Tests validate what the code does, not how it's implemented
- Focus on user-facing behavior and business requirements
- Tests remain stable during refactoring

### 2. Isolated Unit Tests

- Each unit test is independent and can run in any order
- External dependencies are mocked (databases, APIs, file systems)
- No side effects between tests
- Fast execution (< 1 second per test)

### 3. AAA Pattern (Arrange-Act-Assert)

All tests follow a consistent structure:

```python
def test_something():
    # Arrange - Set up test data and mocks
    mock_service.return_value = expected_data

    # Act - Execute the code under test
    result = function_under_test()

    # Assert - Verify the outcome
    assert result.status_code == 200
```

### 4. Comprehensive Coverage

- **Minimum 80% code coverage**, targeting 90%+
- Cover happy paths, error cases, and edge conditions
- Test boundary values and validation rules
- Include both positive and negative test cases

## Running Tests

### Backend Tests (pytest)

```bash
cd backend

# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-cov
```

For more backend testing commands, see **[Backend Testing](backend.html)**.

### Frontend Tests (Vitest + Playwright)

```bash
cd frontend

# Run unit and integration tests
npm test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Debug E2E tests
npm run test:e2e:debug
```

For more frontend testing commands, see **[Frontend Testing](frontend.html)**.

## Test Structure

### Backend Test Structure

```text
backend/
├── tests/
│   ├── fixtures/                 # Shared test fixtures
│   ├── integration/              # Integration tests (4 tests)
│   │   └── test_companies_integration.py
│   └── unit/                     # Unit tests (124 tests)
│       ├── api/                  # API unit tests (70 tests)
│       ├── db/                   # DB model tests (12 tests)
│       ├── schemas/              # Schema tests (18 tests)
│       ├── services/             # Service tests (13 tests)
│       └── utils/                # Utility tests (11 tests)
```

For detailed backend test structure, see **[Backend Testing](backend.html)**.

### Frontend Test Structure

```text
frontend/
├── tests/
│   ├── components/              # Unit tests (Vitest)
│   ├── integration/             # Integration tests (Vitest)
│   ├── e2e/                     # E2E tests (Playwright)
│   │   ├── home.spec.ts
│   │   ├── navigation.spec.ts
│   │   ├── error-pages.spec.ts
│   │   └── ...
│   ├── vitest.config.mjs
│   └── vitest.setup.ts
└── playwright.config.ts         # Playwright configuration
```

For detailed frontend test structure, see **[Frontend Testing](frontend.html)**.

## Testing Workflow

### Development

1. Write tests before or alongside code (TDD)
2. Run relevant tests frequently during development
3. Ensure all tests pass before committing
4. Keep tests fast and focused

### Pre-Commit

1. Run full test suite
2. Check coverage thresholds
3. Verify no regressions

### CI/CD

1. Run all tests on every push
2. Generate coverage reports
3. Block merges if tests fail or coverage drops

## Continuous Improvement

Our testing strategy continues to evolve:

1. ✅ **Unit tests** - Comprehensive backend and frontend coverage
2. ✅ **Integration tests** - Database workflows and component integration
3. ✅ **End-to-end tests** - Complete user workflows with Playwright
4. ⏳ **Performance tests** - Load and stress testing
5. ⏳ **Security tests** - Vulnerability scanning

## Additional Resources

- **[Backend Testing](backend.html)** - Complete pytest guide for FastAPI backend
- **[Frontend Testing](frontend.html)** - Complete Vitest guide for Next.js frontend
- **[API Reference](../api/reference.html)** - API documentation
- **[Task Processing](../infrastructure/tasks.html)** - Celery task testing
