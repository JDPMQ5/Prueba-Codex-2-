"""Utilidades generales del MVP."""

from __future__ import annotations

from io import BytesIO

import pandas as pd


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convierte DataFrame a bytes de Excel para descarga en Streamlit."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="clientes_no_compra_abril")
    buffer.seek(0)
    return buffer.getvalue()
