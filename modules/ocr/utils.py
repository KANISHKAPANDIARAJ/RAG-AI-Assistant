def filter_low_confidence(lines: list, threshold: float = 0.7) -> list:
    return [line for line in lines if line["confidence"] >= threshold]

def extract_text_only(lines: list) -> str:
    return "\n".join([line["text"] for line in lines])