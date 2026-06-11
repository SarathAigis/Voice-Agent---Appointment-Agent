# Refactoring Guide

## What Changed

The project has been refactored from a multi-phase structure to a proper **pnpm monorepo** following the AGENTS.md guidelines.

## New Structure

```
voice-agent-appointment-scheduler/
├── packages/
│   ├── dashboard/          # Next.js dispatcher dashboard
│   └── shared/             # Shared TypeScript types and utilities
├── services/
│   ├── voice-agent/        # Python voice agent (Phase 1-5 backend)
│   └── api/                # FastAPI server
├── Phase1-6/               # Legacy phase-based code (kept for reference)
├── .github/workflows/      # CI/CD pipelines
├── package.json            # Root monorepo config
├── pnpm-workspace.yaml     # pnpm workspace definition
├── turbo.json              # Turborepo pipeline config
└── AGENTS.md               # Development guidelines
```

## Key Changes

### 1. Monorepo Setup
- ✅ **pnpm workspaces** for dependency management
- ✅ **Turborepo** for build orchestration
- ✅ **Shared package** for common types/utilities

### 2. Package Structure

**packages/dashboard** - Frontend
- Next.js 14 with TypeScript
- Vitest for testing
- ESLint + Prettier
- Uses `shared` package for types

**packages/shared** - Common code
- TypeScript types
- Utility functions
- Shared across dashboard and API

**services/voice-agent** - Backend
- Python voice agent
- pytest for testing
- black + ruff for linting

**services/api** - API Server
- FastAPI
- Webhooks and endpoints

### 3. Development Workflow

**Install dependencies:**
```bash
pnpm install
```

**Run everything:**
```bash
pnpm dev  # Runs all services in parallel
```

**Run specific package:**
```bash
pnpm --filter dashboard dev
pnpm --filter voice-agent dev
```

**Testing:**
```bash
pnpm test                    # All packages
pnpm turbo run test --filter dashboard
```

**Linting:**
```bash
pnpm lint                    # All packages
pnpm --filter shared lint
```

### 4. CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:
- ✅ Runs lint, type-check, test, build
- ✅ Separate jobs for TypeScript and Python
- ✅ Matrix testing for Python 3.11 and 3.12

### 5. PR Guidelines (from AGENTS.md)

**Title format:**
```
[dashboard] Add real-time call monitoring
[shared] Add phone number formatting utility
[voice-agent] Fix voicemail detection
```

**Before committing:**
```bash
pnpm lint   # Must pass
pnpm test   # Must pass
```

## Migration Path

### For Development

1. **Use the new structure:**
   ```bash
   cd packages/dashboard
   pnpm dev
   ```

2. **Add shared types:**
   ```typescript
   import { Call, Driver } from 'shared'
   ```

3. **Follow testing patterns:**
   ```bash
   # Run specific test
   pnpm vitest run -t "formatDuration"
   
   # Watch mode
   pnpm test:watch
   ```

### For Deployment

**Old way (Phase 6):**
```bash
cd Phase6/dashboard
npm install
npm run build
```

**New way (Monorepo):**
```bash
pnpm install
pnpm build --filter dashboard
```

## Benefits

### Before (Phase-based)
- ❌ Duplicated dependencies across phases
- ❌ No shared code between phases
- ❌ Manual coordination between services
- ❌ Inconsistent testing approaches
- ❌ No CI/CD

### After (Monorepo)
- ✅ Shared dependencies (faster installs)
- ✅ `shared` package for common code
- ✅ Turborepo orchestration
- ✅ Consistent testing (Vitest for TS, pytest for Python)
- ✅ Automated CI/CD
- ✅ Follows AGENTS.md guidelines

## Commands Cheat Sheet

```bash
# Development
pnpm dev                                # Run all services
pnpm --filter dashboard dev             # Run dashboard only
pnpm --filter voice-agent dev           # Run voice agent only

# Building
pnpm build                              # Build all packages
pnpm turbo run build --filter dashboard # Build dashboard

# Testing
pnpm test                               # Test all packages
pnpm vitest run -t "test name"          # Run specific test

# Linting
pnpm lint                               # Lint all packages
pnpm --filter shared lint               # Lint shared package

# Adding dependencies
pnpm add axios --filter dashboard       # Add to dashboard
pnpm add -D vitest --filter shared      # Add dev dependency

# Finding packages
pnpm dlx turbo run where dashboard      # Show package location

# Cleaning
pnpm clean                              # Clean all build artifacts
```

## Next Steps

1. **Move Phase 6 dashboard code to packages/dashboard**
   ```bash
   cp -r Phase6/dashboard/src packages/dashboard/
   ```

2. **Update imports to use shared package**
   ```typescript
   // Before
   interface Call { ... }
   
   // After
   import { Call } from 'shared'
   ```

3. **Add tests following Vitest patterns**
   ```typescript
   import { describe, it, expect } from 'vitest'
   ```

4. **Update CI/CD as needed**

## Legacy Code

Phase 1-6 directories are kept for reference but should not be used for new development. All new work should go in:
- `packages/` for frontend/shared code
- `services/` for backend services

## Questions?

See:
- [AGENTS.md](./AGENTS.md) - Development guidelines
- [README.md](./README.md) - Project overview
- [turbo.json](./turbo.json) - Build pipeline config
