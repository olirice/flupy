# Test Coverage Analysis for flupy

## Executive Summary

This document analyzes the current test coverage of the flupy library and proposes specific areas for improvement. The library currently has **good test coverage** (~80-85%) of its public API, but several edge cases and error handling paths are not tested.

## Current Test Statistics

| Component | Tests | Lines | Coverage |
|-----------|-------|-------|----------|
| `flupy/fluent.py` | 40 | 429 | ~80-85% |
| `flupy/cli/cli.py` | 11 | 111 | ~70-80% |
| `flupy/cli/utils.py` | 2 | 10 | ~70-80% |

## Identified Coverage Gaps

### High Priority (Error Handling)

#### 1. Empty Iterator Operations

**Gap:** Several terminal operations that should fail on empty iterators are not tested for their error behavior.

| Method | Expected Error | Currently Tested |
|--------|---------------|------------------|
| `reduce()` on empty | `TypeError` | ❌ No |
| `min()` on empty | `ValueError` | ❌ No |
| `max()` on empty | `ValueError` | ❌ No |

**Rationale:** These are common user errors that should have predictable behavior. Tests ensure the errors are descriptive and consistent.

#### 2. Attribute/Item Access Errors

**Gap:** `map_item()` and `map_attr()` don't have tests for when the requested item/attribute doesn't exist.

| Method | Scenario | Expected Error | Currently Tested |
|--------|----------|---------------|------------------|
| `map_item("missing")` | Key doesn't exist | `KeyError` | ❌ No |
| `map_item(999)` | Index out of range | `IndexError` | ❌ No |
| `map_attr("missing")` | Attribute doesn't exist | `AttributeError` | ❌ No |

**Rationale:** Users need clear error messages when accessing non-existent data. Current behavior is untested.

### Medium Priority (Edge Cases)

#### 3. Parameter Validation

| Method | Edge Case | Expected Behavior | Currently Tested |
|--------|-----------|-------------------|------------------|
| `chunk(0)` | Zero chunk size | Error or empty? | ❌ No |
| `chunk(-1)` | Negative chunk size | Error | ❌ No |
| `flatten(depth=-1)` | Negative depth | Error or no-op? | ❌ No |
| `head(-1)` | Negative count | Error or empty? | ❌ No |
| `tail(-1)` | Negative count | Error or empty? | ❌ No |
| `take(-1)` | Negative count | Error or empty? | ❌ No |
| `collect(n=-1)` | Negative count | Error or empty? | ❌ No |

**Rationale:** These edge cases can occur from user calculations (e.g., `head(len(items) - 5)` when `len(items) < 5`). Behavior should be documented and tested.

#### 4. `__getitem__` Edge Cases

| Scenario | Currently Tested |
|----------|------------------|
| Negative index (`flu([1,2,3])[-1]`) | ❌ No (raises TypeError) |
| Step in slice (`flu(range(10))[::2]`) | ❌ No |
| Negative slice (`flu(range(10))[-3:]`) | ❌ No |

**Rationale:** Python users expect standard sequence behavior. Current limitations should be tested/documented.

### CLI Coverage Gaps

#### 5. CLI Error Handling

| Scenario | Currently Tested |
|----------|------------------|
| Malformed import syntax (e.g., `"a:b:c:d"`) | ❌ No |
| Non-existent module import | ❌ No |
| Non-existent file with `-f` | ❌ No |
| Exception in user command | ❌ No |
| Empty file with `-f` | ❌ No |

**Rationale:** CLI tools should gracefully handle invalid input with helpful error messages.

### Utility Function Gaps

#### 6. File System Edge Cases

| Function | Scenario | Currently Tested |
|----------|----------|------------------|
| `walk_files()` | Non-existent path | ❌ No |
| `walk_files()` | Permission denied | ❌ No |
| `walk_dirs()` | Non-existent path | ❌ No |
| `walk_dirs()` | Permission denied | ❌ No |

**Rationale:** File system operations commonly encounter permission issues in real-world usage.

## Proposed Test Additions

See `src/tests/test_coverage_improvements.py` for proposed test implementations.

### Summary of Proposed Tests

| Category | New Tests | Priority |
|----------|-----------|----------|
| Empty iterator errors | 3 | High |
| Attribute/item access errors | 3 | High |
| Parameter validation | 7 | Medium |
| `__getitem__` edge cases | 3 | Medium |
| CLI error handling | 4 | Medium |
| Utility function errors | 2 | Low |
| **Total** | **22** | |

## Implementation Recommendations

### Phase 1: High Priority (Error Handling)
1. Add tests for `reduce()`, `min()`, `max()` on empty iterators
2. Add tests for `map_item()` and `map_attr()` with missing keys/attributes
3. Verify error messages are helpful

### Phase 2: Medium Priority (Edge Cases)
1. Document expected behavior for edge cases (negative parameters, etc.)
2. Add tests based on documented behavior
3. Consider whether some edge cases should raise errors vs. return empty

### Phase 3: CLI/Utilities
1. Add CLI error handling tests
2. Add file system error path tests (may require mocking)

## Appendix: Methods Fully Covered by Existing Tests

The following methods have comprehensive test coverage:

- `collect()`, `to_list()`, `sum()`, `count()`
- `first()`, `last()` (including defaults and empty iterator errors)
- `head()`, `tail()` (basic functionality)
- `map()`, `filter()`, `take()`, `take_while()`, `drop_while()`
- `chunk()` (basic functionality)
- `unique()`, `sort()`, `shuffle()`
- `group_by()`, `window()`, `enumerate()`
- `zip()`, `zip_longest()`, `tee()`
- `flatten()`, `denormalize()`
- `join_left()`, `join_inner()`, `join_full()`
- `side_effect()`, `rate_limit()`
- `reduce()`, `fold_left()` (basic functionality)
