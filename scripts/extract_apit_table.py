"""Extract the official IRD APIT Tax Table No. 01 into a compact CSV fixture.

The IRD publishes Table 01 as a ~280 page PDF generated from Excel. Each row is
"income from - income to -> monthly tax", and the tax goes up by exactly Rs. 1 per
row. Text extraction occasionally glues neighbouring cells together, so we keep
only the reliable part (the upper income for each tax value) and rebuild the
lower bounds from it.

Usage:
    pdftotext -layout APIT_2526_Table_01.pdf table.txt
    python scripts/extract_apit_table.py table.txt tests/fixtures/apit_table01_2526.csv.gz
"""

import csv
import gzip
import re
import sys

# "low - high tax", sometimes with the dash lost...
ROW = re.compile(r"\b\d{6}\s*-?\s+(\d{6})\s+(\d{1,5})\b")
# ...or "- high tax" when a column's "low" was pushed onto the previous line.
ROW_NO_LOW = re.compile(r"-\s+(\d{6})\s+(\d{1,5})\b")


def extract(text: str) -> list[tuple[int, int, int]]:
    highest: dict[int, int] = {}
    for high, tax in ROW.findall(text) + ROW_NO_LOW.findall(text):
        tax, high = int(tax), int(high)
        highest[tax] = max(highest.get(tax, 0), high)

    taxes = sorted(highest)
    if taxes != list(range(1, len(taxes) + 1)):
        missing = sorted(set(range(1, taxes[-1] + 1)) - set(taxes))
        raise SystemExit(f"table is not contiguous; missing tax values: {missing[:10]}")

    first_low = int(re.search(r"up\s+to\s+(\d{6})", text).group(1)) + 1
    rows, low = [], first_low
    for tax in taxes:
        rows.append((low, highest[tax], tax))
        low = highest[tax] + 1
    return rows


def main() -> None:
    text_path, out_path = sys.argv[1], sys.argv[2]
    with open(text_path, encoding="utf-8") as fh:
        rows = extract(fh.read())
    with gzip.open(out_path, "wt", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["income_from", "income_to", "monthly_tax"])
        writer.writerows(rows)
    print(f"{len(rows)} rows: Rs. {rows[0][0]:,} - {rows[-1][1]:,} -> tax Rs. 1 - {rows[-1][2]:,}")


if __name__ == "__main__":
    main()
