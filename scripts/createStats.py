import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

def extract_authors_table(authors_soup):
    table = authors_soup.find("table")
    headers_raw = [th.get_text(strip=True) for th in table.find_all("th")]

    # Normalize and filter columns
    drop_cols = {"Age", "Active days", "First commit", "Last commit", '# by commits'}
    keep_indices = [i for i, h in enumerate(headers_raw) if h.strip() not in drop_cols]
    headers = [h for i, h in enumerate(headers_raw) if i in keep_indices]

    data = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) >= max(keep_indices) + 1:
            values = [cells[i].get_text(strip=True) for i in keep_indices]
            data.append(values)

    return pd.DataFrame(data, columns=headers)

def extract_total_lines(lines_soup):
    dt = lines_soup.find("dt", string=lambda s: s and s.strip() == "Total lines")
    dd = dt.find_next_sibling("dd") if dt else None
    total_lines = dd.get_text(strip=True) if dd else "N/A"
    return pd.DataFrame([{"Metric": "Total lines of code", "Value": total_lines}])

def generate_gitstats_excel(gitstats_dir: Path, output_excel: Path):
    authors_html = (gitstats_dir / "authors.html").read_text(encoding="utf-8")
    lines_html = (gitstats_dir / "lines.html").read_text(encoding="utf-8")

    authors_soup = BeautifulSoup(authors_html, "html.parser")
    lines_soup = BeautifulSoup(lines_html, "html.parser")

    # Remove unwanted sections from authors.html
    for heading_id in ["author_of_year", "commits_by_domains", "author_of_month"]:
        h2 = authors_soup.find("h2", id=heading_id)
        if h2:
            next_el = h2.find_next_sibling()
            h2.decompose()
            while next_el and not (next_el.name == "h2" and next_el.has_attr("id")):
                to_remove = next_el
                next_el = next_el.find_next_sibling()
                to_remove.decompose()

    # Extract the filtered tables
    authors_df = extract_authors_table(authors_soup)
    summary_df = extract_total_lines(lines_soup)

    # Export to Excel
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        authors_df.to_excel(writer, sheet_name="Authors", index=False, startrow=0)
        summary_df.to_excel(writer, sheet_name="Authors", index=False, startrow=len(authors_df) + 2)

    print("Files saved:")
    print("- gitstats_table.xlsx")

if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    generate_gitstats_excel(base, base / "gitstats_table.xlsx")
