import json
from flask import Flask, request, render_template

app = Flask(__name__)

# Function to load size charts from the JSON file
def load_size_charts():
    with open("size_charts.json", "r") as file:
        return json.load(file)

# Load size charts into a global variable
size_charts = load_size_charts()

def parse_range(value):
    """Parse a range in the format 'min-max' and return the midpoint as a float."""
    value = str(value)
    if "-" in value:
        min_val, max_val = map(float, value.split("-"))
        return (min_val + max_val) / 2
    return float(value)

def recommend_size(unfamiliar_brand, familiar_brand, familiar_size, category):
    familiar_measurements = size_charts[familiar_brand][category].get(familiar_size)
    
    if not familiar_measurements:
        return "Invalid size entered for the familiar brand."

    # Parse familiar measurements to get midpoints
    familiar_measurements = {dim: parse_range(val) for dim, val in familiar_measurements.items()}
    
    min_diff = float('inf')
    recommended_size = None
    
    for size, measurements in size_charts[unfamiliar_brand][category].items():
        measurements = {dim: parse_range(val) for dim, val in measurements.items()}
        diff = sum(abs(familiar_measurements[dim] - measurements[dim]) for dim in familiar_measurements)
        
        if diff < min_diff:
            min_diff = diff
            recommended_size = size
    
    return recommended_size

@app.route("/", methods=["GET", "POST"])
def index():
    brands = list(size_charts.keys())  # Get the list of brand names
    result = None

    if request.method == "POST":
        unfamiliar_brand = request.form["unfamiliar_brand"]
        category = request.form["category"]
        familiar_brand = request.form["familiar_brand"]
        familiar_size = request.form["familiar_size"].upper()

        if unfamiliar_brand not in size_charts or familiar_brand not in size_charts:
            result = "One of the brands is not in the size chart database."
        
        if category not in size_charts[familiar_brand]:
            result = "This category is not available for the familiar brand."
        else:
            result = f"Your recommended size for {unfamiliar_brand} for {category} is: {recommend_size(unfamiliar_brand, familiar_brand, familiar_size, category)}"
    
    return render_template("index.html", brands=brands, result=result)

if __name__ == "__main__":
    app.run(debug=True)
