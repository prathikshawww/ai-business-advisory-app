import spacy
nlp = spacy.load("en_core_web_sm")

def process_query(query):
    doc = nlp(query)

    # Extract entities (dates, numbers, etc.)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Simple intent detection
    if "profit" in query.lower():
        return "financial_profit", entities
    elif "revenue" in query.lower() and "expenses" in query.lower():
        return "compare_financials", entities
    elif "growth" in query.lower():
        return "financial_revenue_growth", entities
    else:
        return "unknown", entities
