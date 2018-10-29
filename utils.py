import pandas as pd

# Fast date parser, source: https://github.com/sanand0/benchmarks/tree/master/date-parse
def parse_dates(s):
    """
    This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.
    """
    dates = {date:pd.to_datetime(date) for date in s.unique()}
    return s.map(dates)

# Simple heuristic to clean company name data
def clean(string):
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