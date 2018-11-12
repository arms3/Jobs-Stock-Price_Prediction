import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def correlation(ticker, emps, lag=0, smoothing=0):
    """Calculates the correlation between a stock ticker Series and a LinkedIn employment series.
    Returns the processed DataFrame and the calculated correlation.
    """

    last_ticker = ticker.dropna().tail(1).index.values[0]
    first_ticker = ticker.dropna().head(1).index.values[0]

    # Join data
    df = pd.concat([ticker, emps], axis=1)
    df.columns = ['close', 'emps']

    # Shift ticker
    df['unshifted_close'] = df['close']
    df['close'] = df.close.shift(lag)

    df = df.loc[first_ticker + pd.Timedelta(lag, unit='d'):last_ticker + pd.Timedelta(lag, unit='d')]

    # Interpolate ticker data
    df['close'] = df['close'].interpolate('linear')
    df = df.dropna()

    # Normalize ticker and employment data
    df = (df - df.mean()) / df.std()

    # Smoothing
    df = df.ewm(span=smoothing).mean()

    # Drop nans
    df = df.dropna()

    # Create correlation
    cor = df.close.corr(df.emps)

    return df, cor


def cross_correlation_plot(ticker, emps, srange=(-180, 180), smoothing=0, plot=True, resolution=1):
    """
    Calculates the cross correlation plot and optimal lags
    :param ticker: Stock ticker pandas.Series
    :param emps: LinkedIn employment pandas.Series
    :param srange: Tuple of timeshifts defining min and max
    :param smoothing: Span parameter for exponential weighted smoothing function
    :param plot: Bool, if True plots the cross correlation and dataframe
    :param resolution: Step in timeshift within range
    :return: Cleaned dataframe, location of optimal lag, correlation at optimal lag, list of calculated correlations
    """
    cors = []
    for shift in range(srange[0], srange[1], resolution):
        df, cor = correlation(ticker, emps, shift, smoothing)
        if len(df) < 100:
            cors.append(np.nan)  # Too few datapoints to correlate
        else:
            cors.append(cor)

    if np.isnan(cors).all():
        print("Can't calculate correlaction")
        return (None, None, None, None)

    max_cor = np.nanmax(cors)
    max_lag = range(srange[0], srange[1], resolution)[np.nanargmax(cors)]

    print('Max correlation at t=' + str(max_lag))
    print('Max correlation:' + str(max_cor))

    df, cor = correlation(ticker, emps, max_lag, smoothing=smoothing)

    if plot:
        fig, ax = plt.subplots(1, 2, figsize=(20, 5))
        plt.title(ticker.name)
        ax[0].plot(range(srange[0], srange[1], resolution), cors, marker='.', linestyle='None', alpha=0.5)
        df.plot(ax=ax[1])
        ax[0].set_xlabel('Time shift of series (Negative is LinkedIn employee count leading stock price)')
        ax[0].set_ylabel('Series Cross Correlation')
        ax[1].set_ylabel('Normalized price / employee count')

    return df, max_lag, max_cor, cors


def correlation_w_diff(ticker, emps, lag=0, smoothing=0, diff=True):
    """Calculates the correlation between a stock ticker Series and a LinkedIn employment series.
    Returns the processed DataFrame and the calculated correlation.
    """

    last_ticker = ticker.dropna().tail(1).index.values[0]
    first_ticker = ticker.dropna().head(1).index.values[0]

    # Join data
    df = pd.concat([ticker, emps], axis=1)
    df.columns = ['close', 'emps']

    # Shift ticker
    df['unshifted_close'] = df['close']
    df['close'] = df.close.shift(lag)

    # Slice for contingent timeranges
    df = df.loc[first_ticker + pd.Timedelta(lag, unit='d'):last_ticker + pd.Timedelta(lag, unit='d')]

    # Normalize by column
    df = (df - df.mean()) / df.std()

    # Interpolate
    df = df.interpolate()
    df = df.dropna()

    # Detrend data
    # dftrend = df.ewm(span=180).mean()
    # df = df - dftrend
    if diff:
        df = df.diff()
        # Remove points more than 3 std deviations from mean
        filt = abs(df - df.mean()) > 3 * df.std()
        if (len(filt) != 0):
            df[filt] = np.nan

    # Create correlation
    cor = df.close.corr(df.emps)

    return df, cor


def cross_correlation_plot_w_diff(ticker, emps, srange=(-180, 180), smoothing=0, plot=True, resolution=1, diff=True):
    """
    Calculates the cross correlation plot and optimal lags
    :param ticker: Stock ticker pandas.Series
    :param emps: LinkedIn employment pandas.Series
    :param srange: Tuple of timeshifts defining min and max
    :param smoothing: Span parameter for exponential weighted smoothing function
    :param plot: Bool, if True plots the cross correlation and dataframe
    :param resolution: Step in timeshift within range
    :return: Cleaned dataframe, location of optimal lag, correlation at optimal lag, list of calculated correlations
    """
    cors = []
    for shift in range(srange[0], srange[1], resolution):
        df, cor = correlation_w_diff(ticker, emps, shift, smoothing)
        if len(df) < 100:
            cors.append(np.nan)  # Too few datapoints to correlate
        else:
            cors.append(cor)

    if np.isnan(cors).all():
        print("Can't calculate correlaction")
        return (None, None, None, None)

    # Investigate positive and negative correlation
    #     max_cor = np.nanmax(np.abs(cors))
    max_lag = range(srange[0], srange[1], resolution)[np.nanargmax(np.abs(cors))]
    max_cor = cors[np.nanargmax(np.abs(cors))]

    print('Max correlation at t=' + str(max_lag))
    print('Max correlation:' + str(max_cor))

    df, cor = correlation_w_diff(ticker, emps, max_lag, smoothing=smoothing, diff=diff)

    if plot:
        fig, ax = plt.subplots(1, 2, figsize=(20, 5))
        plt.title(ticker.name)
        ax[0].plot(range(srange[0], srange[1], resolution), cors, marker='.', linestyle='None', alpha=0.5)
        df.plot(ax=ax[1])
        ax[0].set_xlabel('Time shift of series (Negative is LinkedIn employee count leading stock price)')
        ax[0].set_ylabel('Series Cross Correlation')
        ax[1].set_ylabel('Normalized price / employee count')

    return df, max_lag, max_cor, cors