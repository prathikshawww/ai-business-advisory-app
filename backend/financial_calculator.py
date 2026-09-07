import re


def calculate(entities, question=""):
    amount = 0

    # First try existing NER-based entities
    for label, text in entities.items():
        if label in ("MONEY", "CARDINAL"):
            try:
                amount = float(text.replace(",", "").replace("₹", "").replace("$", "").strip())
                break
            except ValueError:
                continue

    # Fallback: pull the first plain number directly out of the question text
    if amount == 0 and question:
        match = re.search(r"[\d,]+(?:\.\d+)?", question)
        if match:
            amount = float(match.group().replace(",", ""))

    return {"calculation": f"Estimated profit is {amount * 1.2}"}