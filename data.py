import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import os

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




def main():
    get_names()


if __name__ == "__main__":
    main()