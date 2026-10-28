import requests
from datetime import datetime

def send_discord_webhook(webhook_url: str, content: str = None, embeds: list = None) -> bool:
    """Envía un mensaje o embed al webhook de Discord especificado."""
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        return False
    
    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds
        
    try:
        response = requests.post(webhook_url, json=payload, timeout=8)
        return response.status_code in (200, 204)
    except Exception as e:
        print(f"Error enviando webhook a Discord: {e}")
        return False

def test_discord_webhook(webhook_url: str) -> tuple[bool, str]:
    """Prueba la conexión enviando un mensaje de prueba."""
    if not webhook_url or not webhook_url.strip():
        return False, "La URL del Webhook está vacía."
    
    embed = {
        "title": "✅ Conexión Exitosa con el Screener",
        "description": "Tu bot de alertas de trading ha sido configurado correctamente. Recibirás aquí las señales de Swing y Day Trading.",
        "color": 0x00FF88,  # Verde Neón
        "fields": [
            {"name": "Estado", "value": "🟢 Activo y escuchando", "inline": True},
            {"name": "Hora", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
        ],
        "footer": {"text": "Trading Screener Pro • Notificaciones"}
    }
    
    success = send_discord_webhook(webhook_url, embeds=[embed])
    if success:
        return True, "Mensaje de prueba enviado con éxito a Discord."
    return False, "No se pudo conectar. Verifica que la URL del Webhook sea válida."

def send_trade_alert(webhook_url: str, alert: dict, scan_type: str = "Swing Trading") -> bool:
    """Envía una alerta formateada de un ticker específico con diseño profesional."""
    ticker = alert.get("Ticker", "UNKNOWN")
    price = alert.get("Precio", 0.0)
    change_pct = alert.get("Cambio %", alert.get("Gap %", 0.0))
    pattern = alert.get("Patrón", scan_type)
    
    # Color según sentimiento / cambio
    color = 0x00FF88 if change_pct >= 0 else 0xFF3366  # Verde o Rojo
    
    fields = [
        {"name": "💵 Precio", "value": f"${price:.2f}", "inline": True},
        {"name": "📈 Variación", "value": f"{change_pct:+.2f}%", "inline": True},
        {"name": "🎯 Estrategia", "value": pattern, "inline": True}
    ]
    
    if "ADR (10s) %" in alert:
        fields.append({"name": "🎯 ADR (10d)", "value": f"{alert['ADR (10s) %']:.1f}%", "inline": True})
    if "Avg $Vol (20s) $M" in alert:
        fields.append({"name": "💵 Vol. Prom 20d", "value": f"${alert['Avg $Vol (20s) $M']:.1f}M", "inline": True})
    if "RVOL" in alert:
        fields.append({"name": "🔥 RVOL", "value": f"{alert['RVOL']:.2f}x", "inline": True})
    if "Posición Rango %" in alert:
        fields.append({"name": "📏 Cierre en Rango", "value": f"{alert['Posición Rango %']:.1f}%", "inline": True})
    if "RSI" in alert:
        fields.append({"name": "⚡ RSI (14)", "value": f"{alert['RSI']:.1f}", "inline": True})
    if "Dist_Max52w(%)" in alert:
        fields.append({"name": "🏔️ Dist. Max 52s", "value": f"{alert['Dist_Max52w(%)']:.1f}%", "inline": True})
    if "Vol Dólares ($M)" in alert:
        fields.append({"name": "💰 Vol. Dólares", "value": f"${alert['Vol Dólares ($M)']:.1f}M", "inline": True})
    if "Volumen" in alert:
        fields.append({"name": "📊 Volumen", "value": f"{int(alert['Volumen']):,}", "inline": True})
    
    chart_link = f"https://www.tradingview.com/chart/?symbol={ticker}"
    
    embed = {
        "title": f"🚨 ALERTA: {ticker} [{scan_type.upper()}]",
        "description": f"Se ha detectado una oportunidad de alta probabilidad en **{ticker}**.\n👉 [Abrir gráfico en TradingView]({chart_link})",
        "color": color,
        "fields": fields,
        "footer": {"text": f"Trading Screener • {datetime.now().strftime('%H:%M:%S')}"}
    }
    
    return send_discord_webhook(webhook_url, embeds=[embed])
