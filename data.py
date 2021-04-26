import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import os

def get_activities():
    url = "http://www.boredapi.com/api/activity/"
    activities = {}
    
    for i in range(25):
        response = requests.get(url)
        data = response.json()
        activities[data["activity"]] = [data["type"], data["accessibility"], data["price"]]
    
    return activities

def get_names():
    # get the most common names from SSA
    response = requests.get("https://www.ssa.gov/oact/babynames/decades/century.html")
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find("table").find("tbody").find_all("tr")

    names = []
    male_names = []
    female_names = []

    for row in rows[:100]:
        data = row.find_all("td")

        male = data[1].get_text()
        female = data[3].get_text()

        male_names.append(male)
        female_names.append(female)
    
    names.append(male_names)
    names.append(female_names)

    return names

def get_ages(names):
    ages = {}
    base = "https://api.agify.io?name="
    for name_list in names:
        for name in name_list:
            url = base + name
            call = requests.get(url)
            ages[name] = call.json()["age"]
    
    return ages

def get_gender(names):
    genders = {}
    base = "https://api.genderize.io?name="
    for name_list in names:
        for name in name_list:
            url = base + name
            call = requests.get(url)
            genders[name] = call.json()["probability"]

    return genders

def set_database(db):
    path = os.path.dirname(os.path.abspath(__file__))
    con = sqlite3.connect(path + "/" + db)
    cur = con.cursor()
    return cur, con

def write_database(activities, cur, con):
    cur.execute("CREATE TABLE IF NOT EXISTS Activities (Activity TEXT PRIMARY KEY, Type TEXT, Accessibility TEXT, Price DOUBLE(3, 2))")
    for activity, data in activities.items():
        cur.execute("INSERT OR IGNORE INTO Activities (Activity, Type, Accessibility, Price) VALUES (?, ?, ?, ?)", (activity, data[0], data[1], data[2]))
    con.commit()

def calculate_average_price(cur, con):
    types = ["education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork"]
    averages = {}
    for name in types:
        cur.execute("SELECT AVG(Price) FROM Activities WHERE Type = ?", (name,))
        averages[name] = cur.fetchone()
    print(averages)
    return averages

def calculate_average_accessibility(cur, con):
    types = ["education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork"]
    averages = {}
    for name in types:
        cur.execute("SELECT AVG(Accessibility) FROM Activities WHERE Type = ?", (name,))
        averages[name] = cur.fetchone()
    print(averages)
    return averages

def main():
    activities = get_activities()
    names = get_names()
    get_ages(names)
    get_gender(names)
    cur, con = set_database("data.db")
    write_database(activities, cur, con)
    calculate_average_price(cur, con)
    calculate_average_accessibility(cur, con)

if __name__ == "__main__":
    main()