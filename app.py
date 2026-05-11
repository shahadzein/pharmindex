from flask import Flask, request, render_template
from drug_info import get_drug_info, get_strengths

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    strengths = []
    selected_strength = None
    med_name = ""

    if request.method == "POST":
        med_name = request.form.get("med_name", "").strip()
        selected_strength = request.form.get("strength", "").strip()

        if med_name:
            # Always get available strengths
            strengths = get_strengths(med_name)

            # Only get full drug info if a strength was selected
            if selected_strength and selected_strength != "Select strength":
                result = get_drug_info(med_name, selected_strength)
                if not result:
                    error = f"No information found for '{med_name}'. Try a generic name like 'aspirin' or 'ibuprofen'."
            elif not strengths:
                # No strengths found, just show general info
                result = get_drug_info(med_name)
                if not result:
                    error = f"No information found for '{med_name}'."

    return render_template("index.html",
                           result=result,
                           error=error,
                           strengths=strengths,
                           selected_strength=selected_strength,
                           med_name=med_name)

if __name__ == "__main__":
    app.run(debug=False)