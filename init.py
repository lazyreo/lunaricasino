"""Generate missing ``__init__.py`` files for Python packages."""

from pathlib import Path


PACKAGE_ROOTS = ("app", "service", "schemas", "utils", "logger", "tests")


def ensure_init_files() -> None:
    """Create ``__init__.py`` under known package trees when missing."""
    root = Path(__file__).resolve().parent
    for package_name in PACKAGE_ROOTS:
        package_dir = root / package_name
        if not package_dir.exists():
            continue
        for directory in [package_dir, *package_dir.rglob("*")]:
            if not directory.is_dir():
                continue
            if directory.name.startswith(".") or directory.name == "__pycache__":
                continue
            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.write_text("", encoding="utf-8")
                print(f"created {init_file.relative_to(root)}")


if __name__ == "__main__":
    ensure_init_files()
