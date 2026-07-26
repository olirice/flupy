"""Type-checks src/tests/typesafety, one pytest test per assert_type call.

Each fixture file pins the exact type a Fluent method or chain resolves to
via `assert_type`. mypy runs once per session; its output is attributed back
to the specific assert_type call site it belongs to, so a broken overload or
generic handoff fails only the test(s) for the call sites it affects, and
mismatches unaccounted for by any known call site fail
test_no_unattributed_mypy_errors instead of being silently dropped.
"""

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple

import pytest
from mypy import api as mypy_api

TYPESAFETY_DIR = Path(__file__).parent / "typesafety"

_ERROR_LINE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+): error: (?P<message>.*)$")


class AssertTypeSite(NamedTuple):
    filename: str
    lineno: int


def _discover_assert_type_sites() -> List[AssertTypeSite]:
    sites = []
    for path in sorted(TYPESAFETY_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            is_assert_type_call = (
                isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "assert_type"
            )
            if is_assert_type_call:
                sites.append(AssertTypeSite(path.name, node.lineno))
    return sites


def _run_mypy() -> Dict[Tuple[str, int], List[str]]:
    stdout, stderr, _exit_status = mypy_api.run(
        ["--strict", "--python-version", "3.10", "--no-incremental", str(TYPESAFETY_DIR)]
    )
    errors_by_site: Dict[Tuple[str, int], List[str]] = defaultdict(list)
    for line in stdout.splitlines():
        match = _ERROR_LINE.match(line)
        if match is None:
            continue
        key = (Path(match["file"]).name, int(match["line"]))
        errors_by_site[key].append(match["message"])
    return errors_by_site


ASSERT_TYPE_SITES = _discover_assert_type_sites()


@pytest.fixture(scope="session")
def mypy_errors_by_site() -> Dict[Tuple[str, int], List[str]]:
    return _run_mypy()


@pytest.mark.parametrize(
    "site",
    ASSERT_TYPE_SITES,
    ids=[f"{site.filename}:{site.lineno}" for site in ASSERT_TYPE_SITES],
)
def test_assert_type_site(site: AssertTypeSite, mypy_errors_by_site: Dict[Tuple[str, int], List[str]]) -> None:
    errors = mypy_errors_by_site.get((site.filename, site.lineno), [])
    assert not errors, "\n".join(errors)


def test_no_unattributed_mypy_errors(mypy_errors_by_site: Dict[Tuple[str, int], List[str]]) -> None:
    known_sites = {(site.filename, site.lineno) for site in ASSERT_TYPE_SITES}
    stray = {key: msgs for key, msgs in mypy_errors_by_site.items() if key not in known_sites}
    assert not stray, f"mypy reported errors not tied to any assert_type call: {stray}"
