"""Deterministic rules engine — cleansing, normalisation and house-style enforcement.

Implements the Unilog content-standard mechanics without any AI:
- Placeholder detection ("-- Unbranded --" etc. are NOT data)
- Manufacturer string parsing ("Freud Inc (2435)" -> name + code)
- Trade-abbreviation expansion (SS -> Stainless Steel, WH -> White, ...)
- UOM normalisation to a single approved abbreviation per measurement type
- Decimal <-> fractional inch conversion (0.5 -> 1/2, 50.25 in -> 50-1/4 in)
- Character-limit enforcement for description fields
"""

import re
from fractions import Fraction

# --------------------------------------------------------------------------
# Placeholders
# --------------------------------------------------------------------------

PLACEHOLDERS = {
    "-- unbranded --",
    "-- no unilog brand --",
    "-- no dib brand --",
    "-",
    "--",
    "n/a",
    "na",
    "none",
}


def is_placeholder(value: str | None) -> bool:
    """True when a field looks empty / placeholder (case-insensitive)."""
    if value is None:
        return True
    v = str(value).strip()
    return not v or v.lower() in PLACEHOLDERS


def clean(value: str | None) -> str:
    """Return stripped text, or '' for placeholders."""
    if value is None:
        return ""
    v = str(value).strip()
    return "" if is_placeholder(v) else v


# --------------------------------------------------------------------------
# Manufacturer parsing
# --------------------------------------------------------------------------

_MANUF_CODE_RE = re.compile(r"^(?P<name>.+?)\s*\((?P<code>[A-Za-z0-9]+)\)$")


def parse_manufacturer(raw: str) -> tuple[str, str]:
    """Split 'Freud Inc (2435)' -> ('Freud Inc', '2435').

    Returns (clean_name, code); code may be ''.
    """
    raw = clean(raw)
    if not raw:
        return "", ""
    m = _MANUF_CODE_RE.match(raw)
    if m:
        return m.group("name").strip(), m.group("code").strip()
    return raw, ""


# Canonical legal-entity suffix casing (normalise 'INC'/'inc' -> 'Inc' etc.)
_ENTITY_SUFFIXES = {
    "inc": "Inc",
    "llc": "LLC",
    "ltd": "Ltd",
    "co": "Co.",
    "corp": "Corp",
    "corporation": "Corporation",
    "company": "Company",
    "industries": "Industries",
    "industrial": "Industrial",
    "mfg": "Mfg.",
    "manufacturing": "Manufacturing",
    "products": "Products",
    "supply": "Supply",
    "usa": "USA",
    "us": "U.S.",
}


def normalise_entity_case(name: str) -> str:
    """Title-case each word but keep known suffix/acronym casing."""
    out: list[str] = []
    for token in name.split():
        low = token.lower().strip(".,")
        if token.isupper() and len(token) <= 4:  # acronym e.g. 3M, JAM
            out.append(token)
        elif low in _ENTITY_SUFFIXES:
            suffix = _ENTITY_SUFFIXES[low]
            trail = token[len(token.rstrip(".,")):]
            out.append(suffix + ("." if token.endswith(".") and not suffix.endswith(".") else "") + trail)
        else:
            out.append(token.capitalize())
    return " ".join(out)


# --------------------------------------------------------------------------
# Trade abbreviations (expansion dictionary)
# --------------------------------------------------------------------------

