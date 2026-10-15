from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

# ---------------------------------------------------------------------------
# Custom recognizer for Indian Aadhar numbers (XXXX-XXXX-XXXX)
# ---------------------------------------------------------------------------
AADHAR_PATTERN = Pattern(
    name="aadhar_pattern",
    regex=r"\b\d{4}-\d{4}-\d{4}\b",
    score=0.9,
)

aadhar_recognizer = PatternRecognizer(
    supported_entity="AADHAR_NUMBER",
    patterns=[AADHAR_PATTERN],
)

# ---------------------------------------------------------------------------
# Build the analyzer and anonymizer (created once at module load)
# ---------------------------------------------------------------------------
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(aadhar_recognizer)

anonymizer = AnonymizerEngine()

ENTITIES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "AADHAR_NUMBER"]


def redact_text(text: str) -> str:
    """
    Analyze *text* for PII and return a copy with all detected entities
    replaced by their entity-type label (e.g. <PERSON>, <AADHAR_NUMBER>).

    Entities covered:
      - PERSON
      - EMAIL_ADDRESS
      - PHONE_NUMBER
      - AADHAR_NUMBER  (custom: XXXX-XXXX-XXXX)
    """
    results = analyzer.analyze(text=text, entities=ENTITIES, language="en")

    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text


# ---------------------------------------------------------------------------
# Quick smoke-test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = (
        "Dear Rohan Mehta, your Aadhar 3456-7890-1234 has been linked "
        "to rohan.mehta@example.com. For queries call +91 98765 43210."
    )
    print("Original :", sample)
    print("Redacted :", redact_text(sample))
