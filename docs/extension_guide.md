# Extension Guide

## How to add a new mode

1. Add prompt template
2. Add response schema
3. Register mode in the mode registry
4. Expose route and CLI command if needed
5. Add formatter support if needed
6. Add tests
7. Update docs

## Required checks

- schema exists
- prompt exists
- mode is wired into API and CLI as intended
- tests cover basic success and failure behavior
