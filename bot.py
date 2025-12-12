import pandas as pd

COLUMN_MAP = {
    "Торговое название и синоним": "commercial_name",
    "Международное название": "international_name",
    "Лекарственная форма выпуска": "form",
    "Страна-производитель": "country",
    "Фирма производитель": "manufacturer",
    "Фармакотерапевтическая группа": "group",
    "Код АТХ": "atc_code",
    "№ Регистрационного удостоверения": "reg_number",
    "Дата регистрации и перерегис-трации": "date_registration",
    "Дата изменения к регистрационному удостоверению": "date_modified",
    "Условия отпуска": "prescription_rule",
}

def load_db(path):
    df = pd.read_csv(path)

    # Remove completely empty columns (from leading commas)
    df = df.dropna(axis=1, how="all")

    # Rename known columns
    df = df.rename(columns={c: COLUMN_MAP[c] for c in df.columns if c in COLUMN_MAP})

    # Normalize commercial name
    df["commercial_name"] = (
        df["commercial_name"]
        .astype(str)
        .str.lower()
        .str.replace("®", "", regex=False)
        .str.replace("™", "", regex=False)
        .str.replace("\r", " ", regex=False)   # replace CR with space
        .str.replace("\n", " ", regex=False)   # replace LF with space
        .str.strip()
    )


    return df

def search_drug(query: str):
    q = query.lower().strip()

    for label, df in [
        ("Uzbek database", uzbek),
        ("Russian database", russian),
        ("International database", international),
    ]:
        match = df[df["commercial_name"].str.contains(q, regex=False)]
        if not match.empty:
            return label, match.iloc[0]

    return None, None

def format_drug_info(source_name, row):
    def safe(field):
        return row[field] if field in row and pd.notna(row[field]) else "—"

    return (
        f"Found in: {source_name}\n"
        f"Commercial name: {safe('commercial_name')}\n"
        f"International name: {safe('international_name')}\n"
        f"Form: {safe('form')}\n"
        f"Country: {safe('country')}\n"
        f"ATC: {safe('atc_code')}\n"
        f"Manufacturer: {safe('manufacturer')}\n"
        f"Prescription rule: {safe('prescription_rule')}\n"
        f"Registration number: {safe('reg_number')}\n"
        f"Registered on: {safe('date_registration')}\n"
        f"Modified on: {safe('date_modified')}\n"
    )

# ---------------------------------------------------------
# Load the data
# ---------------------------------------------------------

uzbek = load_db("data/uzbek.csv")
russian = load_db("data/russian.csv")
international = load_db("data/international.csv")

# ---------------------------------------------------------
# Test in terminal
# ---------------------------------------------------------

if __name__ == "__main__":
    while True:
        q = input("Enter drug name (or 'quit'): ")
        if q == "quit":
            break

        source, row = search_drug(q)
        if row is None:
            print("Not found. Check spelling or it is not registered.\n")
        else:
            print(format_drug_info(source, row))
            print()
