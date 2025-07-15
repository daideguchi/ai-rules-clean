# Tests Directory

This directory contains all test files following the structure of src/.

## Structure
```
tests/
├── ai/           # Tests for src/ai/
├── integrations/ # Tests for src/integrations/
└── unit/         # Unit tests
```

## Testing Guidelines
- Mirror the src/ directory structure
- Use pytest for Python tests
- Test coverage target: >90%
- Integration tests in tests/integration/
- Unit tests organized by module