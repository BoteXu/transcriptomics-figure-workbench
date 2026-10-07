"""Shared, explicit matrix input normalization for publication plots.

The renderers in this package consume a canonical long table with three
columns: ``feature``, ``sample`` and ``value``.  This module accepts that
representation as well as a wide table (one identifier column plus value
columns), while keeping identifier values as supplied and never guessing a
missing value as zero.

No ordering, clustering, imputation, or statistical transformation happens
here.  A missing or duplicated cell is a data-contract issue unless the
caller explicitly requests a masked display.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import numpy as np
import pandas as pd


def _text_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty column name")
    return value


def _unique_order(values: Sequence[object], supplied: Sequence[object] | None, label: str) -> list[object]:
    observed = list(pd.unique(pd.Series(values, dtype=object)))
    if any(pd.isna(x) for x in observed):
        raise ValueError(f"{label} identifiers cannot be missing")
    if len(observed) != len(set(observed)):
        raise ValueError(f"{label} identifiers must be unique")
    if supplied is None:
        return observed
    requested = list(supplied)
    if len(requested) != len(set(requested)) or set(requested) != set(observed):
        raise ValueError(f"{label}_order must contain every supplied identifier exactly once")
    return requested


def _coerce_value(series: pd.Series, field: str) -> pd.Series:
    """Convert values read from TSV/CSV without converting identifiers."""
    if pd.api.types.is_numeric_dtype(series):
        out = series.astype(float)
    else:
        out = pd.to_numeric(series, errors="raise").astype(float)
    if not np.isfinite(out.to_numpy()).all():
        raise ValueError(f"{field} contains nonfinite values")
    return out


def normalize_matrix(
    data: pd.DataFrame,
    *,
    row_field: str = "feature",
    column_field: str = "sample",
    value_field: str = "value",
    value_columns: Sequence[object] | None = None,
    row_order: Sequence[object] | None = None,
    column_order: Sequence[object] | None = None,
    missing: str = "error",
) -> tuple[pd.DataFrame, list[object], list[object]]:
    """Return ``(long_table, row_order, column_order)`` for a matrix.

    A long table is selected when all three named fields are present.  When
    the column and value fields are absent, the table is interpreted as wide:
    ``row_field`` identifies rows and ``value_columns`` explicitly selects
    columns.  If ``value_columns`` is omitted, all remaining columns must be
    numeric (or losslessly numeric strings), which prevents annotation columns
    from being mistaken for matrix values.

    ``missing='error'`` requires a complete rectangular grid.  The only other
    supported mode is ``missing='mask'``; it retains absent cells as NaN so a
    renderer can show them as masked/hatched cells.  Missing values are never
    silently replaced by zero.
    """
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise ValueError("Expected nonempty matrix DataFrame")
    if missing not in ("error", "mask"):
        raise ValueError("missing must be 'error' or 'mask'")
    row_field = _text_name(row_field, "row_field")
    column_field = _text_name(column_field, "column_field")
    value_field = _text_name(value_field, "value_field")
    if len({row_field,column_field,value_field})!=3 or data.columns.duplicated().any():
        raise ValueError('Distinct matrix field names and unique table columns required')
    cols = set(data.columns)
    is_long = {row_field, column_field, value_field}.issubset(cols)
    if is_long:
        d = data[[row_field, column_field, value_field]].copy()
        d = d.rename(columns={row_field: "feature", column_field: "sample", value_field: "value"})
        if d[["feature", "sample"]].isna().any().any():
            raise ValueError("Matrix identifiers cannot be missing")
        d["value"] = _coerce_value(d["value"], value_field)
    else:
        if row_field not in cols:
            raise ValueError(f"Missing matrix row column: {row_field}")
        if column_field in cols or value_field in cols:
            raise ValueError("Use either long fields row/column/value or a wide row column with value_columns")
        if value_columns is None:
            candidates = [c for c in data.columns if c != row_field]
            if not candidates:
                raise ValueError("Wide matrix needs at least one value column")
            bad = []
            for c in candidates:
                try:
                    _coerce_value(data[c], str(c))
                except (TypeError, ValueError):
                    bad.append(c)
            if bad:
                raise ValueError("Wide matrix value_columns must be explicit when nonnumeric annotations are present")
            value_columns = candidates
        else:
            value_columns = list(value_columns)
            if not value_columns or len(value_columns) != len(set(value_columns)):
                raise ValueError("value_columns must contain at least one unique column")
            unknown = [c for c in value_columns if c not in cols or c == row_field]
            if unknown:
                raise ValueError(f"Unknown wide matrix value columns: {unknown}")
        if data[row_field].duplicated().any() or data[row_field].isna().any():
            raise ValueError("Wide matrix row identifiers must be unique and nonmissing")
        d = data[[row_field] + list(value_columns)].melt(
            id_vars=[row_field], var_name="sample", value_name="value"
        ).rename(columns={row_field: "feature"})
        d["value"] = _coerce_value(d["value"], value_field)

    if d.duplicated(["feature", "sample"]).any():
        raise ValueError("Duplicate matrix cells")
    rows = _unique_order(d["feature"], row_order, "row")
    columns = _unique_order(d["sample"], column_order, "column")
    expected = len(rows) * len(columns)
    if len(d) != expected and missing == "error":
        raise ValueError("Incomplete matrix grid; use missing='mask' to display explicit absent cells")
    return d, rows, columns


def axis_labels(keys: Sequence[object], aliases: Mapping[object, object] | None, label: str) -> list[str]:
    """Validate optional display aliases without changing stored IDs."""
    keys = list(keys)
    if aliases is None:
        return [str(x) for x in keys]
    if set(aliases) != set(keys):
        raise ValueError(f"{label}_aliases must cover every supplied identifier exactly")
    out = [str(aliases[k]) for k in keys]
    if any(not x.strip() for x in out) or len(set(out)) != len(out):
        raise ValueError(f"{label}_aliases must be nonempty and unique")
    return out


def matrix_frame(d: pd.DataFrame, rows: Sequence[object], columns: Sequence[object]) -> pd.DataFrame:
    """Pivot in declared order, keeping absent cells as NaN."""
    return d.pivot(index="feature", columns="sample", values="value").reindex(index=list(rows), columns=list(columns))
