================
Book recommender
================

Overview
========

Code for downloading, processing and analyzing the books dataset.

Process description
===================

Prerequisities
--------------

Create Python virtual environment and install necessary packages::

    python3 -m venv --clear venv
    pip3 install -r requirements.txt
    pip3 install black flake8 isort

Downloading and obtaining the data
------------------------------------------------------

The script ``common.py`` contains code that downloads the zipfile with the most current version of books data (from http://www2.informatik.uni-freiburg.de/~cziegler/BX/) and returns a pandas dataframe with its contents. This script is used for fetching data in any subsequent programs, to use it run::

    ```python
    from common import get_books_df
    df = get_books_df()
    ```
Alternatively, if you do not need to download the data each time you use them, run::
    
    ```python
    df = get_books_df(download=False)
    ```

Suggesting books based on correlation
------------------------------------------------------

The ```book_rec.py`` contains improved version of the same script given in the assignment. To run it, type the following command into your terminal:: 

    python3 book_rec.py

The improvement of the script consist of:

    - removing the numpy dependency and using just the pandas library (which uses numpy internally)
    - avoiding superfluous variables
    - clearer naming of variables
    - using method chaining when manipultaing with dataframes
    - using pandas builtin methods and avoiding for-loops
    - using all three LOTR books in the computation and unifying the names of the lotr books into three distinct categories

Contribution guidelines
=======================

This repository uses isort_ to organize imports, Black_ to ensure consistent
code style and Flake8_ for linting. 

   isort .
   black .
   flake8 .

.. _isort: https://pycqa.github.io/isort/index.html
.. _Black: https://github.com/psf/black
.. _Flake8: https://github.com/PyCQA/flake8