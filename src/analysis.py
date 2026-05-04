"""Lógica de análisis comercial para detectar clientes sin compra en abril 2026."""

from __future__ import annotations

import pandas as pd

APRIL_START = pd.Timestamp("2026-04-01")
APRIL_END = pd.Timestamp("2026-04-30")
MARCH_START = pd.Timestamp("2026-03-01")
FEB_START = pd.Timestamp("2026-02-01")
REFERENCE_DATE = pd.Timestamp("2026-05-01")


def _top_values(series: pd.Series, top_n: int = 3) -> str:
    values = (
        series.dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .head(top_n)
        .index.tolist()
    )
    return ", ".join(values)


def _calc_avg_monthly_nr(df_customer: pd.DataFrame) -> float:
    monthly = (
        df_customer.assign(month=df_customer["FechaFacturacion"].dt.to_period("M"))
        .groupby("month", as_index=False)["nr_canje"]
        .sum()
    )
    if monthly.empty:
        return 0.0
    return float(monthly["nr_canje"].mean())


def _assign_priority(last_purchase: pd.Timestamp, nr_hist: float, nr_cutoff: float) -> str:
    if pd.isna(last_purchase):
        return "Baja"

    if MARCH_START <= last_purchase <= APRIL_START - pd.Timedelta(days=1) and nr_hist >= nr_cutoff:
        return "Alta"

    if FEB_START <= last_purchase <= APRIL_START - pd.Timedelta(days=1):
        return "Media"

    return "Baja"


def build_churn_table(df: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla de clientes que compraron antes de abril pero no en abril 2026."""
    base = df[
        (df["tipo_de_cliente_real"].str.lower() == "regular")
        & (df["agrupador"].str.lower() == "venta")
        & (df["FechaFacturacion"].notna())
    ].copy()

    before_april = base[base["FechaFacturacion"] < APRIL_START].copy()
    in_april = base[
        (base["FechaFacturacion"] >= APRIL_START) & (base["FechaFacturacion"] <= APRIL_END)
    ].copy()

    clients_before = set(before_april["cliente_id"].dropna().astype(str).unique())
    clients_april = set(in_april["cliente_id"].dropna().astype(str).unique())
    target_clients = clients_before - clients_april

    if not target_clients:
        return pd.DataFrame()

    hist_target = before_april[before_april["cliente_id"].astype(str).isin(target_clients)].copy()

    summary_rows = []
    nr_cutoff = hist_target.groupby("cliente_id")["nr_canje"].sum().quantile(0.75)

    for client_id, g in hist_target.groupby("cliente_id"):
        g = g.sort_values("FechaFacturacion")
        last_purchase = g["FechaFacturacion"].max()
        nr_hist = float(g["nr_canje"].sum())

        summary_rows.append(
            {
                "cliente_id": client_id,
                "nombre_cliente_real": g["nombre_cliente_real"].dropna().astype(str).iloc[-1]
                if not g["nombre_cliente_real"].dropna().empty
                else "",
                "BK": g["BK"].dropna().astype(str).iloc[-1] if not g["BK"].dropna().empty else "",
                "ultima_fecha_compra": last_purchase,
                "dias_desde_ultima_compra": int((REFERENCE_DATE - last_purchase).days),
                "nr_canje_historico": nr_hist,
                "promedio_mensual_nr_canje": _calc_avg_monthly_nr(g),
                "unidades_historicas": float(g["venta_umv"].sum()),
                "cantidad_compras_historicas": int(len(g)),
                "skus_principales": _top_values(g["nombre_sku"], top_n=3),
                "marcas_principales": _top_values(g["marca"], top_n=3),
                "subcategorias_principales": _top_values(g["subcategoria"], top_n=3),
                "prioridad": _assign_priority(last_purchase, nr_hist, float(nr_cutoff)),
            }
        )

    result = pd.DataFrame(summary_rows)
    priority_order = {"Alta": 0, "Media": 1, "Baja": 2}
    result["_priority_sort"] = result["prioridad"].map(priority_order).fillna(3)

    result = result.sort_values(
        by=["_priority_sort", "nr_canje_historico", "ultima_fecha_compra"],
        ascending=[True, False, False],
    ).drop(columns=["_priority_sort"])

    return result.reset_index(drop=True)