ABBREVIATIONS: dict[str, str] = {
    # materials / finishes
    "SST": "Stainless Steel", "SS": "Stainless Steel", "STL": "Steel",
    "CRS": "Cold Rolled Steel", "HRS": "Hot Rolled Steel", "GALV": "Galvanized",
    "BRZ": "Bronze", "BRASS": "Brass", "BRS": "Brass", "AL": "Aluminum",
    "ALUM": "Aluminum", "CU": "Copper", "ZN": "Zinc", "NYL": "Nylon",
    "PVC": "PVC", "ABS": "ABS", "HDPE": "HDPE", "PE": "Polyethylene",
    "PP": "Polypropylene", "CRTN": "Carbon",
    # colors
    "WH": "White", "BK": "Black", "BLK": "Black", "GRY": "Gray", "GY": "Gray",
    "BL": "Blue", "RD": "Red", "GN": "Green", "YL": "Yellow", "SL": "Silver",
    "GD": "Gold", "BEIGE": "Beige", "CHR": "Chrome",
    # product types
    "CPLG": "Coupling", "CPVG": "Coupling", "EL": "Ell", "ELL": "Ell",
    "BRG": "Bearing", "BRGS": "Bearings", "VLV": "Valve", "FLR": "Floor",
    "FLNG": "Flange", "NIP": "Nipple", "TEE": "Tee", "ADPT": "Adapter",
    "CONN": "Connector", "FITG": "Fitting", "FITGS": "Fittings", "HWY": "Hardware",
    "EQ": "Equipment", "ASM": "Assembly", "ASSY": "Assembly", "PKG": "Pack",
    "PWDR": "Powder",
    # electrical / lighting
    "LED": "LED", "MED": "Medium", "W": "Watt", "K": "Kelvin",
    "CRI": "CRI", "LUMEN": "Lumen", "DIM": "Dimmable", "ND": "Non-Dimmable",
    # misc trade terms
    "MINI": "Miniature", "MAXI": "Maximum", "STD": "Standard", "HVY": "Heavy",
    "LT": "Light Duty", "MD": "Medium Duty", "HD": "Heavy Duty",
    "SQ": "Square", "RD": "Round", "RECT": "Rectangular", "HEX": "Hexagon",
    "OD": "Outer Diameter", "ID": "Inner Diameter", "OA": "Overall",
    "CTR": "Center", "CNTR": "Center", "HORIZ": "Horizontal", "VERT": "Vertical",
    "EXT": "Exterior", "INT": "Interior", "COMPL": "Composite",
    "RAIL KIT": "Rail Kit",
}

# Multi-word first so longest-match wins
_ABBREV_SORTED = sorted(ABBREVIATIONS.items(), key=lambda kv: -len(kv[0]))

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z./'-]*")


def expand_abbreviations(text: str, max_expansions: int = 12) -> tuple[str, list[str]]:
    """Expand trade abbreviations to full words.

    Returns (expanded_text, [terms expanded]). Protects tokens with digits
    (model numbers like SST06G are untouched).
    """
    expanded_terms: list[str] = []

    def repl(match: re.Match) -> str:
        token = match.group(0)
        core = token.strip(".,'-")
        lookup = core.upper().rstrip(".")
        if lookup in ABBREVIATIONS and core.upper() != ABBREVIATIONS[lookup].upper():
            if len(expanded_terms) < max_expansions:
                expanded_terms.append(core)
                return token.replace(core, ABBREVIATIONS[lookup])
        return token

    text = _WORD_RE.sub(repl, text)
    return text, expanded_terms


# --------------------------------------------------------------------------
# UOM standards (approved abbreviation per unit family)
# --------------------------------------------------------------------------

UOM_APPROVED: dict[str, set[str]] = {
    # canonical -> acceptable spellings that map to it
    "in": {"in", "inch", "inches", "IN.", '"'},
    "ft": {"ft", "foot", "feet", "'"},
    "mm": {"mm", "millimeter", "millimeters"},
    "cm": {"cm", "centimeter", "centimeters"},
    "m": {"m", "meter", "meters"},
    "V": {"v", "volt", "volts"},
    "A": {"a", "amp", "amps", "ampere", "amperes"},
    "W": {"w", "watt", "watts"},
    "kW": {"kw", "kilowatt"},
    "dBA": {"dba", "decibel", "db"},
    "lb": {"lb", "lbs", "pound", "pounds"},
    "kg": {"kg", "kilogram", "kilograms"},
    "oz": {"oz", "ounce", "ounces"},
    "ga": {"ga", "gallon", "gallons", "gal"},
    "qt": {"qt", "quart", "quarts"},
    "psi": {"psi"},
    "rpm": {"rpm", "rev/min"},
    "hp": {"hp", "horsepower"},
    "°F": {"f", "degf", "deg f", "degrees fahrenheit", "°f"},
    "°C": {"c", "degc", "deg c", "degrees celsius", "°c"},
    "pc": {"pc", "pcs", "piece", "pieces"},
    "pk": {"pk", "pack"},
    "pr": {"pr", "pair", "pairs"},
    "cfm": {"cfm"},
    "lm": {"lm", "lumen", "lumens"},
    "K": {"k", "kelvin", "K"},  # color temperature, kept as e.g. 2700 K
    "k": {"k", "kelvin", "K"},
}
_UOM_LOOKUP = {
    alias.strip().lower(): canonical
    for canonical, aliases in UOM_APPROVED.items()
    for alias in aliases
}

_UOM_TOKEN_RE = re.compile(
    r"(?P<num>\d+(?:-\d+/\d+|\.\d+)?(?:/\d+)?)\s*(?P<unit>[A-Za-z°\"'/]{1,12})\.?"
)


