"""Helpers for CSV bulk upload, export, and Google Form data parsing."""
from __future__ import annotations

import csv
import io

from .choices import CATEGORIES, SURVEY_FIELDS

CSV_COLUMNS = SURVEY_FIELDS


def sample_rows() -> list[list[str]]:
    example_a = ['STU-2024-001'] + [CATEGORIES[f][0] for f in CATEGORIES]
    example_b = ['STU-2024-002'] + [CATEGORIES[f][-1] for f in CATEGORIES]
    return [example_a, example_b]


def build_sample_csv() -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for row in sample_rows():
        writer.writerow(row)
    return buffer.getvalue()


def parse_upload(file_obj) -> tuple[list[dict], list[str]]:
    """Parse and validate an uploaded CSV for bulk prediction.

    Returns (valid_rows, errors). valid_rows is a list of feature dicts
    ready to send to the ML service; errors describes rejected rows.
    """
    errors: list[str] = []
    valid_rows: list[dict] = []

    raw = file_obj.read()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8-sig', errors='replace')
    reader = csv.DictReader(io.StringIO(raw))

    if reader.fieldnames is None:
        return [], ['The CSV file is empty.']

    header = [h.strip() for h in reader.fieldnames]
    missing = [c for c in CSV_COLUMNS if c not in header]
    if missing:
        return [], [f'Missing required columns: {", ".join(missing)}']

    seen_refs: set[str] = set()
    for line_no, row in enumerate(reader, start=2):
        cleaned = {k.strip(): (v or '').strip() for k, v in row.items()}
        ref = cleaned.get('student_ref', '')
        if not ref:
            errors.append(f'Row {line_no}: missing student_ref.')
            continue
        if ref in seen_refs:
            errors.append(f'Row {line_no}: duplicate student_ref "{ref}" in file.')
            continue

        bad_fields = []
        for field, allowed in CATEGORIES.items():
            value = cleaned.get(field, '')
            if value not in allowed:
                bad_fields.append(field)
        if bad_fields:
            errors.append(
                f'Row {line_no} ({ref}): invalid value(s) for {", ".join(bad_fields)}.'
            )
            continue

        seen_refs.add(ref)
        payload = {'student_ref': ref}
        payload.update({field: cleaned[field] for field in CATEGORIES})
        valid_rows.append(payload)

    return valid_rows, errors


def parse_google_form_file(file_obj) -> tuple[list[dict], list[str], int]:
    """Parse a Google Form Excel/CSV export for model training.

    Returns (training_rows, errors, total_raw_rows).
    Each training_row is {'features': {...}, 'label': performance_class}.
    """
    from .google_form_mapping import (
        CGPA_TO_PERFORMANCE, map_columns, normalise_value,
    )

    errors: list[str] = []
    training_rows: list[dict] = []
    name = getattr(file_obj, 'name', '')

    raw_bytes = file_obj.read()

    # Some exports arrive as a zip archive containing a CSV (e.g. responses.csv).
    if isinstance(raw_bytes, bytes) and raw_bytes[:2] == b'PK':
        import zipfile
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
            for name in zf.namelist():
                if name.lower().endswith('.csv'):
                    raw_bytes = zf.read(name)
                    break

    if name.lower().endswith(('.xlsx', '.xls')):
        try:
            import openpyxl
            import io as _io
            wb = openpyxl.load_workbook(_io.BytesIO(raw_bytes), read_only=True, data_only=True)
            ws = wb.active
            rows_iter = list(ws.iter_rows(values_only=True))
            if not rows_iter:
                return [], ['Excel file is empty.'], 0
            headers = [str(h).strip() if h is not None else '' for h in rows_iter[0]]
            data_rows = [
                {headers[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(r)}
                for r in rows_iter[1:]
            ]
        except ImportError:
            return [], ['openpyxl is required to read Excel files. Please upload a CSV instead.'], 0
    else:
        if isinstance(raw_bytes, bytes):
            raw_str = raw_bytes.decode('utf-8-sig', errors='replace')
        else:
            raw_str = raw_bytes
        reader = csv.DictReader(io.StringIO(raw_str))
        if reader.fieldnames is None:
            return [], ['CSV file is empty.'], 0
        data_rows = list(reader)

    if not data_rows:
        return [], ['No data rows found.'], 0

    headers = list(data_rows[0].keys())
    col_map = map_columns(headers)

    if not col_map:
        return [], [
            'No recognisable question columns found. '
            'Please use the Google Form export directly or match column headers to survey questions.'
        ], len(data_rows)

    total_raw = len(data_rows)
    for i, row in enumerate(data_rows, start=2):
        features: dict[str, str] = {}
        row_errors: list[str] = []

        for orig_col, feature in col_map.items():
            raw_val = row.get(orig_col, '').strip()
            if not raw_val:
                continue
            canonical = normalise_value(feature, raw_val)
            if canonical is not None:
                features[feature] = canonical
            else:
                row_errors.append(f'{feature}="{raw_val}"')

        if len(features) < 10:
            errors.append(
                f'Row {i}: too few recognisable fields ({len(features)}), skipping.'
            )
            continue

        if row_errors:
            errors.append(
                f'Row {i}: unrecognised values for {", ".join(row_errors[:4])} — row partially used.'
            )

        label_raw = features.get('current_cgpa', '')
        label = CGPA_TO_PERFORMANCE.get(label_raw)
        if label is None:
            errors.append(f'Row {i}: could not determine performance label from current_cgpa, skipping.')
            continue

        training_rows.append({'features': features, 'label': label})

    return training_rows, errors, total_raw
