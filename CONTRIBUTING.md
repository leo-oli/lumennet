# Contributing to LumenNet

Thank you for your interest in contributing to LumenNet! We welcome contributions that improve the model's performance, code quality, or user experience.

## How to Contribute

### 1. Report Bugs

If you find a bug, please open an issue on GitHub. Include:
- A clear description of the problem.
- Steps to reproduce the issue.
- Details about your environment (Docker version, OS, etc.).

### 2. Suggest Enhancements

Have an idea to make LumenNet better? Open an issue to discuss it before starting work.

### 3. Pull Requests

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Ensure your code follows the existing style.
4. Submit a Pull Request with a clear description of your changes.

## Development Setup

To set up the project locally:
1. Clone the repository.
2. Ensure you have [uv](https://github.com/astral-sh/uv) installed.
3. Install dependencies:
   - Backend: `cd backend && uv sync`
   - Frontend: `cd frontend && uv sync`
4. Run the stack using Docker: `docker compose up --build`

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
