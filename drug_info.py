import requests

def get_strengths(med_name):
    """Get all available strengths and forms for a medication"""
    url = "https://api.fda.gov/drug/ndc.json"

    res = requests.get(url, params={"search": f"generic_name:{med_name}", "limit": 20})
    data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        res = requests.get(url, params={"search": f"brand_name:{med_name}", "limit": 20})
        data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        return []

    strengths = set()
    for result in data["results"]:
        form = result.get("dosage_form", "")
        for ingredient in result.get("active_ingredients", []):
            strength = ingredient.get("strength", "")
            if strength and form:
                strengths.add(f"{strength} — {form.capitalize()}")
            elif strength:
                strengths.add(strength)

    return sorted(list(strengths))


def get_drug_info(med_name, strength=None):
    url = "https://api.fda.gov/drug/label.json"

    res = requests.get(url, params={"search": f"openfda.generic_name:{med_name}", "limit": 1})
    data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        res = requests.get(url, params={"search": f"openfda.brand_name:{med_name}", "limit": 1})
        data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        res = requests.get(url, params={"search": f"openfda.substance_name:{med_name}", "limit": 1})
        data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        res = requests.get(url, params={"search": med_name, "limit": 1})
        data = res.json() if res.status_code == 200 else {}

    if not data.get("results"):
        return None

    label = data["results"][0]

    def get_field(label, *keys):
        for key in keys:
            val = label.get(key)
            if val and val[0].strip():
                return val[0][:600]
        return "Not available"

    forms = label.get("openfda", {}).get("dosage_form", ["Not available"])
    routes = label.get("openfda", {}).get("route", ["Not available"])
    strengths = label.get("openfda", {}).get("strength", [])

    # Get dosage text and highlight the selected strength if provided
    dosage_text = get_field(label, "dosage_and_administration", "dosage_and_administration_table")
    if strength and strength != "Select strength":
        # Try to find the specific sentence mentioning this strength
        for sentence in dosage_text.split("."):
            if strength.lower() in sentence.lower():
                dosage_text = sentence.strip() + "."
                break

    return {
        "name": med_name.capitalize(),
        "form": forms[0].capitalize() if forms else "Not available",
        "route": ", ".join(routes).capitalize() if routes else "Not available",
        "strengths": strengths,
        "selected_strength": strength,
        "indications": get_field(label, "indications_and_usage", "purpose"),
        "dosage": dosage_text,
        "side_effects": get_field(label, "adverse_reactions", "side_effects", "warnings"),
        "warnings": get_field(label, "warnings", "warnings_and_cautions", "boxed_warning"),
        "interactions": get_field(label, "drug_interactions", "drug_and_or_laboratory_test_interactions"),
        "contraindications": get_field(label, "contraindications", "when_using", "do_not_use"),
        "food_interactions": get_field(label, "food_safety_warning", "ask_doctor_or_pharmacist"),
        "alcohol": get_field(label, "warnings", "ask_a_doctor_or_pharmacist_when_using_this_product"),
    }