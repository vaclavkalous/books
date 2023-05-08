import logging
import os
import sys
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests
from lxml import html

logger = logging.getLogger("common")
logging.basicConfig(
    stream=sys.stdout, level=os.getenv("LOG_LEVEL", logging.INFO)
)
logging.captureWarnings(True)

BOOKS_DATASET_URL = "http://www2.informatik.uni-freiburg.de/~cziegler/BX/"


def get_books_df(
    download: bool = True,
    start_url: str = BOOKS_DATASET_URL,
    include_users: bool = False,
) -> pd.DataFrame:
    """Download a zipfile found on start_url
    and return a pandas DataFrame with its contents"""
    if download:
        try:
            session = requests.Session()
            req_dataset = session.get(start_url)
            req_dataset.raise_for_status()

            tree = html.fromstring(req_dataset.content)
            zipfile_href = tree.xpath(
                "//a[contains(text(),'CSV Dump')]/@href"
            )[0]
            zipfile_url = requests.compat.urljoin(start_url, zipfile_href)

            req_zipfile = session.get(zipfile_url)
            req_zipfile.raise_for_status()

            with ZipFile(BytesIO(req_zipfile.content)) as zipped:
                zipped.extractall("./data")
            logger.info("Successfuly decompressed books zipfile")
        except Exception:
            logger.error("Failed to access books zipfile", exc_info=True)
            return

    try:
        books = pd.read_csv(
            "./data/BX-Books.csv",
            encoding="cp1251",
            sep=";",
            on_bad_lines="warn",
            low_memory=False,
        )
        ratings = pd.read_csv(
            "./data/BX-Book-Ratings.csv",
            encoding="cp1251",
            sep=";",
            on_bad_lines="warn",
        )
        ratings = ratings[ratings["Book-Rating"] != 0]
        df = books.merge(ratings, on="ISBN")
        if include_users:
            users = pd.read_csv(
                "./data/BX-Users.csv",
                encoding="cp1251",
                sep=";",
                on_bad_lines="warn",
            )
            df = df.merge(right=users, on="User-ID")
        logger.info("Successfully read CSVs into a dataframe")

        return df

    except FileNotFoundError:
        logger.error(
            "Could not find CSV files in the ./data directory. Try running the function again and set download=True"  # noqa: E501
        )
        return

    except Exception:
        logger.error("Failed to read CSVs into a dataframe", exc_info=True)
        return
