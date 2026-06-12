"""Helpers for CSV bulk upload and export."""
from __future__ import annotations

import csv
import io

from .choices import CATEGORIES, SURVEY_FIELDS

# CSV columns must exactly match the survey fields (student_ref + features).
CSV_COLUMNS = SURVEY_FIELDS


def sample_rows() -> list[list[str]]:
    """A couple of example rows using valid category values."""
    example_a = ["STU-2024-001"] + [CATEGORIES[f][0] for f in CATEGORIES]
    example_b = ["STU-2024-002"] + [CATEGORIES[f][-1] for f in CATEGORIES]
    return [example_a, example_b]


def build_sample_csv() -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for row in sample_rows():
        writer.writerow(row)
    return buffer.getvalue()


def parse_upload(file_obj) -> tuple[list[dict], list[str]]:
    """Parse and validate an uploaded CSV.

    Returns ``(valid_rows, errors)``. ``valid_rows`` is a list of feature dicts
    ready to send to the ML service; ``errors`` describes rejected rows.
    """
    errors: list[str] = []
    valid_rows: list[dict] = []

    raw = file_obj.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))

    if reader.fieldnames is None:
        return [], ["The CSV file is empty."]

    header = [h.strip() for h in reader.fieldnames]
    missing = [c for c in CSV_COLUMNS if c not in header]
    if missing:
        return [], [f"Missing required columns: {', '.join(missing)}"]

    seen_refs: set[str] = set()
    for line_no, row in enumerate(reader, start=2):
        cleaned = {k.strip(): (v or "").strip() for k, v in row.items()}
        ref = cleaned.get("student_ref", "")
        if not ref:
            errors.append(f"Row {line_no}: missing student_ref.")
            continue
        if ref in seen_refs:
            errors.append(f"Row {line_no}: duplicate student_ref '{ref}' in file.")
            continue

        bad_fields = []
        for field, allowed in CATEGORIES.items():
            value = cleaned.get(field, "")
            if value not in allowed:
                bad_fields.append(field)
        if bad_fields:
            errors.append(
                f"Row {line_no} ({ref}): invalid value(s) for {', '.join(bad_fields)}."
            )
            continue

        seen_refs.add(ref)
        payload = {"student_ref": ref}
        payload.update({field: cleaned[field] for field in CATEGORIES})
        valid_rows.append(payload)

    return valid_rows, errors
