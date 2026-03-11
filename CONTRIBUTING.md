# Contributing to ScholarAIO

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/ZimoLiao/scholaraio.git && cd scholaraio
pip install -e ".[full,dev]"
```

## Making Changes

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run tests: `python -m pytest tests/ -v`
4. Submit a pull request

## Code Style

- **Docstrings**: Google-style for public API functions in library modules
- **CLI output / help text**: Chinese
- **Code comments**: English, only when logic isn't self-evident
- Python 3.10+

## Adding a Skill

**Tool skill** (wraps CLI command):
1. Implement the Python function in `scholaraio/`
2. Expose it as a CLI subcommand in `cli.py`
3. Test the CLI command with real data
4. Create `.claude/skills/<name>/SKILL.md`

**Orchestration skill** (pure prompt):
1. Create `.claude/skills/<name>/SKILL.md` — compose existing CLI commands via instructions

Skills follow the [AgentSkills.io](https://agentskills.io) open standard.

## Reporting Issues

- Use [GitHub Issues](https://github.com/ZimoLiao/scholaraio/issues)
- Include your Python version, OS, and steps to reproduce

## License

By contributing, you agree that your contributions will be licensed under [MIT](LICENSE).
