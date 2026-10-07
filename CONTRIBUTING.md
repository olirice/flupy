# For Contributors

## Setup

Use Python 3.10+ and uv. From the repository root, install the project and its development dependencies:

```sh
uv sync --locked
```

This creates a `.venv` with an editable installation of flupy. Run development commands through `uv run` to use that environment.

Install the Git hooks with:

```sh
uv run pre-commit install
```

## Tests and benchmarks

Run the full test suite with coverage:

```sh
uv run pytest
```

The suite includes runtime tests and mypy assertions in `src/tests/typesafety/`.
To run one test file without the full suite added by the default pytest configuration:

```sh
uv run pytest -o addopts='' src/tests/test_cli.py
```

Run benchmarks separately:

```sh
uv run pytest -o addopts='' benchmark/test_benchmark.py
```

## Formatting and static analysis

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

To apply formatting and available lint fixes:

```sh
uv run ruff check --fix .
uv run ruff format .
```

Run all configured Git hooks on the repository:

```sh
uv run pre-commit run --all-files
```

## Documentation

Build the Sphinx HTML documentation:

```sh
uv run sphinx-build -b html docs build/docs
```

Open `build/docs/index.html` to review the output.

## Dependencies and CI

Development dependencies are declared in `pyproject.toml`; `uv.lock` records their resolved versions. After changing dependencies, run `uv lock` and `uv sync`, and commit both files.

GitHub Actions runs tests on Python 3.10, 3.11, 3.12, and 3.13. A separate workflow runs the pre-commit hooks. Both workflows install dependencies with `uv sync --locked`.

## Releases

For maintainers, update the version in `pyproject.toml`, refresh `uv.lock` with `uv lock`, and run the checks above. Build the source distribution and wheel:

```sh
uv build
```

Review the artifacts in `dist/`. To publish to PyPI, replace `X.Y.Z` with the release version and upload only that version's artifacts using your configured PyPI credentials:

```sh
uv publish dist/flupy-X.Y.Z.tar.gz dist/flupy-X.Y.Z-py3-none-any.whl
```
