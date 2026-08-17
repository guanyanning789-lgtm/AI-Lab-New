import re
from pathlib import Path


VERSIONED_SOURCE_NAME = re.compile(r"(?:^|_)v\d+(?:_|\.|$)", re.IGNORECASE)


def test_source_filenames_do_not_contain_versions() -> None:
    root = Path(__file__).parents[1] / "src"
    offenders = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*.py")
        if VERSIONED_SOURCE_NAME.search(path.name)
    ]
    assert offenders == [], f"version numbers belong in Git tags, not filenames: {offenders}"
