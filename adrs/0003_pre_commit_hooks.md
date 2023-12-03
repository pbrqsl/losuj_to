## 1. Implement Pre-commit Hooks with Ruff and Black
### Decision
We have decided to implement pre-commit hooks in the "Losuj To" app using the standard pre-commit template along with the `ruff` and `black` modules.

### Implementation Steps
1. **Install Pre-commit:** Integrate pre-commit into the project by adding a `.pre-commit-config.yaml` file to the repository.
2. **Configure Ruff Hook:** Add a pre-commit hook for the `ruff` module to ensure style consistency.
3. **Configure Black Hook:** Add a pre-commit hook for the `black` module to enforce code formatting.

### Considerations
- Automated code linting and formatting checks before each commit.
- Consistent coding style across the project.
- Integration with widely used Python linting and formatting tools (`ruff` and `black`).


## Status
Accepted

## Date
2023-12-02
