"""
Tests for version information.
"""
import re

import flupy


def test_version_format():
    """Test that __version__ follows semantic versioning format (MAJOR.MINOR.PATCH)."""
    # Standard semver regex pattern
    semver_pattern = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    assert re.match(
        semver_pattern, flupy.__version__
    ), f"Version '{flupy.__version__}' does not match semantic versioning format"

    # Ensure version parts can be parsed as integers
    major, minor, patch = flupy.__version__.split("-")[0].split("+")[0].split(".")[:3]
    assert major.isdigit(), f"Major version '{major}' is not a valid integer"
    assert minor.isdigit(), f"Minor version '{minor}' is not a valid integer"
    assert patch.isdigit(), f"Patch version '{patch}' is not a valid integer"
