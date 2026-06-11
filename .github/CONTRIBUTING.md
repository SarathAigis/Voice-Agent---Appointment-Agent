# Contributing to Voice Agent Appointment Scheduler

Thank you for contributing! This project follows a **pnpm monorepo** structure with Turborepo.

## Quick Start

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Voice-Agent---Appointment-Agent.git
   cd Voice-Agent---Appointment-Agent
   ```

2. **Install pnpm:**
   ```bash
   npm install -g pnpm@8
   ```

3. **Install dependencies:**
   ```bash
   pnpm install
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

Please read [AGENTS.md](../AGENTS.md) for detailed development guidelines.

### Key Commands

```bash
# Development
pnpm dev                              # Run all services
pnpm --filter dashboard dev           # Run specific package

# Testing
pnpm test                             # Test all packages
pnpm vitest run -t "test name"        # Run specific test

# Linting
pnpm lint                             # Lint all packages
pnpm --filter shared lint             # Lint specific package

# Building
pnpm build                            # Build all packages
```

### Before Committing

**Required checks:**
```bash
pnpm lint    # Must pass
pnpm test    # Must pass
```

### PR Title Format

Follow the format from [AGENTS.md](../AGENTS.md):

```
[package-name] Brief description

Examples:
[dashboard] Add real-time call monitoring
[shared] Add phone number formatting
[voice-agent] Fix voicemail detection
```

### Commit Messages

Use conventional commits:

```
feat(dashboard): add live call panel
fix(shared): handle invalid phone formats
docs(readme): update setup instructions
test(shared): add formatDuration tests
```

## Project Structure

```
voice-agent-appointment-scheduler/
├── packages/
│   ├── dashboard/          # Next.js frontend
│   └── shared/             # Shared TypeScript utilities
├── services/
│   ├── voice-agent/        # Python voice agent
│   └── api/                # FastAPI server
└── .github/workflows/      # CI/CD
```

## Testing Requirements

### TypeScript Packages

- Use **Vitest** for testing
- Place tests next to source: `index.test.ts` alongside `index.ts`
- Aim for >80% coverage on new code
- Run: `pnpm --filter <package> test`

### Python Services

- Use **pytest** for testing
- Place tests in `tests/` directory
- Follow naming: `test_*.py`
- Run: `cd services/<service> && pytest`

## Code Style

### TypeScript

- **Formatter:** Prettier (auto-run on commit)
- **Linter:** ESLint
- **Config:** See `.prettierrc` and `.eslintrc.js`

### Python

- **Formatter:** Black
- **Linter:** Ruff
- **Line length:** 100 characters

## CI/CD

All PRs run through GitHub Actions:

1. ✅ Lint check
2. ✅ Type check
3. ✅ Unit tests
4. ✅ Build verification

See `.github/workflows/ci.yml` for details.

## Adding Dependencies

### TypeScript Packages

```bash
# Add to specific package
pnpm add <package> --filter dashboard

# Add dev dependency
pnpm add -D <package> --filter shared

# Add to root (tooling only)
pnpm add -D -w <package>
```

### Python Services

```bash
cd services/<service>
pip install <package>
# Add to requirements.txt manually
```

## Package Structure

When creating a new package:

```json
{
  "name": "package-name",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "...",
    "build": "...",
    "test": "vitest run",
    "lint": "eslint .",
    "type-check": "tsc --noEmit"
  }
}
```

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes in appropriate package(s)
3. Add tests: `*.test.ts` for TypeScript
4. Run checks: `pnpm lint && pnpm test`
5. Commit: `git commit -m "feat(package): description"`
6. Push: `git push origin feature/my-feature`
7. Create PR with proper title: `[package] Description`

### Fixing a Bug

1. Write a failing test first
2. Fix the bug
3. Verify test passes
4. Run full test suite: `pnpm test`
5. Create PR: `[package] Fix description`

### Updating Documentation

1. Edit relevant `.md` files
2. Check formatting: `pnpm format`
3. Create PR: `[docs] Update description`

## Getting Help

- 📖 Read [AGENTS.md](../AGENTS.md) for workflow details
- 📖 Read [REFACTOR_GUIDE.md](../REFACTOR_GUIDE.md) for migration info
- 🐛 Check existing [issues](https://github.com/SarathAigis/Voice-Agent---Appointment-Agent/issues)
- 💬 Ask questions in PRs or issues

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Assume good intent

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

**Thank you for contributing!** 🎉
