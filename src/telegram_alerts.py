"""Generación y envío de alertas comerciales por Telegram."""

from __future__ import annotations

import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


def build_telegram_messages(df) -> Dict[str, str]:
    """Genera mensajes agrupados por BK."""
    messages = {}
    if df.empty:
        return messages

    for bk, g in df.groupby("BK"):
        lines: List[str] = ["🚨 CLIENTES SIN COMPRA EN ABRIL 2026", "", f"📍 BK: {bk}", ""]
        for idx, row in enumerate(g.itertuples(index=False), start=1):
            lines.extend(
                [
                    f"{idx}. {row.nombre_cliente_real}",
                    f"ID: {row.cliente_id}",
                    f"Última compra: {row.ultima_fecha_compra.strftime('%d/%m/%Y')}",
                    f"Días sin compra: {row.dias_desde_ultima_compra}",
                    f"NR histórico: S/ {row.nr_canje_historico:,.0f}",
                    f"Unidades históricas: {row.unidades_historicas:,.0f}",
                    f"SKUs habituales: {row.skus_principales}",
                    f"Prioridad: {row.prioridad}",
                    "Acción sugerida: contactar esta semana y ofrecer reposición de sus SKUs habituales.",
                    "",
                ]
            )
        messages[bk] = "\n".join(lines)

    return messages


def send_telegram_message(text: str) -> tuple[bool, str]:
    """Envía un mensaje al chat configurado; falla de forma segura si falta configuración."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return False, "Credenciales de Telegram no configuradas en .env"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        return True, "Mensaje enviado correctamente"
    except requests.RequestException as exc:
        return False, f"Error al enviar mensaje: {exc}"
