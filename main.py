import yfinance as yf
import scipy.integrate as spi
import numpy as np
import math
import time # Used for sleep funfction to avoid getting blocked form yfinance

# Imports: Webscrapping modules might be inlcuded and not used
# Needs:
# Need to gather date of the option from the user and also the Ticker symbol to search

# Constants
TRADING_DAYS_ANNUAL = 252
VOLATILITY_RANGE = 100 # Range in days of the volatility that is calculated
DAYS_IN_A_YEAR = 365
PI = math.pi

# the function used in definite integral below
def f(x):
    return math.e ** (-x**2 / 2)

def cumulativeDistribution(input):
    firstTerm = 1 / math.sqrt(2*PI)
    result, error = spi.quad(f, -np.inf, input) # tupple acts as a static array fixed size
    return firstTerm * result

def theoreticalFairValue(stockName : str, exercise_price, optionDuration, call_option : bool):
    # The name of the ticker we are using the formula on ex: "AAPL"
    ticker_str = stockName

    time.sleep(1)
    # Get data for specific ticker that you're using for Stock option
    ticker = yf.Ticker(ticker_str)

    # get the risk-free interest rate
    # Use ^IRX(Short term) & ^TNX(Long term) - most stock option durations are low to medium
    time.sleep(1)
    #tickerIntrestRate = yf.Ticker("^IRX")

    # fetching the latest price
    current_price = ticker.fast_info['last_price']

    # get the risk-free interest rate
    # Use ^IRX(Short term) & ^TNX(Long term)
    tickerIntrestRate = yf.Ticker("^IRX")
    # getting annualized discount rate
    dailyRateAmount = tickerIntrestRate.fast_info['last_price'] 
    decimial_rate = dailyRateAmount / 100 # Turning into decimial

    # Calculating duration of the option as a decimal to be inserted into formula
    t = optionDuration / DAYS_IN_A_YEAR

    # getting the risk-free interest rate
    # log function is using ln(x)
    intrest_rate = math.log(1 + decimial_rate)

    # need to claculate log returns or (volatility)
    # would be an estimate of the volatility
    # prices range holds the stock prices in a 100 day range / sample size - this claculates the volatility
    # use closing price for each day
    sum = 0.0
    #prices_list = [100.0, 102.0, 101.0, 105.0] # prototype code line
    price_history = ticker.history(period = "200d") # gets the history of the ticker from 200d
    closing_prices = price_history['Close']         # gets the closing price of each day

    if len(closing_prices) < VOLATILITY_RANGE + 1:  # Disclaimer not enough data history
        print("Trading history is less than desired")

    # trim the prices ranges to only be VOLATILITY_RANGE + 1 elements
    prices_range = closing_prices.tail(VOLATILITY_RANGE + 1)

    prices_list = prices_range.astype(float).tolist() # convert to python list of type float
    log_returns = []

    # Iterate through the list, stopping before the last element to avoid out of bounds error
    # adds each element to log_returns
    for i, current_element in enumerate(prices_list[:-1]):
        next_element = prices_list[i + 1]
        log_return = math.log(next_element / current_element)
        log_returns.append(log_return)

    # Sum total of log_returns
    for amount in log_returns:
        sum += amount

    # get the mean of log_returns
    mean_log_return = sum / len(log_returns)

    summation_deviation = 0
    for amount in log_returns:
        summation_deviation += (amount - mean_log_return) ** 2 

    # getting the stardard deviation
    n = len(log_returns)
    standard_deviation = math.sqrt(summation_deviation / (n - 1))

    # Annualizing for Annual volatility(sigma) - this value is sigma in formula
    standard_deviation_annual = standard_deviation * math.sqrt(TRADING_DAYS_ANNUAL)

    # Probability function d1
    d1_numerator = math.log(current_price / exercise_price) + (intrest_rate + (standard_deviation_annual ** 2 / 2)) * t
    d1 = d1_numerator / (standard_deviation_annual * math.sqrt(t))

    # Probability function d2
    d2_numerator = math.log(current_price / exercise_price) + (intrest_rate - (standard_deviation_annual ** 2 / 2)) * t
    d2 = d2_numerator / (standard_deviation_annual * math.sqrt(t))

    # final formula for Black scholes:
    # Change calculation based on call option/put option
    if call_option:
        part1 = current_price*cumulativeDistribution(d1)
        part2 = exercise_price * math.e ** (-intrest_rate*t) * cumulativeDistribution(d2)
    else:
        part1 = exercise_price * math.e ** (-intrest_rate*t) * cumulativeDistribution(-d2)
        part2 = current_price * cumulativeDistribution(-d1)

    result = part1 - part2
    return result


def quickTheoreticalFairValue(tickerIR: str, stock_price, volatility, exercise_price, optionDuration, call_option : bool):
    # This func avoids multiple fetches of dataframes from yahoo finance
    # Passes in paramters are the ticker objects from yahoo finance
    # We already have the stock price as paramater & viotility

    # fetching the latest price
    current_price = stock_price

    # get the risk-free interest rate
    # Use ^IRX(Short term) & ^TNX(Long term)
    # getting annualized discount rate
    dailyRateAmount = tickerIR.fast_info['last_price'] 
    decimial_rate = dailyRateAmount / 100 # Turning into decimial

    # getting the risk-free interest rate
    # log function is using ln(x)
    intrest_rate = math.log(1 + decimial_rate)

    # Calculating duration of the option as a decimal to be inserted into formula
    t = optionDuration / DAYS_IN_A_YEAR
    # Annualizing for Annual volatility(sigma) - this value is sigma in formula
    standard_deviation_annual = volatility

    # Probability function d1
    d1_numerator = math.log(current_price / exercise_price) + (intrest_rate + (standard_deviation_annual ** 2 / 2)) * t
    d1 = d1_numerator / (standard_deviation_annual * math.sqrt(t))

    # Probability function d2
    d2_numerator = math.log(current_price / exercise_price) + (intrest_rate - (standard_deviation_annual ** 2 / 2)) * t
    d2 = d2_numerator / (standard_deviation_annual * math.sqrt(t))

    # final formula for Black scholes:
    # Change calculation based on call option/put option(true = call option)
    if call_option:
        part1 = current_price*cumulativeDistribution(d1)
        part2 = exercise_price * math.e ** (-intrest_rate*t) * cumulativeDistribution(d2)
    else:
        part1 = exercise_price * math.e ** (-intrest_rate*t) * cumulativeDistribution(-d2)
        part2 = current_price * cumulativeDistribution(-d1)

    result = part1 - part2
    return result


def validTicker(ticker: str) -> str:
    print(f"validTicker:{ticker}" )
    try:
        ticker = yf.Ticker(ticker.upper())
        data = ticker.history(period="3d")
        # returns true if valid false otherwise
        return not data.empty
    except Exception:
        return False
    
def getCurrentPrice(ticker: str) -> str:
    ticker = yf.Ticker(ticker.upper())
    current_price = ticker.fast_info['last_price']
    return current_price

  
#print(f"Stock option result: {result:.4f}")
#print(f"mean_log_return: {mean_log_return:.5f}")                      # mean_log_return = 0.01626
#print(f"standard_deviation: {standard_deviation:.4f}")                # standard_deviation = 0.0245
#print(f"standard_deviation_annual: {standard_deviation_annual:.4f}")  # standard_deviation_annual = 0.389
# Extra info
# You would select the strike price or at least tell the user at what strike price the program determing.

