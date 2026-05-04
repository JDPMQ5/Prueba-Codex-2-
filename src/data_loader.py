"""Módulo para carga y validación de datos de sell-out."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "FechaFacturacion",
    "cliente_id",
    "CD",
    "cond_pago",
    "condicion_pago_id",
    "material_id",
    "combo_id",
    "combinacion",
    "descripcion",
    "direccion",
    "gerencia",
    "nombre_sku",
    "marca",
    "subcategoria",
    "unidad_negocio",
    "agrupador",
    "promocion",
    "venta_umv",
    "nr_canje",
    "tipo_de_cliente_real",
    "nombre_cliente_real",
    "BK",
]


def clean_column_name(name: str) -> str:
    """Limpia espacios en nombres de columnas sin alterar su semántica."""
    return str(name).strip()


def load_dataset(file_obj) -> pd.DataFrame:
    """Carga un dataset desde CSV o Excel."""
    file_name = file_obj.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(file_obj)
    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_obj)
    else:
        raise ValueError("Formato no soportado. Usa CSV o Excel.")

    return preprocess_dataset(df)


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza columnas, valida esquema y convierte tipos críticos."""
    df = df.copy()
    df.columns = [clean_column_name(c) for c in df.columns]

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            "Faltan columnas requeridas en la base: " + ", ".join(missing_cols)
        )

    # Conversión robusta de fecha
    df["FechaFacturacion"] = pd.to_datetime(
        df["FechaFacturacion"], dayfirst=True, errors="coerce"
    )

    # Conversión de métricas numéricas para evitar errores de tipo
    df["nr_canje"] = pd.to_numeric(df["nr_canje"], errors="coerce").fillna(0)
    df["venta_umv"] = pd.to_numeric(df["venta_umv"], errors="coerce").fillna(0)

    # Estandarizar texto clave
    df["tipo_de_cliente_real"] = df["tipo_de_cliente_real"].astype(str).str.strip()
    df["agrupador"] = df["agrupador"].astype(str).str.strip()

    return df
