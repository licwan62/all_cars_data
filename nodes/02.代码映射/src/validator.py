from __future__ import annotations

from .models import MakeMapping, ModelMapping


def validate_make_mappings(items: list[MakeMapping], width: int, max_code: int) -> None:
    keys: set[str] = set()
    codes: set[str] = set()
    for item in items:
        _validate_code(item.make_code, "MAKE_CODE", width, max_code)
        if item.make_key in keys:
            raise ValueError(f"Duplicate MAKE mapping: {item.make}")
        if item.make_code in codes:
            raise ValueError(f"Duplicate MAKE_CODE: {item.make_code}")
        keys.add(item.make_key)
        codes.add(item.make_code)


def validate_model_mappings(
    items: list[ModelMapping], makes: list[MakeMapping], width: int, max_code: int
) -> None:
    make_codes = {item.make_key: item.make_code for item in makes}
    keys: set[tuple[str, str]] = set()
    scoped_codes: set[tuple[str, str]] = set()
    for item in items:
        _validate_code(item.make_code, "MAKE_CODE", width, max_code)
        _validate_code(item.model_code, "MODEL_CODE", width, max_code)
        if make_codes.get(item.make_key) != item.make_code:
            raise ValueError(f"MAKE_CODE mismatch for model {item.make}/{item.model}")
        key = (item.make_key, item.model_key)
        scoped_code = (item.make_key, item.model_code)
        if key in keys:
            raise ValueError(f"Duplicate MODEL mapping: {item.make}/{item.model}")
        if scoped_code in scoped_codes:
            raise ValueError(f"Duplicate MODEL_CODE {item.model_code} for {item.make}")
        keys.add(key)
        scoped_codes.add(scoped_code)


def validate_immutable(
    old_makes: list[MakeMapping],
    new_makes: list[MakeMapping],
    old_models: list[ModelMapping],
    new_models: list[ModelMapping],
) -> None:
    new_make_codes = {item.make_key: item.make_code for item in new_makes}
    for old in old_makes:
        if new_make_codes.get(old.make_key) != old.make_code:
            raise ValueError(
                f"Immutable mapping violation: MAKE {old.make}; OLD {old.make_code}; "
                f"NEW {new_make_codes.get(old.make_key, '<missing>')}. Mapping files were NOT modified."
            )
    new_model_codes = {(item.make_key, item.model_key): item.model_code for item in new_models}
    for old in old_models:
        new_code = new_model_codes.get((old.make_key, old.model_key))
        if new_code != old.model_code:
            raise ValueError(
                f"Immutable mapping violation: MODEL {old.make}/{old.model}; OLD {old.model_code}; "
                f"NEW {new_code or '<missing>'}. Mapping files were NOT modified."
            )


def _validate_code(code: str, label: str, width: int, max_code: int) -> None:
    if len(code) != width or not code.isdigit() or int(code) > max_code:
        raise ValueError(f"Invalid {label}: {code!r}; expected 00-{max_code:0{width}d}.")

