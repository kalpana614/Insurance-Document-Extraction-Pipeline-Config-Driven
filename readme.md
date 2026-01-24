# Insurance Document Extraction Pipeline

## Overview
This Python-based project processes unstructured insurance emails and documents into structured JSON outputs.  
It implements cleaning, filtering, regex-based extraction, normalization, and priority logic for multiple sources.

## Features
- Text preprocessing and cleaning of emails and documents
- Regex-based extraction of policy number, limit of liability, and deductible
- Source prioritization and conflict resolution
- Config-driven framework for flexibility
- Schema-validated JSON outputs

## Tech Stack
- Python
- Regex
- JSON

## Usage
```python
from extraction_pipeline import extract_policy_data_with_priority

email_text = open("sample_email.txt").read()
doc_text = open("sample_doc.txt").read()

output = extract_policy_data_with_priority(email_text, doc_text)
print(output)
