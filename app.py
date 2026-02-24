from flask import Flask, render_template, request, redirect
import csv
import os
import matplotlib.pyplot as plt
import time

app = Flask(__name__)
DATA_FILE = "data.csv"


@app.route("/")
def home():
    # Fresh start every time homepage loads
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    return render_template("index.html",
                           subjects=None,
                           percentages=None,
                           strongest=None,
                           weakest=None,
                           suggestion=None,
                           motivation=None,
                           graph=None)


@app.route("/add", methods=["POST"])
def add_data():
    subject = request.form["subject"]
    hours = request.form["hours"]

    try:
        hours = float(hours)
    except ValueError:
        return redirect("/")

    with open(DATA_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([subject, hours])

    return redirect("/report")


@app.route("/report")
def report():
    subjects = {}
    graph_file = None

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    subject, hours = row
                    hours = float(hours)
                    subjects[subject] = subjects.get(subject, 0) + hours

    strongest = None
    weakest = None
    suggestion = None
    motivation = None
    percentages = {}

    if subjects:
        total_hours = sum(subjects.values())

        for subject, hours in subjects.items():
            percentages[subject] = round((hours / total_hours) * 100, 1)

        strongest = max(subjects, key=subjects.get)
        weakest = min(subjects, key=subjects.get)

        suggestion = f"You should improve {weakest}. Try adding at least 1 extra hour daily."
        motivation = f"Excellent consistency in {strongest}! Keep pushing forward!"

        # 🔥 Generate graph again
        plt.figure()
        plt.bar(subjects.keys(), subjects.values())
        plt.xlabel("Subjects")
        plt.ylabel("Hours Studied")
        plt.title("Study Time Analysis")

        filename = f"graph_{int(time.time())}.png"
        filepath = os.path.join("static", filename)
        plt.savefig(filepath)
        plt.close()

        graph_file = filename

    return render_template("index.html",
                           subjects=subjects,
                           percentages=percentages,
                           strongest=strongest,
                           weakest=weakest,
                           suggestion=suggestion,
                           motivation=motivation,
                           graph=graph_file)


if __name__ == "__main__":
    app.run(debug=True)