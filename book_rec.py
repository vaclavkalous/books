import logging
import os
import pprint
import sys

import pandas as pd

from common import get_books_df

logger = logging.getLogger("book_rec")
logging.basicConfig(
    stream=sys.stdout, level=os.getenv("LOG_LEVEL", logging.INFO)
)
logging.captureWarnings(True)

LOTR_BOOK_NAMES = [
    "fellowship of the ring",
    "two towers",
    "return of the king",
]


def main():
    try:
        # load data
        df = get_books_df()

        # unify book titles case-wise
        df["Book-Title"] = df["Book-Title"].str.lower()

        # select LOTR books based on names in trilogy
        lotr_books = df[
            (
                df["Book-Author"]
                .str.contains("tolkien", case=False)
                .fillna(False)
            )
            & (df["Book-Title"].str.contains("|".join(LOTR_BOOK_NAMES)))
        ]["Book-Title"].unique()

        # unfiy LOTR book names into three distinct values
        lotr_name_conversion = {
            book: next(
                (name for name in LOTR_BOOK_NAMES if name in book), None
            )
            for book in lotr_books
        }

        df["Book-Title"].replace(lotr_name_conversion, inplace=True)

        lotr_users = df[df["Book-Title"].isin(LOTR_BOOK_NAMES)][
            "User-ID"
        ].unique()
        lotr_users_books = df[df["User-ID"].isin(lotr_users)]

        relevant_books = (
            lotr_users_books.groupby("Book-Title")
            .agg({"User-ID": "nunique"})
            .query("`User-ID`>=8")
            .index
        )

        relevant_ratings = (
            lotr_users_books[
                lotr_users_books["Book-Title"].isin(relevant_books)
            ]
            .groupby(["User-ID", "Book-Title"], as_index=False)
            .agg({"Book-Rating": "mean"})
            .pivot(index="User-ID", columns="Book-Title", values="Book-Rating")
        )

        corr = relevant_ratings.corr()
        avg_rating = (
            lotr_users_books[
                lotr_users_books["Book-Title"].isin(relevant_books)
            ]
            .groupby("Book-Title", as_index=False)
            .agg({"Book-Rating": "mean"})
        )

        for l in LOTR_BOOK_NAMES:
            f = (
                corr[corr.index == l]
                .transpose()
                .merge(avg_rating, on="Book-Title")
                .rename(columns={f"{l}": f"Corr with {l}"})
                .nlargest(10, f"Corr with {l}")
                .to_string()
            )

            print(f"recomended books for {l}: {f}")

        return 0

    except Exception:
        logger.error("Failed to create book recommendation", exc_info=True)


if __name__ == "__main__":
    status = main()
    sys.exit(status)
