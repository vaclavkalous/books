import logging
import os
import sys

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

        # select books that LOTR users rated
        lotr_users = df[df["Book-Title"].isin(LOTR_BOOK_NAMES)][
            "User-ID"
        ].unique()
        lotr_users_books = df[df["User-ID"].isin(lotr_users)]

        # select books that have at least 8 ratings
        relevant_books = (
            lotr_users_books.groupby("Book-Title")
            .agg({"User-ID": "nunique"})
            .query("`User-ID`>=8")
            .index
        )

        # get rating of book per user
        relevant_ratings = lotr_users_books[
            lotr_users_books["Book-Title"].isin(relevant_books)
        ].pivot_table(
            index="User-ID", columns="Book-Title", values="Book-Rating"
        )

        corr = relevant_ratings.corr()
        avg_rating = (
            lotr_users_books[
                lotr_users_books["Book-Title"].isin(relevant_books)
            ]
            .groupby("Book-Title", as_index=False)
            .agg(average_rating=("Book-Rating","mean"),
                number_of_ratings=("Book-Rating", "count"))
        )

        for book in LOTR_BOOK_NAMES:
            rec = (
                corr[corr.index == book]
                .drop(LOTR_BOOK_NAMES, axis=1)
                .transpose()
                .merge(avg_rating, on="Book-Title")
                .rename(columns={f"{book}": f"Corr with {book}"})
                .nlargest(10, f"Corr with {book}")
                .to_string(index=False)
            )

            print(f"Recomended books for {book}: \n {rec}")

        return 0

    except Exception:
        logger.error("Failed to create book recommendation", exc_info=True)
        return 1


if __name__ == "__main__":
    status = main()
    sys.exit(status)
