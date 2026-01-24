email_text = """
Hello Team,

POLICY NO :   PN-45678

Some random footer text
Insured   Name: ABC Manufacturing Ltd

LIMIT OF LIABILITY : $5,000,000 USD

Phone: +61 987654321
Email: broker@test.com

Thanks,
Broker Team
"""
doc_text = """
Hello Team,

POLICY NO :   PN-45678

Some random footer text
Insured   Name: ABC Manufacturing Ltd

LIMIT OF LIABILITY : $5,000,000 USD



Thanks,
Broker Team
"""

import re

# ---------- Cleaning ----------
def clean_text(raw_text):
    lines = raw_text.lower().strip().split("\n")
    return [line.strip() for line in lines if line.strip()]

# ---------- Filtering ----------
SIGNATURE_KEYWORDS = ["regards", "thanks", "thank you", "sincerely"]
CONTACT_KEYWORDS = ["phone", "tel", "mobile", "www"]

def filter_lines(lines):
    filtered = []
    for line in lines:
        if any(sig in line for sig in SIGNATURE_KEYWORDS):
            break
        if "@" in line:
            continue
        if any(word in line for word in CONTACT_KEYWORDS):
            continue
        filtered.append(line)
    return filtered

# ---------- Extractors ----------
def extract_policy_number(lines):
    pattern = r"policy\s(no|number|#)\s*:\s*([a-z0-9-]+)"
    matches = []

    for line in lines:
        match = re.search(pattern, line)
        if match:
            matches.append(match.group(2))

    unique_matches = list(set(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    return None

def extract_limit(lines):
    pattern = r"limit\s*of\s*liability\s*:\s*([$]?[0-9,]+)"
    matches = []

    for line in lines:
        match = re.search(pattern, line)
        if match:
            value = match.group(1).replace(",", "").replace("$", "")
            matches.append(value)

    unique_matches = list(set(matches))
    if len(unique_matches) == 1:
        return int(unique_matches[0])
    return None

def extract_deductible(lines):
    pattern = r"deductible\s*:\s*([$]?[0-9,]+)"
    matches = []

    for line in lines:
        match = re.search(pattern, line)
        if match:
            value = match.group(1).replace(",", "").replace("$", "")
            matches.append(value)

    unique_matches = list(set(matches))
    if len(unique_matches) == 1:
        return int(unique_matches[0])
    return None

# ---------- Field Config ----------
FIELD_CONFIG = {
    "policy_number": {
        "extractor": extract_policy_number,
        "priority": "email",
        "required": True
        },
    "limit_of_liability":
        {
        "extractor": extract_limit,
        "priority": "email",
        "required": True
        },
    "deductible": {
        "extractor": extract_deductible,
        "priority": "email",
        "required": False
        }
}

# ---------- Field Level Wrapper----------
def wrap_field(value, source):
    return {
        "value": value,
        "source": source,
        "confidence": 1.0 if value is not None else 0.0
    }

# ---------- Safe Extraction ----------    
def safe_extract(extractor, lines):
    try:
        return extractor(lines)
    except Exception:
        return None

# ---------- Priority Handling ----------

def try_sources(extractor, primary_lines, secondary_lines):
    value = safe_extract(extractor, primary_lines)
    if value is not None:
        return value, "primary"

    value = safe_extract(extractor, secondary_lines)
    if value is not None:
        return value, "secondary"

    return None, None
    
def process_field(field_name, config, email_lines, doc_lines):
    extractor = config["extractor"]
    priority = config.get("priority", "email")

    if priority == "email":
        value, source = try_sources(extractor, email_lines, doc_lines)
        source = "email" if source == "primary" else "document"
    else:
        value, source = try_sources(extractor, doc_lines, email_lines)
        source = "document" if source == "primary" else "email"

    return wrap_field(value, source)

# ---------- Final Pipeline ----------
def run_pipeline(email_text, doc_text):
    email_lines = filter_lines(clean_text(email_text))
    doc_lines = filter_lines(clean_text(doc_text))

    result = {}

    for field, config in FIELD_CONFIG.items():
        result[field] = process_field(
            field, config, email_lines, doc_lines
        )

    return result

    
output = run_pipeline(email_text, doc_text)
print(output)
