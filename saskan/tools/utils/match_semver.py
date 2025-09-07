# saskan/infra_tools/match_semver.py

import re


def match_semver(version: str) -> bool:
    """Check if version string matches semantic versioning pattern."""

    semver_pattern = r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-(0|[1-9A-Za-z-][0-9A-Za-z-]*)(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$"  # noqa: E501
    return re.match(semver_pattern, version) is not None