def normalise_uom_text(text: str) -> tuple[str, list[str]]:
    """Normalise unit spellings to approved form with number spacing.

    '24 inches' -> '24 in';  '50.25 IN.' -> '50-1/4 in' handled by caller.
    Returns (text, [canonical units applied]).
    """
    applied: list[str] = []

    def repl(m: re.Match) -> str:
        num, unit = m.group("num"), m.group("unit")
        canon = _UOM_LOOKUP.get(unit.lower())
        if not canon:
            # inch/foot symbols
            if unit == '"':
                canon, num2 = "in", _fractional_inch_str(num)
                return f"{num2} {canon}"
            if unit == "'":
                return f"{num} ft"
            return m.group(0)
        applied.append(canon)
        if canon == "in":
            return f"{_fractional_inch_str(num)} in"
        if canon.upper() == "K":
            return f"{num} K"
        return f"{num} {canon}"

    return _UOM_TOKEN_RE.sub(repl, text), applied


# --------------------------------------------------------------------------
# Decimal <-> fraction (63rds precision, Unilog style)
# --------------------------------------------------------------------------

def decimal_to_fraction(value: float, max_denominator: int = 64) -> str | None:
    """0.25 -> '1/4'; 50.25 -> '50-1/4'; 1.0 -> '1'. None when not clean."""
    try:
        val_float = float(value)
        if val_float.is_integer():
            return str(int(val_float))
        whole = int(val_float)
        remainder = abs(val_float - whole)
    except (ValueError, TypeError, OverflowError):
        return None
    frac = Fraction(remainder).limit_denominator(max_denominator)
    if frac.denominator > max_denominator:
        return None
    if frac.numerator == 0:
        return str(whole)
    if frac.numerator == frac.denominator:
        return str(whole + (1 if val_float >= 0 else -1))
    if whole == 0:
        sign = "-" if val_float < 0 else ""
        return f"{sign}{frac.numerator}/{frac.denominator}"
    sign = "-" if val_float < 0 else ""
    return f"{sign}{abs(whole)}-{frac.numerator}/{frac.denominator}"


def _fractional_inch_str(num_token: str) -> str:
    """Convert numeric token to fractional-inch display form.

    '50.25' -> '50-1/4';  '8.5' -> '8-1/2';  '24' stays '24'.
    """
    tok = num_token.strip()
    if "." not in tok:
        return tok
    try:
        value = float(tok)
    except ValueError:
        return tok
    frac_form = decimal_to_fraction(value)
    return frac_form if frac_form else tok


def normalise_dimension_values(text: str) -> str:
    """Convert decimal dimensions inside free text to fraction+space+unit form."""
    text = re.sub(r"(\d+\.\d+)\s*-?\s*(?:in\b|inch|inches|\"|IN)",
                  lambda m: f"{_fractional_inch_str(m.group(1))} in", text)
    return text


# --------------------------------------------------------------------------
# Description house rules
# --------------------------------------------------------------------------

CHAR_LIMITS = {
    "invoice_desc": 40,
    "mobile_desc_min": 60,
    "mobile_desc_max": 80,
}


def enforce_invoice_desc(text: str, limit: int = CHAR_LIMITS["invoice_desc"]) -> str:
    """UPPERCASE, hard limit, truncated on a word boundary."""
    t = re.sub(r"\s+", " ", (text or "").strip()).upper()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut


def enforce_mobile_desc(text: str) -> str:
    """Target 60-80 chars; trim to <=80 on word boundary, pad guidance upstream."""
    t = re.sub(r"\s+", " ", (text or "").strip())
    if len(t) <= CHAR_LIMITS["mobile_desc_max"]:
        return t
    cut = t[: CHAR_LIMITS["mobile_desc_max"]]
    return cut.rsplit(" ", 1)[0] if " " in cut else cut


def title_case_keep_symbols(text: str) -> str:
    """Sentence-ish title case preserving acronyms and ®/™ marks."""
    minor = {"with", "and", "or", "the", "for", "of", "a", "an", "to", "in", "on"}
    words = text.split()
    out = []
    for i, w in enumerate(words):
        core = w.strip(",.-")
        if core.isupper() and len(core) <= 4:  # acronym
            out.append(w)
        elif i > 0 and core.lower() in minor:
            out.append(w.lower())
        elif w and w[0].isalpha():
            out.append(w[0].upper() + w[1:])
        else:
            out.append(w)
    return " ".join(out)


def strip_placeholders_from_desc(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text or "").strip()
