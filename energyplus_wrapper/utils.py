import warnings

import bs4

import pandas as pd


def process_eplus_html_report(eplus_html_report):
    with open(eplus_html_report) as f:
        soup = bs4.BeautifulSoup(f.read(), features="lxml")
    for table in soup.find_all("table"):
        title = table.find_previous_sibling("b").get_text()
        yield title, pd.read_html(str(table), index_col=0, header=0)[0]


def process_eplus_time_series(working_dir):
    for csv_file in working_dir.files("*.csv"):
        name = csv_file.basename().stripext()
        if name != "eplus":
            name = name.replace("eplus-", "")
        try:
            time_serie = pd.read_csv(csv_file)
        except Exception:
            warnings.warn(
                f"Unable to parse csv file {csv_file}. Return raw string as fallback."
            )
            with open(csv_file) as f:
                time_serie = f.read()
        yield str(name), time_serie
