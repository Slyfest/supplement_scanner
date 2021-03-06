from typing import List

import cv2
import pandas as pd
import pytesseract
from flashtext import KeywordProcessor

custom_config = r"-l eng+rus"


def prepare_text(text: str) -> str:
    return text.replace("Е", "E").replace("£", "E").replace("‘", "").replace("E-", "E").lower()


def extract_text_from_image(img) -> str:
    text1 = pytesseract.image_to_string(img, config=custom_config)
    text2 = pytesseract.image_to_string(cv2.bitwise_not(img), config=custom_config)

    text = text1 if len(text1) > len(text2) else text2
    return prepare_text(text)


def load_image(image_path):
    return cv2.imread(image_path)


def load_data():
    df = pd.read_csv("data/supplements.csv")
    title_processor = KeywordProcessor()
    e_title_processor = KeywordProcessor()

    title_processor.add_keywords_from_list(list(df["title"].values))
    e_title_processor.add_keywords_from_list(list(df["numeric_title"].values))

    return df, title_processor, e_title_processor


def prepare_output(
    found_titles: List[str], found_e_titles: List[str], df: pd.DataFrame
) -> pd.DataFrame:
    titles_df = df[df["title"].isin(found_titles)]
    e_titles_df = df[df["numeric_title"].isin(found_e_titles)]

    return pd.concat([titles_df, e_titles_df]).to_dict("records")


def extract_supplements_from_image(image_path: str) -> pd.DataFrame:
    df, title_processor, e_title_processor = load_data()
    image = load_image(image_path)
    text = extract_text_from_image(image)

    found_titles = title_processor.extract_keywords(text)
    found_e_titles = e_title_processor.extract_keywords(text)

    result = prepare_output(found_titles, found_e_titles, df)
    return result


def extract_supplements_from_text(text: str) -> pd.DataFrame:
    text = prepare_text(text)
    df, title_processor, e_title_processor = load_data()

    found_titles = title_processor.extract_keywords(text)
    found_e_titles = e_title_processor.extract_keywords(text)

    result = prepare_output(found_titles, found_e_titles, df)
    return result
