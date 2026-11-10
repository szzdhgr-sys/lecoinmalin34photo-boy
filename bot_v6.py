"""Outils légers de fiabilité du bot Telegram (sans dépendances externes)."""

import re


def env_int(raw, default, minimum, maximum):
    """Lit un entier de configuration sans faire planter le démarrage."""
    try:
        value = int(str(raw).strip())
    except (ValueError, TypeError):
        value = default
    return max(minimum, min(maximum, value))


def configured_admin_ids(raw):
    """Accepte un ou plusieurs identifiants Telegram séparés par des virgules."""
    values = re.split(r"[\s,;]+", str(raw or "").strip())
    return {int(value) for value in values if value.isdecimal() and int(value) > 0}


def is_admin_user(chat_id, allowed_ids):
    """Fail-closed : sans ADMIN_USER_ID défini, aucune commande sensible."""
    try:
        return int(chat_id) in allowed_ids
    except (TypeError, ValueError):
        return False


def ordered_message_ids(values, limit=100):
    """Telegram copyMessages exige des IDs distincts, strictement croissants."""
    result = set()
    for value in values:
        if isinstance(value, bool):
            continue
        try:
            message_id = int(value)
        except (ValueError, TypeError):
            continue
        if message_id > 0:
            result.add(message_id)
    return sorted(result)[:max(1, min(100, limit))]


def format_uptime(seconds):
    """Durée lisible pour /ping et le diagnostic Railway."""
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        return f"{days}j {hours}h {minutes}min"
    if hours:
        return f"{hours}h {minutes}min"
    if minutes:
        return f"{minutes}min {seconds}s"
    return f"{seconds}s"
