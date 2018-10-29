import pandas as pd
from pathlib import Path


def parse_dates(s):
    """
    Fast date parser, source: https://github.com/sanand0/benchmarks/tree/master/date-parse
    This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.
    """
    dates = {date:pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)


def clean(string):
    # Simple heuristic to clean company name data
    str_ = string.replace('Inc','')
    str_ = str_.lower()
    str_ = str_.replace('.com','')
    str_ = str_.replace('.','')
    str_ = str_.replace(',','')
    str_ = str_.replace('®','')
    str_ = str_.replace("'",'')
    str_ = str_.replace('corporation','')
    str_ = str_.replace('group','')
    str_ = str_.replace('  ',' ')
    str_ = str_.replace('-','')
    str_ = str_.strip()
    return str_


def clean_name(series):
    names = {name: clean(name) for name in series.unique()}
    return series.map(names)


def parse_currency(x):
    if type(x) == float or type(x) == int:
        return x
    else: x = x.replace('$','')
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0


def data_load(PATH):
    PATH = Path(PATH) #make sure we're dealing with a pathlib object

    link = pd.read_csv(PATH / 'temp_datalab_records_linkedin_company.csv',
                       parse_dates=['as_of_date', 'date_added', 'date_updated'],
                       index_col='as_of_date')

    companies = pd.read_csv(PATH / 'extracted_correlations_all.csv')

    # Data source: https://www.quandl.com/databases/WIKIP
    stocks = pd.read_csv(PATH / 'WIKI_PRICES.csv')

    # Fast clean dates
    stocks['date'] = parse_dates(stocks.date)
    stocks = stocks.set_index('date')

    # Select on the adjusted close column
    stocks = stocks[['ticker', 'adj_close']].pivot(columns='ticker')
    stocks.columns = stocks.columns.droplevel(0)

    return link, companies, stocks
