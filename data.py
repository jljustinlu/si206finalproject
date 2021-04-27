import requests
import random
from bs4 import BeautifulSoup
import sqlite3
import json
import os
import numpy as np
import matplotlib.pyplot as plt

def get_activities():
    # get activities from Bored API
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
    location = "&country_id=US"
    for i in range(10):
        name = random.choice(names[0])
        url = base + name + location
        call = requests.get(url)
        ages[name] = call.json()["age"]
    for i in range(10):
        name = random.choice(names[1])
        url = base + name + location
        call = requests.get(url)
        ages[name] = call.json()["age"]
    return ages


def set_database(db):
    # set up database cursor and connection
    path = os.path.dirname(os.path.abspath(__file__))
    con = sqlite3.connect(path + "/" + db)
    cur = con.cursor()
    return cur, con

def write_database_ages(ages, cur, con):
    cur.execute("CREATE TABLE IF NOT EXISTS Ages (Name TEXT PRIMARY KEY, Age INTEGER)")
    for name, age in ages.items():
        cur.execute("INSERT OR IGNORE INTO Ages (Name, Age) VALUES (?, ?)", (name, age))
    con.commit()

def calculate_average_age(cur, con):
    cur.execute("SELECT AVG(Age) FROM Ages")

def make_graph_ages(cur, con):
    cur.execute("SELECT * FROM Ages")
    rows = cur.fetchall()
    names = []
    ages = []
    for row in rows:
        names.append(row[0])
        ages.append(row[1])
    
    x = np.array(names)
    y = np.array(ages)
    plt.scatter(x, y)
    plt.ylabel("Age")
    plt.xlabel("Name")
    plt.title("Ages of Most Popular Names in the United States from 1920-2019")
    plt.show()


def write_database_activities(activities, cur, con):
    # write to the database file
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
    cur.execute("CREATE TABLE IF NOT EXISTS Average_Price (Type TEXT PRIMARY KEY, Price DOUBLE(3, 2))")
    for name, average in averages.items():
        average = float(average[0])
        cur.execute("INSERT OR IGNORE INTO Average_Price (Type, Price) VALUES (?, ?)", (name, average))
    con.commit()


def calculate_average_accessibility(cur, con):
    types = ["education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork"]
    averages = {}
    for name in types:
        cur.execute("SELECT AVG(Accessibility) FROM Activities WHERE Type = ?", (name,))
        averages[name] = cur.fetchone()
    cur.execute("CREATE TABLE IF NOT EXISTS Average_Accessibility (Type TEXT PRIMARY KEY, Accessibility DOUBLE(3, 2))")
    for name, average in averages.items():
        average = float(average[0])
        cur.execute("INSERT OR IGNORE INTO Average_Accessibility (Type, Accessibility) VALUES (?, ?)", (name, average))
    con.commit()

def join_averages(cur, con):
    cur.execute("CREATE TABLE IF NOT EXISTS Combined (Type TEXT PRIMARY KEY, Price DOUBLE(3, 2), Accessibility DOUBLE(3, 2))")
    cur.execute("SELECT Average_Price.Type, Average_Price.Price, Average_Accessibility.Accessibility FROM Average_Accessibility JOIN Average_Price ON Average_Price.Type = Average_Accessibility.Type")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("INSERT OR IGNORE INTO Combined (Type, Price, Accessibility) VALUES (?, ?, ?)", row)
    con.commit()

def make_graph_activities(cur, con):
    n_groups = 9

    types = ("education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork")
    y_pos = np.arange(len(types))
    accessibility = []
    prices = []

    for name in types:
        cur.execute("SELECT Price FROM Average_Price WHERE Type = ?", (name,))
        prices.append(float(cur.fetchone()[0]))
    
    for name in types:
        cur.execute("SELECT Accessibility FROM Average_Accessibility WHERE Type = ?", (name,))
        accessibility.append(float(cur.fetchone()[0]))
    
    means_accessibility = tuple(accessibility)
    means_price = tuple(prices)

    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = .25
    opacity = .5

    rects1 = plt.bar(index, means_accessibility, bar_width, alpha = opacity, color = "b", label = "Accessibility")
    rects2 = plt.bar(index, means_price, bar_width, alpha = opacity, color = "r", label = "Price")

    plt.xlabel("Type")
    plt.ylabel("Score")
    plt.title("Accessibility and Price by Activity Type")
    plt.xticks(index + bar_width, types)
    plt.legend()
    plt.tight_layout()

    plt.show()

def main():
    activities = get_activities()
    names = get_names()
    ages = get_ages(names)
    cur, con = set_database("data.db")
    write_database_ages(ages, cur, con)
    write_database_activities(activities, cur, con)
    calculate_average_age(cur, con)
    calculate_average_price(cur, con)
    calculate_average_accessibility(cur, con)
    join_averages(cur, con)
    make_graph_activities(cur, con)
    make_graph_ages(cur, con)

if __name__ == "__main__":
    main()