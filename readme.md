## Insurance Document Extraction Pipeline (Config-Driven)

# Overview

This project implements a production-ready, config-driven text extraction pipeline for insurance documents and emails.

It extracts structured insurance fields (like policy number, limit of liability, deductible) from noisy unstructured text, while ensuring:

- High precision

- Safe failure (never crashes)

- Explicit ambiguity handling

- Explainable confidence scoring

- Stable, predictable output schema

The pipeline is designed with real-world insurance workflows in mind, where data can appear in emails, documents, and attachments with inconsistencies.

# Key Features

- Config-driven architecture (no hardcoding)
- Email > document priority handling
- Noise filtering (signatures, contact info, footers)
- Ambiguity-safe extraction (never guesses)
- Dynamic confidence scoring
- Required vs optional field validation
- Metadata for traceability (run ID, timestamp, version)
- Production-style structured JSON output

# Architecture
Raw Text (Email / Document)
        ↓
Text Cleaning
        ↓
Noise Filtering
        ↓
Regex-based Extraction
        ↓
Ambiguity Detection
        ↓
Priority Resolution (Email > Document)
        ↓
Confidence Scoring
        ↓
Validation (Required Fields)
        ↓
Final Structured JSON Output

# Supported Fields

| Field Name         | Required | Priority |
| ------------------ | -------- | -------- |
| policy_number      |   Yes    | Email    |
| limit_of_liability |   Yes    | Email    |
| deductible         |   No     | Email    |

- New fields can be added by updating configuration only, without changing pipeline logic.


# 🧩 Configuration-Driven Design

All field behavior is controlled via a single configuration object:

```python
{
  "metadata": {
    "run_id": "uuid",
    "timestamp": "ISO-8601",
    "pipeline_version": "v1.0-day15"
  },
  "fields": {
    "policy_number": {
      "value": "PN-45678",
      "source": "email",
      "confidence": 0.95,
      "required": true,
      "reason": null
    },
    "limit_of_liability": {
      "value": 5000000,
      "source": "email",
      "confidence": 0.9,
      "required": true,
      "reason": null
    },
    "deductible": {
      "value": null,
      "source": null,
      "confidence": 0.0,
      "required": false,
      "reason": "not_found"
    }
  }
}
```

- This allows the pipeline to scale to dozens of fields without rewriting code.

# Output Schema 

Every run produces a stable, predictable JSON structure:

FIELD_CONFIG = {
    "policy_number": {
        "extractor": extract_policy_number,
        "priority": "email",
        "required": True
    },
    "limit_of_liability": {
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


# Confidence Scoring Logic

Confidence is deterministic and explainable, not guessed:

| Signal                          | Weight |
| ------------------------------- | ------ |
| Value exists                    | +0.4   |
| Trusted source (email/document) | +0.3   |
| Unique match (no ambiguity)     | +0.2   |
| Required field                  | +0.1   |


Final confidence is capped at 1.0.

# Safety & Reliability

- Extractors never crash the pipeline

- Ambiguous values are rejected

- Missing fields are explicitly marked

- Required field failures are flagged

- Output schema is always preserved

Wrong data is worse than missing data — this pipeline enforces that principle.

# 🧪 Example Usage
output = run_pipeline(email_text, document_text)
print(output)


The pipeline automatically:

- Cleans and filters input

- Applies extraction rules

- Resolves source priority

- Calculates confidence

- Returns structured output

# 🧑‍💻 Skills Demonstrated

- Python

- Regex-based extraction

- Config-driven system design

- Data validation & normalization

- Confidence scoring

- Fault-tolerant pipelines

- Insurance domain understanding

- AI Data Engineering principles

# 📌 Future Enhancements

Multi-document aggregation

LLM-assisted fallback extraction

Field-level confidence calibration

Schema validation (JSON Schema / Pydantic)

Batch processing support

# 📄 License

This project is for learning and demonstration purposes.

