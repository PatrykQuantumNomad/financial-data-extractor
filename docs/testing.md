---
layout: default
title: Testing Overview
description: Overview of testing strategies for backend and frontend components
nav_order: 12
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

For detailed backend testing documentation, see **[Backend Testing](backend-testing)**.

### Frontend Testing (Vitest)

- UI components
- Layout components
- User interactions
- Component rendering

For detailed frontend testing documentation, see **[Frontend Testing](frontend-testing)**.

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

## Current Test Coverage

### Backend Tests

**Status:** ✅ **70 unit tests** covering API endpoints and middleware

- **Companies API** - 100% coverage (17 tests)
- **Documents API** - 100% coverage (17 tests)
- **Extractions API** - 100% coverage (15 tests)
- **Error Handler** - 100% coverage (13 tests)
- **Middleware** - 100% coverage (9 tests)

For detailed backend testing information, see **[Backend Testing](backend-testing)**.

### Frontend Tests

**Status:** ✅ **Coverage in progress**

For detailed frontend testing information, see **[Frontend Testing](frontend-testing)**.

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

For more backend testing commands, see **[Backend Testing](backend-testing)**.

### Frontend Tests (Vitest)

```bash
cd frontend

# Run tests
npm test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

For more frontend testing commands, see **[Frontend Testing](frontend-testing)**.

## Test Structure

### Backend Test Structure

```text
backend/
├── tests/
│   ├── fixtures/                 # Shared test fixtures
│   ├── integration/              # Integration tests (coming soon)
│   └── unit/                     # Unit tests
│       └── api/                  # API unit tests (70 tests)
```

For detailed backend test structure, see **[Backend Testing](backend-testing)**.

### Frontend Test Structure

```text
frontend/
├── src/
│   ├── components/
│   │   └── __tests__/           # Component tests
│   └── lib/
│       └── __tests__/           # Utility tests
```

For detailed frontend test structure, see **[Frontend Testing](frontend-testing)**.

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

1. ✅ **Unit tests** - Comprehensive backend coverage (70 tests)
2. 🔄 **Integration tests** - Database and external services (in progress)
3. ⏳ **End-to-end tests** - Complete workflows
4. ⏳ **Performance tests** - Load and stress testing
5. ⏳ **Security tests** - Vulnerability scanning

## Additional Resources

- [Backend Testing](backend-testing) - Complete pytest guide for FastAPI backend
- [Frontend Testing](frontend-testing) - Complete Vitest guide for Next.js frontend
- [API Reference](api-reference) - API documentation
- [Task Processing](task-processing) - Celery task testing
