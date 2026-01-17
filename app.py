from flask import Flask, render_template, request, send_from_directory
import csv
import os

# =====================
# Flask App
# =====================
app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

# =====================
# Google Search Console 用
# =====================
@app.route("/google1b16542a751c4bae.html")
def google_verify():
    return send_from_directory("static", "google1b16542a751c4bae.html")

# =====================
# CSV Utility
# =====================
def load_csv(path, key, value):
    data = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[row[key]] = row[value]
    return data

def load_food_names():
    with open("foods.csv", encoding="utf-8") as f:
        return [row["name"] for row in csv.DictReader(f)]

# =====================
# Data Load
# =====================
FOOD_CALORIES = {
    k: int(v) for k, v in load_csv("foods.csv", "name", "calorie").items()
}
FOOD_RECIPES = load_csv("recipes.csv", "name", "url")

RECOMMENDED = {
    "male": [(18, 29, 2650), (30, 49, 2700), (50, 150, 2500)],
    "female": [(18, 29, 2000), (30, 49, 2050), (50, 150, 1950)]
}
AVERAGE = 2300

# =====================
# Logic
# =====================
def recommended_cal(gender, age):
    if not gender or not age:
        return AVERAGE
    age = int(age)
    for a, b, c in RECOMMENDED.get(gender, []):
        if a <= age <= b:
            return c
    return AVERAGE

def eaten_cal(text):
    if not text:
        return 0
    total = 0
    for f in text.split(","):
        f = f.strip()
        if f in FOOD_CALORIES:
            total += FOOD_CALORIES[f]
    return total

def suggest(remain):
    results = []
    for name, cal in FOOD_CALORIES.items():
        if cal <= remain and name in FOOD_RECIPES:
            results.append({
                "name": name,
                "calorie": cal,
                "url": FOOD_RECIPES[name]
            })
    return results

# =====================
# Routes
# =====================
@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    food_names = load_food_names()

    if request.method == "POST":
        gender = request.form.get("gender")
        age = request.form.get("age")
        eaten = request.form.get("foods")

        rec = recommended_cal(gender, age)
        eaten_c = eaten_cal(eaten)
        remain = rec - eaten_c

        data = {
            "recommended": rec,
            "eaten": eaten_c,
            "remain": remain,
            "foods": suggest(remain)
        }

    return render_template(
        "index.html",
        data=data,
        food_names=food_names
    )

@app.route("/about")
def about():
    return render_template("about.html")

# =====================
# Run
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
