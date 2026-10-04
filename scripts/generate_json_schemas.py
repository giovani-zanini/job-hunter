"""Generate self-contained JSON Schema catalogs from profile and enterprise DTOs.

Run from the repository root with ``.venv/bin/python scripts/generate_json_schemas.py``.
Use ``--check`` to fail if any generated file is missing or out of date.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from pathlib import Path
from types import ModuleType

from pydantic import BaseModel
from pydantic.json_schema import models_json_schema


ROOT = Path(__file__).resolve().parents[1]
MODULES = ("profile", "enterprise")
SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"


def feature_directories(module_name: str) -> list[Path]:
    return sorted(
        directory
        for directory in (ROOT / "src" / "modules" / module_name / "features").iterdir()
        if directory.is_dir() and (directory / "dtos.py").is_file()
    )


def load_dtos(module_name: str) -> dict[str, list[type[BaseModel]]]:
    directories = feature_directories(module_name)

    # Several feature __init__.py files import routers, database models and
    # application settings. Register lightweight packages so importing dtos.py
    # does not execute those unrelated side effects.
    for directory in directories:
        package_name = f"src.modules.{module_name}.features.{directory.name}"
        package = ModuleType(package_name)
        package.__path__ = [str(directory)]
        sys.modules[package_name] = package

    features: dict[str, list[type[BaseModel]]] = {}
    for directory in directories:
        dto_module = importlib.import_module(
            f"src.modules.{module_name}.features.{directory.name}.dtos"
        )
        features[directory.name] = sorted(
            (
                cls
                for _, cls in inspect.getmembers(dto_module, inspect.isclass)
                if issubclass(cls, BaseModel) and cls.__module__ == dto_module.__name__
            ),
            key=lambda cls: cls.__name__,
        )
        if not features[directory.name]:
            raise ValueError(f"No Pydantic DTOs found in {dto_module.__name__}")

    if (ROOT / "src" / "modules" / module_name / "shared" / "dtos.py").is_file():
        shared_module = importlib.import_module(f"src.modules.{module_name}.shared.dtos")
        shared_models = sorted(
            (
                cls
                for _, cls in inspect.getmembers(shared_module, inspect.isclass)
                if issubclass(cls, BaseModel) and cls is not BaseModel
            ),
            key=lambda cls: cls.__name__,
        )
        if shared_models:
            features["shared"] = shared_models
    return features


def catalog(title: str, groups: dict[str, list[type[BaseModel]]]) -> dict:
    model_modes = [
        (model, "serialization" if model.__name__.endswith("Response") else "validation")
        for models in groups.values()
        for model in models
    ]
    model_refs, generated = models_json_schema(
        model_modes, ref_template="#/$defs/{model}"
    )
    refs = {
        group_name: {
            model.__name__: model_refs[
                (model, "serialization" if model.__name__.endswith("Response") else "validation")
            ]["$ref"]
            for model in models
        }
        for group_name, models in groups.items()
    }
    return {
        "$schema": SCHEMA_DRAFT,
        "title": title,
        "description": (
            "Consolidated DTO schemas. Select an individual contract through its "
            "reference in x-models. The root accepts any listed DTO."
        ),
        "anyOf": [
            {"$ref": ref}
            for group in refs.values()
            for ref in group.values()
        ],
        "$defs": generated["$defs"],
        "x-models": refs,
    }


def generated_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for module_name in MODULES:
        groups = load_dtos(module_name)
        module_directory = ROOT / "src" / "modules" / module_name
        for feature_name, models in groups.items():
            if feature_name == "shared":
                continue
            path = module_directory / "features" / feature_name / "schema.json"
            document = catalog(f"{module_name}.{feature_name}", {feature_name: models})
            files[path] = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

        path = module_directory / "schema.json"
        document = catalog(module_name, groups)
        files[path] = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check generated schemas")
    args = parser.parse_args()

    files = generated_files()
    stale = [path for path, content in files.items() if not path.is_file() or path.read_text() != content]
    if args.check:
        if stale:
            for path in stale:
                print(f"Out of date: {path.relative_to(ROOT)}")
            return 1
        print(f"All {len(files)} JSON Schema catalogs are up to date.")
        return 0

    for path, content in files.items():
        path.write_text(content)
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
