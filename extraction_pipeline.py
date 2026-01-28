from datetime import datetime, timezone
import uuid

def build_metadata():
    return {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "v1.0-day15"
    }

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

def wrap_field(value, source, config, confidence, reason=None):
    return {
        "value": value,
        "source": source,
        "confidence": confidence,
        "required": config.get("required", False),
        "reason": reason
    }


#-------------- Field Validation ------------
def validate_required(field_name, wrapped_field, config):
    if config.get("required") and wrapped_field["value"] is None:
        wrapped_field["reason"] = "required_field_missing"
    return wrapped_field

#------------ Confidence Calculator ------------

def calculate_confidence(value, source, is_required, is_unique=True):
    confidence = 0.0

    if value is not None:
        confidence += 0.4

        if source in ["email", "document"]:
            confidence += 0.3

        if is_unique:
            confidence += 0.2

        if is_required:
            confidence += 0.1

    return round(min(confidence, 1.0), 2)


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

    if value is None:
        reason = "required_field_missing" if config.get("required") else "not_found"
        confidence = 0.0
    else:
        confidence = calculate_confidence(
            value=value,
            source=source,
            is_required=config.get("required", False),
            is_unique=True
        )
        reason = None

    wrapped = wrap_field(value, source, config, confidence, reason)

    return validate_required(field_name, wrapped, config)

# ---------- Final Pipeline ----------
def run_pipeline(email_text, doc_text):
    email_lines = filter_lines(clean_text(email_text))
    doc_lines = filter_lines(clean_text(doc_text))

    result = {
	"metadata": build_metadata(),
        "fields": {}
	}

    for field, config in FIELD_CONFIG.items():
        result["fields"][field] = process_field(
            field, config, email_lines, doc_lines
        )

    return result

    
output = run_pipeline(email_text, doc_text)
print(output)

