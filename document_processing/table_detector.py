import pdfplumber
import pandas as pd


def detect_tables(pdf_file):

    tables = []

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            extracted = page.extract_tables()

            for table in extracted:

                df = pd.DataFrame(table)

                tables.append(df)

    return tables