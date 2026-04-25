# Pricing per 1K tokens: (input_per_1k, output_per_1k)
_PRICING: dict = {
    "gpt-4o":            (0.0025, 0.0100),
    "gpt-4o-mini":       (0.0001, 0.0006),
    "gpt-4-turbo":       (0.0100, 0.0300),
    "gpt-3.5-turbo":     (0.0005, 0.0015),
    "claude-3-5-sonnet": (0.0030, 0.0150),
    "claude-3-5-haiku":  (0.0008, 0.0040),
    "claude-3-haiku":    (0.0003, 0.0013),
    "claude-3-opus":     (0.0150, 0.0750),
    "claude-3-sonnet":   (0.0030, 0.0150),
    "gemini-1.5-pro":    (0.0035, 0.0105),
    "gemini-1.5-flash":  (0.0001, 0.0004),
    "gemini-2.0-flash":  (0.0001, 0.0004),
    "unknown":           (0.0000, 0.0000),
}

_DISPLAY_NAMES: dict = {
    "gpt-4o-mini":       "gpt-4o-mini",
    "gpt-4o":            "gpt-4o",
    "gpt-4-turbo":       "gpt-4-turbo",
    "gpt-3.5-turbo":     "gpt-3.5-turbo",
    "claude-3-5-sonnet": "claude-3-5-sonnet",
    "claude-3-5-haiku":  "claude-3-5-haiku",
    "claude-3-haiku":    "claude-3-haiku",
    "claude-3-opus":     "claude-3-opus",
    "claude-3-sonnet":   "claude-3-sonnet",
    "gemini-1.5-pro":    "gemini-1.5-pro",
    "gemini-1.5-flash":  "gemini-1.5-flash",
    "gemini-2.0-flash":  "gemini-2.0-flash",
}


def _match_pricing_key(model: str) -> str:
    m = model.lower().strip()
    if "gpt-4o-mini" in m:
        return "gpt-4o-mini"
    if "gpt-4o" in m:
        return "gpt-4o"
    if "gpt-4-turbo" in m:
        return "gpt-4-turbo"
    if "gpt-3.5-turbo" in m:
        return "gpt-3.5-turbo"
    if "claude-3-5-sonnet" in m:
        return "claude-3-5-sonnet"
    if "claude-3-5-haiku" in m:
        return "claude-3-5-haiku"
    if "claude-3-haiku" in m:
        return "claude-3-haiku"
    if "claude-3-opus" in m:
        return "claude-3-opus"
    if "claude-3-sonnet" in m:
        return "claude-3-sonnet"
    if "gemini-2.0" in m and "flash" in m:
        return "gemini-2.0-flash"
    if "gemini-1.5-pro" in m:
        return "gemini-1.5-pro"
    if "gemini" in m and "flash" in m:
        return "gemini-1.5-flash"
    return "unknown"


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate cost in USD. Never raises an exception."""
    try:
        key = _match_pricing_key(str(model) if model is not None else "")
        input_rate, output_rate = _PRICING[key]
        cost = (prompt_tokens / 1000.0 * input_rate) + (completion_tokens / 1000.0 * output_rate)
        return round(cost, 8)
    except Exception:
        return 0.0


def get_model_display_name(model: str) -> str:
    """Return a clean display name for a model string."""
    try:
        key = _match_pricing_key(str(model) if model else "")
        return _DISPLAY_NAMES.get(key, model)
    except Exception:
        return model or "unknown"
