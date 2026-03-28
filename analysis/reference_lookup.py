import json
import re
from functools import lru_cache
from pathlib import Path

try:
    import pandas as pd
except Exception:  # Optional dependency for xlsx/csv ingestion.
    pd = None


def _normalize_name(name):
    value = str(name or "").lower()
    value = value.replace("*", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _safe_load_json(file_path):
    # Accept plain JSON and JSON-with-line-comments for convenience.
    raw = file_path.read_text(encoding="utf-8")
    cleaned_lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    return json.loads(cleaned)


def _normalize_gender(value):
    text = _normalize_name(value)
    if text in {"male", "female", "all"}:
        return text
    if text in {"any", "both", "unisex", "common"}:
        return "all"
    return "all"


def _range_string(range_type, low_value, high_value):
    kind = _normalize_name(range_type)

    try:
        low = float(low_value) if low_value not in {None, ""} else None
    except Exception:
        low = None

    try:
        high = float(high_value) if high_value not in {None, ""} else None
    except Exception:
        high = None

    if kind == "lt" and high is not None:
        return f"< {high}"
    if kind == "gt" and low is not None:
        return f"> {low}"
    if low is not None and high is not None:
        return f"{low} - {high}"
    return None


def _split_aliases(aliases, fallback_name):
    raw = str(aliases or "").strip()
    if not raw:
        return [str(fallback_name or "").strip()]

    parts = [part.strip() for part in re.split(r"[,;|]", raw) if part.strip()]
    if str(fallback_name or "").strip() and str(fallback_name).strip() not in parts:
        parts.insert(0, str(fallback_name).strip())
    return parts


def _find_column(df, candidates):
    normalized = {str(col): _normalize_name(col) for col in df.columns}
    for col, col_norm in normalized.items():
        for candidate in candidates:
            if candidate == col_norm:
                return col
    return None


def _ensure_entry(database, key_name, aliases):
    key = _normalize_name(key_name).replace(" ", "_")
    if key not in database:
        database[key] = {"aliases": [], "ranges": {}}

    entry = database[key]
    existing = {_normalize_name(item) for item in entry.get("aliases", [])}
    for alias in aliases:
        if _normalize_name(alias) not in existing:
            entry.setdefault("aliases", []).append(alias)
            existing.add(_normalize_name(alias))

    return entry


def _load_json_row_schema(data_rows, database):
    for row in data_rows:
        if not isinstance(row, dict):
            continue

        parameter_name = row.get("Parameter") or row.get("parameter")
        if not parameter_name:
            continue

        aliases = _split_aliases(row.get("Aliases") or row.get("aliases"), parameter_name)
        gender = row.get("Gender") or row.get("gender") or "all"
        age_group = row.get("Age Group") or row.get("age_group") or "adult"

        range_text = row.get("Reference") or row.get("reference")
        if not range_text:
            range_text = _range_string(
                row.get("Range Type") or row.get("range_type") or "between",
                row.get("Min Value") if "Min Value" in row else row.get("low_value"),
                row.get("Max Value") if "Max Value" in row else row.get("high_value"),
            )

        entry = _ensure_entry(database, parameter_name, aliases)
        _update_range(entry, gender, age_group, range_text)

        # Add optional unit aliases to improve matching precision.
        unit = row.get("Unit") or row.get("unit")
        if unit:
            entry.setdefault("unit", str(unit).strip())


def _update_range(entry, gender, age_group, reference_text):
    if not reference_text:
        return

    gender_key = _normalize_gender(gender)
    ranges = entry.setdefault("ranges", {})
    bucket = ranges.setdefault(gender_key, {})

    age_text = _normalize_name(age_group)
    if not age_text or age_text == "adult":
        bucket["default"] = reference_text
        return

    # For now map non-adult text as default unless explicit numeric min-max is given.
    min_max_match = re.search(r"(\d+)\s*[-to]+\s*(\d+)", age_text)
    if min_max_match:
        min_age = int(min_max_match.group(1))
        max_age = int(min_max_match.group(2))
        age_ranges = bucket.setdefault("age_ranges", [])
        age_ranges.append({"min": min_age, "max": max_age, "range": reference_text})
    else:
        bucket["default"] = reference_text


def _load_tabular_reference_file(file_path, database):
    if pd is None:
        return

    suffix = file_path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(file_path)
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(file_path)
        else:
            return
    except Exception:
        return

    if df is None or df.empty:
        return

    parameter_col = _find_column(df, {"parameter_name", "parameter", "test", "investigation"})
    aliases_col = _find_column(df, {"aliases", "alias"})
    gender_col = _find_column(df, {"gender_scope", "gender", "sex"})
    age_col = _find_column(df, {"age_group", "age"})
    range_type_col = _find_column(df, {"range_type", "type"})
    low_col = _find_column(df, {"low_value", "low", "min"})
    high_col = _find_column(df, {"high_value", "high", "max"})
    range_col = _find_column(df, {"range", "reference", "reference_range"})

    if not parameter_col:
        return

    for _, row in df.iterrows():
        parameter_name = row.get(parameter_col)
        if parameter_name is None or str(parameter_name).strip() == "":
            continue

        aliases = _split_aliases(row.get(aliases_col) if aliases_col else "", parameter_name)
        gender = row.get(gender_col) if gender_col else "all"
        age_group = row.get(age_col) if age_col else "adult"

        reference_text = None
        if range_col and row.get(range_col) not in {None, ""}:
            reference_text = str(row.get(range_col)).strip()
        else:
            reference_text = _range_string(
                row.get(range_type_col) if range_type_col else "between",
                row.get(low_col) if low_col else None,
                row.get(high_col) if high_col else None,
            )

        entry = _ensure_entry(database, parameter_name, aliases)
        _update_range(entry, gender, age_group, reference_text)


@lru_cache(maxsize=1)
def _load_reference_db():
    knowledge_dir = Path(__file__).resolve().parents[1] / "knowledge"
    file_path = knowledge_dir / "medical_parameters.json"

    database = {}

    if file_path.exists():
        data = _safe_load_json(file_path)
        if isinstance(data, dict):
            database.update(data)
        elif isinstance(data, list):
            _load_json_row_schema(data, database)

    # Optional tabular reference files provided by user.
    for candidate in [
        knowledge_dir / "medical_parameters_complete.xlsx",
        knowledge_dir / "medical_parameters_complete.xls",
        knowledge_dir / "medical_parameters_complete.csv",
    ]:
        if candidate.exists():
            _load_tabular_reference_file(candidate, database)

    return database


def _pick_gender_bucket(ranges, gender):
    if not isinstance(ranges, dict):
        return None

    gender = (gender or "").lower().strip()

    if gender in {"male", "female"} and gender in ranges:
        return ranges.get(gender)

    if "all" in ranges:
        return ranges.get("all")

    if "adult" in ranges:
        return ranges.get("adult")

    if "male" in ranges:
        return ranges.get("male")

    if "female" in ranges:
        return ranges.get("female")

    return None


def _pick_age_range(bucket, age):
    if not isinstance(bucket, dict):
        return None

    if age is not None and "age_ranges" in bucket:
        age_ranges = bucket.get("age_ranges") or []
        for item in age_ranges:
            min_age = item.get("min")
            max_age = item.get("max")
            if min_age is None or max_age is None:
                continue
            if min_age <= age <= max_age and item.get("range"):
                return item.get("range")

    return bucket.get("default")


def get_reference_for_parameter(parameter, gender=None, age=None):
    database = _load_reference_db()
    if not database:
        return None

    parameter_norm = _normalize_name(parameter)
    if not parameter_norm:
        return None

    for _, config in database.items():
        aliases = config.get("aliases", [])
        alias_norms = {_normalize_name(alias) for alias in aliases}

        matched = (
            parameter_norm in alias_norms
            or any(alias in parameter_norm for alias in alias_norms if len(alias) >= 4)
            or any(parameter_norm in alias for alias in alias_norms if len(parameter_norm) >= 4)
        )

        if not matched:
            continue

        ranges = config.get("ranges", {})
        bucket = _pick_gender_bucket(ranges, gender)
        if not bucket:
            continue

        reference = _pick_age_range(bucket, age)
        if reference:
            return reference

    return None
