import pdfplumber
import pandas as pd
import json
import re

PDF_PATH = "Air Quality Data-VMC.pdf"   # Input PDF
OUTPUT_JSON = "air_quality_data.json"   # Output JSON file

def clean_table(table):
    df = pd.DataFrame(table[1:], columns=table[0])
    df = df.dropna(axis=1, how='all')  # drop empty columns
    df = df.dropna(axis=0, how='all')  # drop empty rows
    return df

def extract_pdf_tables(pdf_path):
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    df = clean_table(table)
                    all_tables.append(df)
    return all_tables

def parse_dataframes_to_json(dfs):
    results = []
    year_pattern = re.compile(r"\b(20\d{2})\b")
    for df in dfs:
        headers = [str(c) if c else "" for c in df.columns]
        header_text = " ".join(headers)
        match = year_pattern.search(header_text)
        year = int(match.group(1)) if match else None
        data = {}
        for pollutant in df.columns[1:]:
            values = df.set_index(df.columns[0])[pollutant].to_dict()
            clean_values = {}
            for k, v in values.items():
                if not isinstance(k, str):
                    continue
                k = k.strip().upper()
                try:
                    clean_values[k] = float(v)
                except:
                    clean_values[k] = v
            data[str(pollutant)] = clean_values
        results.append({
            "year": year,
            "location": str(df.columns[0]).strip(),
            "data": data
        })
    return results

if __name__ == "__main__":
    dfs = extract_pdf_tables(PDF_PATH)
    structured_json = parse_dataframes_to_json(dfs)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(structured_json, f, indent=2)
    print(f"✅ Extracted data written to {OUTPUT_JSON}")
