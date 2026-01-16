from flask import Flask, render_template, request
import csv

from flask import Flask

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)

from flask import send_from_directory

@app.route("/google1b16542a751c4bae.html")
def google_verify():
    return send_from_directory("static", "google1b16542a751c4bae.html")

def load_csv(path, key, value):
    data = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[row[key]] = row[value]
    return data

FOOD_CALORIES = {k:int(v) for k,v in load_csv("foods.csv","name","calorie").items()}
FOOD_RECIPES = load_csv("recipes.csv","name","recipe")

RECOMMENDED = {
    "male": [(18,29,2650),(30,49,2700),(50,150,2500)],
    "female": [(18,29,2000),(30,49,2050),(50,150,1950)]
}
AVERAGE = 2300

def recommended_cal(gender, age):
    if not gender or not age:
        return AVERAGE
    age = int(age)
    for a,b,c in RECOMMENDED[gender]:
        if a <= age <= b:
            return c
    return AVERAGE

def eaten_cal(text):
    total = 0
    for f in text.split(","):
        f = f.strip()
        if f in FOOD_CALORIES:
            total += FOOD_CALORIES[f]
    return total

def suggest(remain):
    result = []
    for name, cal in FOOD_CALORIES.items():
        if cal <= remain and name in FOOD_RECIPES:
            result.append({
                "name": name,
                "calorie": cal,
                "recipe": FOOD_RECIPES[name]
            })
    return result

@app.route("/", methods=["GET","POST"])
def index():
    data = None
    if request.method == "POST":
        gender = request.form.get("gender")
        age = request.form.get("age")
        eaten = request.form.get("eaten")

        rec = recommended_cal(gender, age)
        eaten_c = eaten_cal(eaten)
        remain = rec - eaten_c

        data = {
            "recommended": rec,
            "eaten": eaten_c,
            "remain": remain,
            "foods": suggest(remain)
        }
    return render_template("index.html", data=data)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)