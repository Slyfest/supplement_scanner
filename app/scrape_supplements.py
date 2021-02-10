from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://calorizator.ru"


def load_page_content(url: str):
    page = requests.get(url)
    return page.content


def process_supplements(soup) -> List[dict]:
    supplements_containers = soup.find_all("td", class_="views-field views-field-title active")
    supplemets = [
        {"url": BASE_URL + x.find("a")["href"], "full_title": x.find("a").text.strip()}
        for x in supplements_containers
    ]
    return supplemets


def process_effects(soup) -> List[str]:
    effects_containers = soup.find_all("td", class_="views-field views-field-tid")
    effects = [x.find("a").text.strip() for x in effects_containers]
    return effects


def process_category(soup) -> str:
    category = soup.find("h1", id="page-title").text.strip()
    return category


def form_dataframe(category: str, supplements: List[dict], effects: List[str]) -> pd.DataFrame:
    df = pd.DataFrame.from_records(supplements)
    df["title"] = df["full_title"].apply(lambda x: " ".join(x.split(" ")[1:])).str.lower()
    df["numeric_title"] = df["full_title"].apply(lambda x: x.split(" ")[0])
    df["effect"] = effects
    df["category"] = category

    return df


def get_supplements(category: str) -> pd.DataFrame:
    url = f"{BASE_URL}/addon/{category}"
    content = load_page_content(url)

    soup = BeautifulSoup(content, "html.parser")
    category = process_category(soup)
    supplements = process_supplements(soup)
    effects = process_effects(soup)

    return form_dataframe(category, supplements, effects)


def postprocess_supplements_df(df: pd.DataFrame) -> pd.DataFrame:
    harm_list = ["Запрещенные", "Опасные для здоровья", "Канцерогенный эффект (вызывает рак)"]

    df["title"] = df["title"].apply(lambda x: x.split("(")[0].strip())
    df["is_harmful"] = df["effect"].isin(harm_list).astype(int)
    return df


if __name__ == "__main__":
    categories = ["e1xx", "e2xx", "e3xx", "e4xx", "e5xx", "e6xx", "e9xx", "e10xx"]

    dfs = []
    for cat in categories:
        dfs.append(get_supplements(cat))

    full_df = pd.concat(dfs)
    full_df = postprocess_supplements_df(full_df)
    full_df.to_csv("data/supplements.csv", index=False)
