#!usr/bin/env python3

import time
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


def request_by_year(year, stars):
    return request(f"{year}-01-01", f"{year}-12-31", stars)


def request(begin, end, stars):
    print(f"[DEBUG] Begin<{begin}> End<{end}> Stars<{stars}>")
    url = f"https://github.com/search?q=created%3A{begin}..{end}+stars%3A%3E{stars}&type=Repositories"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"request error [r.status_code]: {r.text}")
        return
    return BeautifulSoup(r.text, "html.parser")


def now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S UTC")


def parser_total(soup):
    for h3 in soup.find_all("h3"):
        tmp = h3.get_text()
        if "repository results" in tmp:
            lst = [item for item in tmp.split() if item]
            if len(lst) > 0:
                return int(lst[0].replace(",", ""))


def parser_program(soup, other=True):
    result = list()
    for ul in soup.find_all("ul"):
        if "filter-list" in ul.get_attribute_list("class"):
            for li in ul.find_all("li"):
                lst = [item for item in li.get_text().split() if item]
                if len(lst) == 2:
                    result.append(lst)

    sizes = [int(item[0].replace(",", "")) for item in result]
    labels = [item[1] for item in result]

    if other:
        total = parser_total(soup)
        if total:
            sizes.append(total-sum(sizes))
            labels.append("Others")

    return sizes, labels


def pie(year, stars, sizes, labels):
    plt.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=600)
    plt.axis('equal')

    plt.title(
        f"""    
Distribution of programming languages used in new projects
[Year: {year}; Stars > {stars}; Source: Github Search]
{now()}
""")
    plt.tight_layout()
    plt.savefig(f"./images/pie_{year}.png")
    plt.close()


def line(lst, stars, includes=["Python", "Java", "Go", "TypeScript", "JavaScript"]):
    years = [item[0] for item in lst]
    totals = [sum(item[1]) for item in lst]
    l = len(years)
    lst = [dict(zip(item[2], item[1])) for item in lst]
    r = dict()

    for idx, d in enumerate(lst):
        for k, v in d.items():
            if k not in r:
                r[k] = [0] * l
            r[k][idx] = v/totals[idx] * 100

    for k, v in r.items():
        if k in includes:
            plt.plot([str(year) for year in years], v, label=k)

    plt.title(
        f"""    
Percentage of programming languages used in new projects
[Stars > {stars}; Source: Github Search]
{now()}
""")
    plt.xlabel("Years")
    plt.ylabel("Percentage")
    plt.legend()
    plt.tight_layout()
    plt.savefig("./images/line.png")
    plt.close()


def bar(lst, stars):
    years = [item[0] for item in lst]
    dat = [dict(zip(item[2], item[1])) for item in lst]
    totals = [sum(item[1]) for item in lst]
    l = len(years)

    d = dict()
    for idx, year in enumerate(years):
        for k, v in dat[idx].items():
            if k not in d:
                d[k] = [0] * l
            d[k][idx] = v
            d[k][idx] = v/totals[idx] * 100

    df = pd.DataFrame.from_dict(d, orient="index", columns=years)
    df.plot.bar(
        title=f"""
Percentage of programming languages used in new projects
[Stars > {stars}; Source: Github Search]
{now()}
""")

    plt.xlabel("Programming Languages")
    plt.ylabel("Percentage")
    plt.legend()
    plt.tight_layout()
    plt.savefig("./images/bar.png")
    plt.close()


def statistics_all(stars=10, interval=5):
    lst = list()
    years = list(range(2008, 2021))
    i = 0
    while i < len(years):
        soup = request_by_year(years[i], stars)
        if not soup:
            continue

        sizes, labels = parser_program(soup)
        lst.append((years[i], sizes, labels))
        i += 1
        if i < len(years):
            time.sleep(interval)
    return lst


def run():
    lst = statistics_all(10)

    # pie all
    for item in lst:
        pie(item[0], 10, item[1], item[2])

    # bar all
    bar(lst[-5:], 10)

    # line
    line(lst, 10)


if __name__ == "__main__":
    run()
