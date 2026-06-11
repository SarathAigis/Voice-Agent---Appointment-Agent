# Migration Checklist: Phase-based → Monorepo

This checklist tracks the migration from the legacy Phase 1-6 structure to the new monorepo.

## ✅ Completed

- [x] Root monorepo setup
  - [x] `package.json` with Turborepo
  - [x] `pnpm-workspace.yaml`
  - [x] `turbo.json` pipeline config
  - [x] `.prettierrc` for formatting
  - [x] `.eslintrc.js` for linting

- [x] Shared package (`packages/shared/`)
  - [x] TypeScript types
  - [x] Utility functions
  - [x] Vitest tests with 100% coverage
  - [x] ESLint configuration

- [x] CI/CD
  - [x] GitHub Actions workflow
  - [x] TypeScript testing
  - [x] Python testing (matrix)
  - [x] Lint + type-check + build pipeline

- [x] Documentation
  - [x] `AGENTS.md` guidelines
  - [x] `REFACTOR_GUIDE.md`
  - [x] `CONTRIBUTING.md`
  - [x] PR template
  - [x] This checklist

## 🔄 In Progress

### Dashboard Migration

- [ ] Move Phase6 dashboard to `packages/dashboard/`
  ```bash
  cp -r Phase6/dashboard/src packages/dashboard/
  cp Phase6/dashboard/next.config.js packages/dashboard/
  cp Phase6/dashboard/tailwind.config.ts packages/dashboard/
  ```

- [ ] Update imports to use `shared` package
  ```typescript
  // Replace local types with
  import { Call, Driver, Appointment } from 'shared'
  ```

- [ ] Add dashboard tests
  - [ ] Component tests with Vitest + React Testing Library
  - [ ] API client tests
  - [ ] Utility function tests

- [ ] Update dashboard `package.json` scripts
  - [ ] Verify `dev`, `build`, `test`, `lint` work
  - [ ] Add `type-check` script

### Python Services Migration

- [ ] Move voice agent to `services/voice-agent/`
  ```bash
  cp -r Phase6/agent services/voice-agent/agent
  cp Phase6/requirements.txt services/voice-agent/
  ```

- [ ] Move API server to `services/api/`
  ```bash
  cp -r Phase6/api services/api/
  ```

- [ ] Add Python service configs
  - [ ] `pyproject.toml` for each service
  - [ ] `pytest.ini` for test config
  - [ ] `.pylintrc` or `ruff.toml`

- [ ] Update Python imports
  - [ ] Fix relative imports
  - [ ] Add proper `__init__.py` files
  - [ ] Verify module structure

### Testing

- [ ] Run all tests and verify they pass
  ```bash
  pnpm test
  cd services/voice-agent && pytest
  cd services/api && pytest
  ```

- [ ] Add missing tests
  - [ ] Dashboard component tests
  - [ ] Shared package edge cases
  - [ ] Python service unit tests
  - [ ] Integration tests

### Documentation Updates

- [ ] Update main `README.md`
  - [ ] Add monorepo quick start
  - [ ] Update directory structure
  - [ ] Add new command examples

- [ ] Update package READMEs
  - [ ] `packages/dashboard/README.md`
  - [ ] `packages/shared/README.md`
  - [ ] `services/voice-agent/README.md`
  - [ ] `services/api/README.md`

- [ ] Update legacy phase READMEs
  - [ ] Add deprecation notices
  - [ ] Link to new structure

## 📋 TODO

### Configuration

- [ ] Add root `.nvmrc` or `.node-version`
- [ ] Add `.vscode/settings.json` with recommended settings
- [ ] Add `.vscode/extensions.json` with recommended extensions
- [ ] Add Husky for git hooks
  - [ ] Pre-commit: `pnpm lint-staged`
  - [ ] Pre-push: `pnpm test`

### Package Scripts

- [ ] Add `pnpm clean` to all packages
- [ ] Add `pnpm format:check` (CI)
- [ ] Add `pnpm format:fix` (local)
- [ ] Add `pnpm type-check` to all TS packages

### CI/CD Enhancements

- [ ] Add caching for pnpm store
- [ ] Add caching for Turborepo
- [ ] Add job for E2E tests
- [ ] Add job for security scanning
- [ ] Add automatic dependency updates (Dependabot)

### Shared Package Enhancements

- [ ] Add more shared types
  - [ ] API response types
  - [ ] Error types
  - [ ] Configuration types
- [ ] Add API client utilities
- [ ] Add validation schemas (Zod)
- [ ] Add constants

### Dashboard Enhancements

- [ ] Add E2E tests (Playwright)
- [ ] Add Storybook for components
- [ ] Add bundle size analysis
- [ ] Optimize for production

### Python Services

- [ ] Add Docker files
- [ ] Add health check endpoints
- [ ] Add API documentation (OpenAPI)
- [ ] Add performance tests

### Deployment

- [ ] Add Docker Compose for local development
- [ ] Add Kubernetes manifests (optional)
- [ ] Add Vercel config for dashboard
- [ ] Add deployment documentation

### Cleanup

- [ ] Archive Phase 1-6 to separate branch
- [ ] Remove duplicated code
- [ ] Update all import paths
- [ ] Remove unused dependencies

## 🎯 Success Criteria

Migration is complete when:

- [x] Root `pnpm install` works
- [x] `pnpm lint` passes for all packages
- [ ] `pnpm test` passes for all packages
- [ ] `pnpm build` succeeds for all packages
- [ ] `pnpm dev` starts all services
- [ ] CI/CD pipeline is green
- [ ] All documentation is updated
- [ ] No references to legacy Phase directories in active code

## 📊 Progress

- **Completed:** 35%
- **In Progress:** 40%
- **TODO:** 25%

---

**Last Updated:** 2026-06-11
