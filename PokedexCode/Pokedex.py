import pandas as pd
from flask import Flask, render_template, abort, url_for, redirect, request, flash
from collections import OrderedDict
from thefuzz import process

app = Flask(__name__)
df = pd.read_csv("Pokedex/Pokemon.csv")
app.secret_key = "1n9ru48"

# make sure names don’t have trailing spaces
df['Name'] = df['Name'].str.strip()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["POST"])
def search():
    name = request.form["name"]
    return redirect(url_for("pokemon", name=name))

@app.route("/voice", methods=["POST"])
def voice():
    """Handle voice input sent from JavaScript"""
    name = request.form.get("name", "").strip()
    return redirect(url_for("pokemon", name=name))

@app.route("/<name>")
def pokemon(name):
    # First try exact match
    matched = df[df['Name'].str.lower() == name.lower()]

    if matched.empty:
        # If no exact match, try fuzzy matching
        choices = df['Name'].tolist()
        best_match, score = process.extractOne(name, choices)

        if score < 50:  # threshold to reject very weak matches
            flash("Not a Pokémon!")
            return render_template("home.html")

        # Use the best fuzzy match
        matched = df[df['Name'].str.lower() == best_match.lower()]

    row = matched.iloc[0].to_dict()

    image_url = None
    if "#" in row:
        index = row["#"]
        value = row.pop("#")
        row = OrderedDict([("Index", value)] + list(row.items()))

        image_url = f"/static/images/{index}.png"

    return render_template("index.html", row=row, image_url=image_url)

@app.route("/test")
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run(debug=True)