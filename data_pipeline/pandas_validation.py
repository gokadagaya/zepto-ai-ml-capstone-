import sqlite3
import pandas as pd


DATABASE_FILE = "data_pipeline/books.db"


connection = sqlite3.connect(
    DATABASE_FILE
)

print("Database connection successful.")