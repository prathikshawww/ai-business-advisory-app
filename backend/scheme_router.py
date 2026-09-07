def find_scheme(entities):
    sector = entities.get("sector", "general")
    return {"scheme": f"Government scheme available for {sector} sector."}
