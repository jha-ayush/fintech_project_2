# import libraries - yfinance, prophet, streamlit, plotly
import streamlit as st
from streamlit_lottie import st_lottie
from datetime import datetime
# import yfinance for stock data
import yfinance as yf
#import prophet libraries
from prophet import Prophet
from prophet.plot import plot_plotly
#import plotly for interactive graphs
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
# import cufflinks for bollinger bands
import cufflinks as cf
from datetime import timedelta

import pandas_datareader as pdr

from sklearn.decomposition import PCA # PCA for dimensionality reduction
from sklearn.cluster import KMeans # KMeans for clustering

from yellowbrick.cluster import KElbowVisualizer
import seaborn as sns

from sklearn.preprocessing import StandardScaler # Scaling data
from sklearn.preprocessing import MinMaxScaler # MinMax scaler
from sklearn.metrics import silhouette_score # To evaluate the clustering
from sklearn.metrics import calinski_harabasz_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import adjusted_mutual_info_score
from sklearn.utils import resample

from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from pandas.tseries.offsets import DateOffset
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.kernel_approximation import RBFSampler
from sklearn.svm import SVR
from sklearn import preprocessing
from sklearn import utils
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

from sklearn import datasets
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt
import logging
import os

# Import warnings + watermark
from watermark import watermark
from warnings import filterwarnings
filterwarnings("ignore")
print(watermark())
print(watermark(iversions=True, globals_=globals()))


#______________________________________________________#

# Set page configurations - ALWAYS at the top
st.set_page_config(page_title="Stocks analysis",page_icon="📈",layout="centered",initial_sidebar_state="auto")


# Add cache to store ticker values after first time download in browser
@st.cache(suppress_st_warning=True)

# functions

# Create a function to access the json data of the Lottie animation using requests - if successful return 200 - data is good, show animation else return none
def load_lottieurl(url):
    """
    Loads the json data for a Lottie animation using the given URL.
    Returns None if there was an error.
    """
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
#load lottie asset
lottie_coding=load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_vktpsg4v.json")

# Use local style.css file
def local_css(file_name):
    """
    Use a local style.css file.
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# load css file
local_css("./style/style.css")

#-----------------------------------------------#

# wrap header content in a streamlit container
with st.container():
        # 2 columns section:
        col1, col2 = st.columns([3, 2])
        with col1:           
            # Load title/info
            st.title(f"Equity portfolio analyzer")
            st.markdown(f"Our app utilizes advanced algorithms to analyze and predict the performance of your portfolio, providing valuable insights and recommendations to help optimize your investments.",unsafe_allow_html=True)
        with col2:
            # Load asset(s)
            st_lottie(lottie_coding,height=150,key="finance")   
                 
#------------------------------------------------------------------#

# Read ticker symbols from a CSV file
try:
    tickers = pd.read_csv("./Resources/tickers.csv")
except:
    logging.error('Cannot find the CSV file')

# Benchmark ticker - S&P Global index '^GSPC'
benchmark_ticker=yf.Ticker("^GSPC")

# Display a selectbox for the user to choose a ticker
ticker = st.sidebar.selectbox("Select a ticker from the dropdown menu",tickers)

# Get data for the selected ticker
ticker_data = yf.Ticker(ticker)

#------------------------------------------------------------------#    
            

# add start/end dates
end_date=value=pd.to_datetime("today")
# calculate start date as 20 years before end date
start_date = end_date - pd.DateOffset(years=25)

# Create a new dataframe - add historical trading period for 1 day
ticker_df=ticker_data.history(period="1d",start=start_date,end=end_date)

# query S&P index historical prices
benchmark_ticker=benchmark_ticker.history(period="1d",start=start_date,end=end_date)

# print(ticker_df.head())
####
#st.write('---')
# st.write(ticker_data.info)

# Load stock data - define functions
def load_data(ticker,start_date,end_date):
    data=yf.download(ticker,start_date,end_date)
    # convert the index to a datetime format
    data.index = pd.to_datetime(data.index)
    # use the .rename() function to rename the index to 'Date'
    data = data.rename_axis('Date')
    return data

# data load complete message
data_load_state=st.sidebar.text("Loading data...⌛")  
data=load_data(ticker,start_date,end_date)
data_load_state.text("Past 25 years data loaded ✅")

#------------------------------------------------------#
# Create Navbar tabs
st.write("###")
tab1, tab2, tab3, tab4= st.tabs(["Fin ratios", "Unsupervised", "Supervised", "Recommendations"])

with tab1:
    st.write(f"Select different boxes to view of an individual ticker over the selected period of time.",unsafe_allow_html=True)
    st.subheader(f"Ticker info & financial ratios")
    #---------------------------------------------#
    # Display company info
    if st.checkbox(label=f"Display {ticker} company info"):
        ticker_data = yf.Ticker(ticker).info

        # Check if logo URL is available and display
        logo_url = ticker_data.get('logo_url')
        if logo_url:
            st.markdown(f"<img src={logo_url}>", unsafe_allow_html=True)
        else:
            st.warning("Logo image is missing.")

        # Check if company name is available and display
        st.write("###")
        company_name = ticker_data.get('longName')
        if company_name:
            st.markdown(f"<b>Company Name:</b> {company_name}", unsafe_allow_html=True)
        else:
            st.warning("Company name is missing.")

        # Check if quoteType is available and display
        quoteType = ticker_data.get('quoteType')
        if quoteType:
            st.markdown(f"<b>Quote type:</b> {quoteType}", unsafe_allow_html=True)
        else:
            st.warning("Quote type is missing.")        

        # Check if sector is available and display
        sector = ticker_data.get('sector')
        if sector:
            st.markdown(f"<b>Sector:</b> {sector}", unsafe_allow_html=True)
        else:
            st.warning("Sector is missing.")

        # Check if industry is available and display
        industry = ticker_data.get('industry')
        if industry:
            st.markdown(f"<b>Industry:</b> {industry}", unsafe_allow_html=True)
        else:
            st.warning("Industry is missing.")        

        # Check if location is available and display
        city = ticker_data.get('city')
        country = ticker_data.get('country')
        if city and country:
            st.markdown(f"<b>Location:</b> {city}, {country}", unsafe_allow_html=True)
        else:
            st.warning("Location is missing.")

        # Check if website is available and display
        website = ticker_data.get('website')
        if website:
            st.markdown(f"<b>Company Website:</b> {website}", unsafe_allow_html=True)
        else:
            st.warning("Website is missing.")

        # Check if Business summary is available and display
        summary = ticker_data.get('longBusinessSummary')
        if summary:
            st.info(f"{summary}")
        else:
            st.warning("Business summary is missing.")
        #---------------------------------------------#
        
    # Display data table
    raw_data_check_box=st.checkbox(label=f"Display {ticker} raw dataset")
    if raw_data_check_box:
        st.subheader(f"{ticker} raw data")
        st.write(data)        

    # Display charts
    charts_check_box=st.checkbox(label=f"Display {ticker} charts")
    if charts_check_box:
        # Bollinger bands - trendlines plotted between two standard deviations
        st.header(f"{ticker} Bollinger bands")
        st.info("Bollinger Bands are a technical analysis tool that measures volatility of a financial instrument by plotting three lines: a simple moving average and two standard deviation lines (upper and lower bands). They are used to identify possible overbought or oversold conditions in the market, trend changes and potential buy and sell signals. The upper band is plotted as the moving average plus two standard deviations and lower band is plotted as moving average minus two standard deviations. They should be used in conjunction with other analysis methods for a complete market analysis and not as a standalone method.")
        # Reset index back to original
        data.reset_index(inplace=True)
        # Add description for visualization
        qf=cf.QuantFig(ticker_df,title='Bollinger Quant Figure',legend='top',name='GS')
        qf.add_bollinger_bands()
        fig = qf.iplot(asFigure=True)
        st.plotly_chart(fig)


        # Plot Open vs Close price data
        def plot_raw_data():
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=data["Date"],y=data["Open"],name="stock_open"))
            fig.add_trace(go.Scatter(x=data["Date"],y=data["Close"],name="stock_close"))
            fig.layout.update(title_text=(f"{ticker} raw data plot - Open vs Close price"),xaxis_rangeslider_visible=True)
            st.plotly_chart(fig)
        plot_raw_data()

        # create a streamlit linechart for ticker Volume over time
        st.subheader(f"{ticker} trading volume over time")
        st.line_chart(ticker_df.Volume)

# ----------------------------------------------------------------- #
    # Functions - Financial Ratios

    # Returns
    def calculate_returns(ticker, start_date, end_date):
        """
        Calculate the daily returns for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        pandas.DataFrame: The dataframe having close, returns, and daily returns for the stock in the specified range of time.
        """
        # Download the stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)

        # Adding new columns for returns and daily returns
        stock_data['returns'] = 0.0
        stock_data['daily_returns'] = 0.0

        #Calculating the returns for each day
        stock_data['returns'] = (stock_data['Adj Close'] - stock_data['Adj Close'].shift(1)) / stock_data['Adj Close'].shift(1)
        stock_data['returns'] = stock_data['returns']*100

        #Calculating the daily returns for each day
        stock_data['daily_returns'] = stock_data['Adj Close'].pct_change()
        stock_data['daily_returns'] = stock_data['daily_returns']*100

        return stock_data.dropna()

    # Daily Returns
    def calculate_daily_returns(ticker, start_date, end_date):
        """
        Calculate the daily returns for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        pandas.Series: The daily returns.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate daily returns
        daily_returns = data['Adj Close'].pct_change()

        return daily_returns.dropna()

    # Mean
    def calculate_mean(ticker, start_date, end_date):
        """
        Calculate the mean of returns for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The mean of returns.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate returns
        returns = data['Adj Close'].pct_change()

        # Calculate mean of returns
        mean = np.mean(returns)

        return mean

    # Std Deviation
    def calculate_std_deviation(ticker, start_date, end_date):
        """
        Calculate the standard deviation of returns for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The standard deviation of returns.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate returns
        returns = data['Adj Close'].pct_change()

        # Calculate standard deviation of returns
        std = np.std(returns)

        return std

    # Variance
    def calculate_variance_returns(ticker, start_date, end_date):
        """
        Calculate the variance of returns for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The variance of returns.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate returns
        returns = data['Adj Close'].pct_change()

        # Calculate variance of returns
        variance = np.var(returns)

        return variance

    # Co-variance
    def calculate_covariance_returns(ticker, benchmark_ticker, start_date, end_date, split_ratio = 0.8):
        """
        Calculate the covariance of returns for two given stock tickers.
        Here we are using ^GSPC as the benchmark ticker.

        Parameters:
        ticker (str): The ticker symbol for the first stock.
        benchmark_ticker (str): The S&P Global symbol for the benchmark index.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        split_ratio (float): The ratio of the data to be used for training (default = 0.8)

        Returns:
        float: The covariance of returns.
        """

        print("1")
        print(benchmark_ticker)
        print("2")
        # Get stock data
        data1 = yf.download(ticker, start=start_date, end=end_date)
        print(f"DATA1: {data1}")
        print("3")
        data2 = yf.download(benchmark_ticker, start=start_date, end=end_date)
        print("4")
        print("5")

        # split data into training and testing sets
        split_point = int(split_ratio * len(data1))
        train_data1, test_data1 = data1[:split_point], data1[split_point:]
        train_data2, test_data2 = data2[:split_point], data2[split_point:]

        # Calculate returns for training data
        train_returns1 = train_data1['Adj Close'].pct_change()
        train_returns2 = train_data2['Adj Close'].pct_change()

        # Calculate covariance of returns
        covariance = np.cov(train_returns1, train_returns2)[0][1]

        return covariance

    # Alpha ratio
    def calculate_alpha_ratio(ticker, benchmark_ticker, start_date, end_date):
        """
        Calculate the alpha ratio for a given stock ticker.
        Here we are using ^GSPC as the benchmark ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        benchmark_ticker (str): The S&P Global symbol for the benchmark index.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The alpha ratio.
        """

        # Get stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        benchmark_data = yf.download(benchmark_ticker, start=start_date, end=end_date)

        # Calculate returns
        stock_returns = stock_data['Adj Close'].pct_change()
        benchmark_returns = benchmark_data['Adj Close'].pct_change()

        # Calculate alpha
        alpha = np.mean(stock_returns) - np.mean(benchmark_returns)

        # Calculate standard deviation of returns
        std = np.std(stock_returns)

        # Calculate alpha ratio
        alpha_ratio = alpha / std

        return alpha_ratio.dropna()

    # Beta Ratio
    def calculate_beta_ratio(ticker, benchmark_ticker, start_date, end_date):
        """
        Calculate the beta ratio for a given stock ticker.
        Here we are using ^GSPC as the benchmark ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        benchmark_ticker (str): The ticker symbol for the benchmark index.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The beta ratio.
        """

        # Get stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        benchmark_data = yf.download(benchmark_ticker, start=start_date, end=end_date)

        # Calculate returns
        stock_returns = stock_data['Adj Close'].pct_change()
        benchmark_returns = benchmark_data['Adj Close'].pct_change()

        # Calculate beta
        cov = np.cov(stock_returns, benchmark_returns)[0][1]
        var = np.var(benchmark_returns)
        beta = cov / var

        # Calculate standard deviation of returns
        std = np.std(stock_returns)

        # Calculate beta ratio
        beta_ratio = beta / std

        return beta_ratio.dropna()

    # Omega Ratio
    def calculate_omega_ratio(ticker, start_date, end_date, threshold=0):
        """
        Calculate the omega ratio for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        threshold (float): The threshold for calculating excess return and downside risk. Default is 0.

        Returns:
        float: The omega ratio.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate daily returns
        returns = data['Adj Close'].pct_change()

        # Calculate excess return over threshold
        excess_return = returns[returns > threshold].mean()

        # Calculate downside risk below threshold
        downside_risk = abs(returns[returns < threshold]).mean()

        # Calculate omega ratio
        omega_ratio = excess_return / downside_risk

        return omega_ratio

    # Sharpe Ratio
    def calculate_sharpe_ratio(ticker, start_date, end_date, risk_free_rate=0.03):
        """
        Calculate the Sharpe ratio for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        risk_free_rate (float): The risk-free rate of return. Default is 0.

        Returns:
        float: The Sharpe ratio.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate daily returns
        returns = data['Adj Close'].pct_change()

        # Calculate excess return over risk-free rate
        excess_return = returns - risk_free_rate

        # Calculate Sharpe ratio
        sharpe_ratio = excess_return.mean() / np.std(returns)

        return sharpe_ratio

    # Calmar Ratio
    def calculate_calmar_ratio(ticker, start_date, end_date):
        """
        Calculate the Calmar ratio for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
        float: The Calmar ratio.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate daily returns
        returns = data['Adj Close'].pct_change()

        # Calculate annualized compounded return
        compounded_return = (1 + returns).prod() ** (252 / len(returns)) - 1

        # Calculate maximum drawdown
        max_drawdown = (data['Adj Close'] / data['Adj Close'].cummax() - 1).min()

        # Calculate Calmar ratio
        calmar_ratio = compounded_return / max_drawdown

        return calmar_ratio

    # Sortino Ratio
    def calculate_sortino_ratio(ticker, start_date, end_date, threshold=0):
        """
        Calculate the Sortino ratio for a given stock ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        threshold (float): The threshold for calculating downside risk. Default is 0.

        Returns:
        float: The Sortino ratio.
        """

        # Get stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Calculate daily returns
        returns = data['Adj Close'].pct_change()

        # Calculate downside risk below threshold
        downside_risk = np.sqrt(np.square(returns[returns < threshold]).mean())

        # Calculate Sortino ratio
        sortino_ratio = returns.mean() / downside_risk

        return sortino_ratio

    def calculate_treynor_ratio(ticker, start_date, end_date, benchmark_ticker, risk_free_rate=0.03):
        """
        Calculate the Treynor ratio for a given stock ticker.
        Here we are using ^GSPC as the benchmark ticker.

        Parameters:
        ticker (str): The ticker symbol for the stock.
        ^GSPC (str): The ticker symbol for the S&P 500 index.
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        risk_free_rate (float): The risk-free rate of return. Default is 0.

        Returns:
        float: The Treynor ratio.
        """

        # Get stock & benchmark data
        stock_data = yf.download(ticker, start_date, end_date)
        benchmark_data = yf.download(benchmark_ticker, start=start_date, end=end_date)

        # Calculate the stock's beta against the benchmark
        covariance = np.cov(stock_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance

        # Calculate the stock's excess return over the benchmark
        benchmark_return = benchmark_returns.mean()
        excess_return = stock_returns.mean() - benchmark_return

        # Calculate the Treynor ratio
        treynor_ratio = excess_return / beta

        return treynor_ratio



    # ----------------------------------------------------------------- #


    # Choose a financial ratio from dropdown menu 

    fin_ratios_check_box=st.checkbox(label=f"Display {ticker} related financial ratios")
    if fin_ratios_check_box:
        with st.container():
                # 2 columns section:
                col1, col2 = st.columns([6, 1])
                with col1:           
                    st.write("###") 
                    ratio_choice = st.selectbox("Choose from one of the financial ratios below",("Returns","Daily returns","Mean","Std-deviation","Variance","Co-variance","Alpha ratio","Beta ratio","Omega ratio","Sharpe ratio","Calmar ratio","Sortino ratio","Treynor ratio"),label_visibility="visible")

                    if ratio_choice == "Returns":
                        st.info("Returns is a measure of gain or loss on an investment over a certain period of time, usually expressed as a percentage of the initial investment. A positive return indicates a profit, while a negative return indicates a loss.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.write(calculate_returns(ticker, start_date, end_date))
                    elif ratio_choice == "Daily returns":
                        st.info("Daily returns calculates the percentage change in the adjusted closing price for each day, which gives the daily returns")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.write(calculate_daily_returns(ticker, start_date, end_date))
                    elif ratio_choice == "Mean":
                        st.info("Mean calcuates the arithmetic mean of the daily returns values")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Mean</b> value for <b>{ticker}</b> is: <b>{calculate_mean(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights the average price for the given time period.",unsafe_allow_html=True)
                    elif ratio_choice == "Std-deviation":
                        st.info("Std-dev is a statistical measure that shows how the data varies from the mean")                    
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Standard deviation</b> value for <b>{ticker}</b> is: <b>{calculate_std_deviation(ticker, start_date, end_date):0.4f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights the volatility of the ticker for the given time period.",unsafe_allow_html=True)
                    elif ratio_choice == "Variance":
                        st.info("Variance variance is a measure of the spread of the data around the mean to calculate risk. The larger the variance, the more spread out the data is, indicating a greater degree of volatility. A smaller variance value, on the other hand, indicates that the data is more tightly clustered around the mean and thus less volatile.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Variance</b> value for <b>{ticker}</b> is: <b>{calculate_variance_returns(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights volatility but only positive values.",unsafe_allow_html=True)
                    elif ratio_choice == "Co-variance":
                        st.info("Covariance is a measure of how two random variables are related and/or change together. A positive covariance indicates that the two variables are positively related, which means that as the value of one variable increases, the value of the other variable also tends to increase. A negative covariance indicates that the two variables are negatively related, which means that as the value of one variable increases, the value of the other variable tends to decrease. A covariance of zero indicates that there is no relationship between the two variables.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.write(calculate_covariance_returns(ticker, benchmark_ticker, start_date, end_date))
                        st.markdown(f"The value highlights how two tickers move in relation to each other",unsafe_allow_html=True)
                    elif ratio_choice == "Alpha ratio":
                        st.info("Alpha ratio is a measure of a stock's performance in relation to its benchmark. A positive alpha value indicates that the stock has performed better than the benchmark (^GSPC), while a negative alpha value indicates underperformance.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Alpha ratio</b> value for <b>{ticker}</b> is: <b>{calculate_alpha_ratio(ticker, benchmark_ticker, start_date, end_date)}</b>",unsafe_allow_html=True)
                        st.markdown(f"This highlights some of the following XYZ actions...",unsafe_allow_html=True)
                    elif ratio_choice == "Beta ratio":
                        st.info("Beta ratio is a measure of a stock's volatility in relation to its benchmark index. It compares the volatility of a stock to the volatility of a benchmark index (^GSPC), giving an idea of how much more or less volatile a stock is in relation to the benchmark index. A beta of 1 indicates that the stock's volatility is the same as the benchmark, while a beta greater than 1 indicates that the stock is more volatile than the benchmark, meaning its returns are more sensitive to market movements. Conversely, a beta less than 1 indicates that the stock is less volatile than the benchmark, meaning its returns are less sensitive to market movements.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Beta ratio</b> value for <b>{ticker}</b> is: <b>{calculate_beta_ratio(ticker, benchmark_ticker, start_date, end_date)}</b>",unsafe_allow_html=True)
                        st.markdown(f"This highlights some of the following XYZ actions...",unsafe_allow_html=True)
                    elif ratio_choice == "Omega ratio":
                        st.info("Omega ratio is a risk-adjusted performance measure that compares a stock's excess returns to its downside risk. The Omega ratio is similar to the Sharpe ratio, but it gives more weight to returns below a certain threshold, whereas the Sharpe ratio gives equal weight to all returns. A higher omega ratio indicates that the stock has a higher level of excess returns for a given level of downside risk.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Omega ratio</b> value for <b>{ticker}</b> is: <b>{calculate_omega_ratio(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights how well an investment strategy performs, taking into account both the potential returns and the potential risks of the strategy.",unsafe_allow_html=True)
                    elif ratio_choice == "Sharpe ratio":
                        st.info("Sharpe ratio is a measure of a stock's risk-adjusted performance, which compares the stock's excess returns to the volatility of its returns. A higher Sharpe ratio indicates that the stock has a higher level of excess returns for a given level of volatility, which means the stock is a better risk-adjusted performer.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Sharpe ratio</b> value for <b>{ticker}</b> is: <b>{calculate_sharpe_ratio(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights the measure of risk-adjusted performance that compares the excess return of an investment to its volatility.",unsafe_allow_html=True)
                    elif ratio_choice == "Calmar ratio":
                        st.info("Calmar ratio is a measure of a stock's risk-adjusted performance, which compares the stock's compound return to the maximum drawdown. A higher Calmar ratio indicates that the stock has a higher level of returns for a given level of drawdown, which means the stock is a better risk-adjusted performer.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Calmar ratio</b> value for <b>{ticker}</b> is: <b>{calculate_calmar_ratio(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights the profitability of a trading strategy.",unsafe_allow_html=True)
                    elif ratio_choice == "Sortino ratio":
                        st.info("Sortino ratio is a measure of a stock's risk-adjusted performance, which compares the stock's return to the downside risk. A higher Sortino ratio indicates that the stock has a higher level of return for a given level of downside risk, which means the stock is a better risk-adjusted performer.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True)
                        st.markdown(f"The <b>Sortino ratio</b> value for <b>{ticker}</b> is: <b>{calculate_sortino_ratio(ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"The value highlights the performance of trading strategies that are designed to minimize downside risk.",unsafe_allow_html=True)
                    elif ratio_choice == "Treynor ratio":
                        st.info("Treynor ratio is a measure of risk-adjusted return for a portfolio. Similar to the Sharpe ratio, which also measures risk-adjusted return, but the Treynor ratio uses beta as the measure of systematic risk, while the Sharpe ratio uses the standard deviation of returns. A higher Treynor ratio indicates that the portfolio has generated higher returns for the level of systematic risk taken on, as compared to a portfolio with a lower Treynor ratio.")
                        st.markdown(f"You've selected the following financial ratio - <b>{ratio_choice}</b>, for the ticker <b>{ticker}</b>, from the S&P Global index, between <b>{start_date}</b> and <b>{end_date}</b>.",unsafe_allow_html=True) 
                        st.markdown(f"The <b>Treynor ratio</b> value for <b>{ticker}</b> is: <b>{calculate_treynor_ratio(ticker, benchmark_ticker, start_date, end_date):0.5f}</b>",unsafe_allow_html=True)
                        st.markdown(f"This highlights some of the following XYZ actions...",unsafe_allow_html=True)
                    else:
                        st.empty()
                    
#----------------------------------------------------#
    # Time Series Forecasting with Facebook Prophet
    # Display Prophet section
    st.subheader("Time series forecast")
    prophet_check_box=st.checkbox(label=f"Display {ticker} Prophet time series forecast data")
    if prophet_check_box:
        with st.container():
                # 2 columns section:
                col1, col2 = st.columns([3, 2])
                with col1:           
                    # input a streamlit slider with years of prediction values
                    n_years=st.slider("Select year(s) for time series forecast",1,5)


                    # create a new dataframe from the ticker_df object
                    df_plot = pd.DataFrame.from_dict(ticker_df, orient='columns')

                    # select the 'Close' column
                    df_plot = df_plot[['Close']]

                    # rename the column to 'y'
                    df_plot.columns = ['y']

                    # add a 'ds' column with the dates, converting it to a datetime object and setting the timezone to None
                    df_plot['ds'] = pd.to_datetime(df_plot.index).tz_localize(None)

                    # Prophet requires a specific column format for the dataframe
                    df_plot = df_plot[['ds', 'y']]


                    # create the Prophet model and fit it to the data
                    model = Prophet(daily_seasonality=True)
                    model.fit(df_plot)

                    # create a dataframe with future dates
                    future_dates = model.make_future_dataframe(periods=365)

                    # make predictions for the future dates
                    forecast = model.predict(future_dates)

                    # select the relevant columns for the plot
                    plot_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

                    # Display data table
                    forecast_data_check_box=st.checkbox(label=f"Display {ticker} forecast data & price prediction")
                    if forecast_data_check_box:
                        st.subheader(f"{ticker} forecast dataset")
                        # Show tail of the Forecast data
                        st.write(forecast.tail())
                        st.write("---")

                        # create a plotly figure
                        fig = go.Figure()

                        # add the predicted values to the figure
                        fig.add_trace(go.Scatter(x=plot_df['ds'], y=plot_df['yhat'], name='Prediction'))

                        # add the uncertainty intervals to the figure
                        fig.add_shape(
                                type='rect',
                                xref='x',
                                yref='paper',
                                x0=plot_df['ds'].min(),
                                y0=0,
                                x1=plot_df['ds'].max(),
                                y1=1,
                                fillcolor='#E8E8E8',
                                layer='below',
                                line_width=0
                            )
                        fig.add_shape(
                                type='rect',
                                xref='x',
                                yref='y',
                                x0=plot_df['ds'].min(),
                                y0=plot_df['yhat_upper'],
                                x1=plot_df['ds'].max(),
                                y1=plot_df['yhat_lower'],
                                fillcolor='#E8E8E8',
                                layer='below',
                                line_width=0
                            )

                        # add the actual values to the figure
                        fig.add_trace(go.Scatter(x=df_plot['ds'], y=df_plot['y'], name='Actual'))

                        # set the plot's title and labels
                        fig.update_layout(
                            title=f"{ticker} stock price prediction",
                            xaxis_title='Date',
                            yaxis_title='Price (USD)'
                        )

                        # show the prediction plot
                        st.plotly_chart(fig)

                        # Display Prophet tools & components
                        forecast_component_check_box=st.checkbox(label=f"Display {ticker} Prophet forecast components")
                        if forecast_component_check_box:

                            # create a plotly figure for the model's components
                            st.subheader(f"{ticker} plot widget")
                            fig2 = plot_plotly(model, forecast)
                            # show the plot
                            st.plotly_chart(fig2)


                            # show the model's plots
                            st.subheader(f"{ticker} forecast components")
                            st.write(model.plot(forecast))

                            # show the model's plot_components
                            st.write(model.plot_components(forecast))
                                
#-----------------------------------------------#

    # Contact Form
    with st.container():
        st.write("---")
        st.subheader("Message us")
        st.write("##")

        # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
        contact_form = """
        <form action="https://formsubmit.co/jha.ayush85@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here" required></textarea>
            <button type="submit">Send</button>
        </form>
        """
    # Display form
    with st.container():    
        left_column, mid_column, right_column = st.columns(3)
        with left_column:
            st.markdown(contact_form, unsafe_allow_html=True)
            # Display balloons
            # st.balloons()
            # st.snow()
        with mid_column:
            st.empty()
        with right_column:
            st.empty()


#------------------------------------------------------------------#                      
# Tab 2 - Unsupervised Learning                    
with tab2:
    with st.container():
                # 2 columns section:
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Create a dataframe for symbols only
                    st.write("Ticker symbol dataframe")
                    symbols_df=tickers[['ticker']]
                    st.write(symbols_df)
                    
                    st.write(f"Let us view some datapoints and visualizations.",unsafe_allow_html=True)
                    
                    # Use ticker_df as the original dataframe
                    st.write(f"<b>Original dataframe</b>",unsafe_allow_html=True)
                    st.write(ticker_data)
                    st.write(ticker_df)
                    st.text(f"Original data loaded ✅")
                    
                    # fetch the historical prices data for the symbols
                    symbols_data = yf.download(ticker, start=start_date, end=end_date)

                    # fetch the Treasury bill rate data to calcuate rate_return
                    treasury_bill = pdr.get_data_fred('TB3MS')

                    # Use the assign function to add new columns and calculate their values
                    symbols_data = symbols_data.assign(mean=symbols_data['Adj Close'].mean(), std_dev=symbols_data['Adj Close'].std(), sharpe_ratio=(symbols_data['Close'].mean() - treasury_bill['TB3MS'].mean())/data['Adj Close'].std())
                    st.write(f"<b>Ticker info with metrics</b>",unsafe_allow_html=True)
                    st.write(symbols_data)

                    
                    # Cleanup ticker_df data - 'Dividends' & 'Stock Splits'. Store in a new dataframe called `df`
                    ticker_df.drop(columns=['Dividends', 'Stock Splits', 'Volume'], inplace=True)
                    st.write(f"<b>Cleaned dataframe</b>",unsafe_allow_html=True)
                    st.write(ticker_df)
                    st.text(f"Data Cleanup complete ✅")
                    
                    # Resample ticker data 'Daily' data - Drop Nan values
                    df_resampled = ticker_df.resample('M').mean().dropna()
                    st.write(f"<b>Monthly resampled dataframe</b>",unsafe_allow_html=True)
                    st.write(df_resampled)
                    st.text(f"Monthly data Resampled ✅")
                    
                    # Use metrics like Sharpe ratio to filter out tickers from specific value range
                    st.write(f"Sharpe ratio value is: <b>{calculate_sharpe_ratio(ticker, start_date, end_date, risk_free_rate=0.03)}</b>",unsafe_allow_html=True)
                    
                    # Scale Resampled data
                    scaler = StandardScaler()
                    df_scaled = scaler.fit_transform(df_resampled)
                    st.write(f"<b>Scaled dataframe</b>",unsafe_allow_html=True)
                    st.write(df_scaled)
                    st.text(f"Data Scaled ✅")
                    
                    # Apply PCA analysis
                    pca = PCA(n_components=2)
                    df_pca = pca.fit_transform(df_scaled)
                    st.write(f"<b>PCA dataframe</b>",unsafe_allow_html=True)
                    st.write(df_pca)
                    st.text(f"Applied PCA analysis ✅")
                    
                    
                    st.write("---")
                    st.write(f"View the 'shape' in tuple (row,column) format for each dataset as it goes through data trasformation.",unsafe_allow_html=True)
                    # Check the shape of the tickers dataframe from the csv
                    st.write(f"Original <b>tickers</b> dataset data shape: <b>{tickers.shape}</b>",unsafe_allow_html=True)
                    # Check the shape of the original dataframe from yfinance
                    st.write(f"Original <b>ticker_df</b> dataset data shape: <b>{ticker_df.shape}</b>",unsafe_allow_html=True)
                    # Check the shape of the resampled dataframe on ticker_df
                    st.write(f"Resampled <b>df_resampled</b> dataset data shape: <b>{df_resampled.shape}</b>",unsafe_allow_html=True)
                    # Check the shape of the resampled dataframe
                    st.write(f"Scaled <b>df_scaled</b> dataset data shape: <b>{df_scaled.shape}</b>",unsafe_allow_html=True)
                    # Check the shape of the PCA dataframe
                    st.write(f"PCA <b>df_pca</b> dataset data shape: <b>{df_pca.shape}</b>",unsafe_allow_html=True)
                    st.write("---")
                    
                    
                    # Apply K-means to the data
                    if st.button('Run K-means'):
                        # Create a slider to select the number of clusters
                        n_clusters = st.slider("Select number of clusters:", 2, 10, 3)

                        # Apply K-means
                        kmeans = KMeans(n_clusters=n_clusters)
                        kmeans.fit(df_pca)

                        # Get explained variance for PC1 and PC2
                        explained_variance = pca.explained_variance_ratio_

                        # Create an interactive visualization for the clusters
                        plt.scatter(df_pca[:, 0], df_pca[:, 1], c=kmeans.labels_, cmap='rainbow')
                        plt.title("K-Means scatter plot")
                        plt.xlabel(f"Principal Component 1 (Explained Variance: {explained_variance[0]:.2%})")  # x-label with explained variance
                        plt.ylabel(f"Principal Component 2 (Explained Variance: {explained_variance[1]:.2%})")  # y-label with explained variance
                        st.pyplot()

                        # Add Description
                        st.write(f"<b>Description of the scatter plot</b>",unsafe_allow_html=True)
                        st.write("The K-means scatter plot above shows the clusters obtained using K-means clustering with the number of clusters selected by the user. Each point represents a stock and is colored according to the cluster it belongs to. The x-axis represents the first principal component and the y-axis represents the second principal component.")
                        if hasattr(pca, 'explained_variance_ratio_'):
                            st.write("The x-label and y-label shows the percent of variance explained by each principal component.")
                        else:
                            st.write("The x-label and y-label shows the first and second principal component respectively.")
                    

                        # Get the cluster labels
                        # labels = kmeans.labels_ 
                        # st.write(labels)
                        
                        # Add the cluster labels as a new column in the original dataframe
                        # tickers['cluster'] = labels
                        # st.write(tickers)

                        # Heatmaps - use the indices of the PCA dataset to extract the corresponding rows of the original tickers dataset, and then use it to create the heatmap
                        # Create a new dataframe that contains the cluster labels and the PCA dataset
                        # df_pca_labels = pd.DataFrame(df_pca, columns=['PC1', 'PC2'])
                        # df_pca_labels['cluster'] = labels

                        # Create a heatmap
                        # fig = go.Figure(data=[go.Heatmap(z=df_pca_labels['cluster'], x=df_pca_labels['PC1'], y=df_pca_labels['PC2'], colorscale='Viridis')])
                        
                        # Add Description
                        # st.write(f"<b>Description of the heatmap plot</b>",unsafe_allow_html=True)
                        # st.write("The K-means heatmap shows the distribution of the clusters in the 2D space defined by the first two principal components (PC1 and PC2). The color of each point represents the cluster label assigned by the K-means algorithm, where darker colors represent higher densities of data points within a cluster.")

                    
                    # Find optimal number of clusters using the elbow method
                    # if st.button('Find optimal number of clusters'):
                    #     wcss = []
                    #     for i in range(2, 11):
                    #         kmeans = KMeans(n_clusters=i)
                    #         kmeans.fit(df_pca)
                    #         wcss.append(kmeans.inertia_)
                        # plt.plot(range(2, 11), wcss)
                        # plt.title('Elbow Method')
                        # plt.xlabel('Number of clusters')
                        # plt.ylabel('WCSS')
                        
                    # Plot Elbow method for cluster count optimization
                    if st.button('Determine optimum cluster count using the Elbow method'):
                        model = KMeans()
                        visualizer = KElbowVisualizer(model, k=(2,10))
                        visualizer.fit(df_pca)
                        visualizer.show()
                        st.pyplot()
                    
                        optimal_clusters = st.slider("Select the optimal number of clusters:", 2, 10, 4)
                        st.write(f"Optimum number of clusters: <b>{optimal_clusters}</b>",unsafe_allow_html=True)

                # Apply K-means to the data with optimal number of clusters
                if st.button('Re-run K-means with optimal number of clusters'):
                    kmeans = KMeans(n_clusters=optimal_clusters)
                    kmeans.fit(df_pca)

                    # Get explained variance for PC1 and PC2
                    explained_variance = pca.explained_variance_ratio_

                    # Visualize the clusters
                    plt.scatter(df_pca[:, 0], df_pca[:, 1], c=kmeans.labels_,cmap='rainbow')
                    plt.xlabel('PC1')
                    plt.ylabel('PC2')
                    plt.title(f'Explained variance (PC1, PC2): {explained_variance[0]:.2f}, {explained_variance[1]:.2f}')
                    st.pyplot()

                    # Add cluster labels to the original dataframe
                    ticker_df['cluster'] = kmeans.labels_
                    st.write(ticker_df)
                    st.text("K-means re-analysis complete ✅")
                    
                    # Apply Monte Carlo simulation with optimal number of clusters
                    if st.button('Run MC simulation for cluster optimization'):
                        # Create a slider to select the number of simulations
                        n_simulations = st.slider("Select the number of simulations:", 100, 1000, 500)
                        
                        for n_clusters in optimal_clusters:
                            simulation_results = []
                            kmeans = KMeans(n_clusters=n_clusters)
                            kmeans.fit(df_pca)
                            for i in range(n_simulations):
                                # Apply random normal perturbation to the PCA transformed data
                                df_pca_perturbed = df_pca + np.random.normal(0, 0.1, df_pca.shape)
                                kmeans_perturbed = KMeans(n_clusters=n_clusters)
                                kmeans_perturbed.fit(df_pca_perturbed)
                                # Append the perturbed cluster labels to the simulation results
                                simulation_results.append(kmeans_perturbed.labels_)

                            # Compute the probability of each ticker belonging to each cluster
                            ticker_cluster_prob = np.mean(np.array(simulation_results), axis=0)
                            ticker_cluster_prob = pd.DataFrame(ticker_cluster_prob, columns=['cluster_' + str(i) for i in range(n_clusters)], index=df_resampled.index)

                            # Display the tickers in each cluster
                            for i in range(n_clusters):
                                st.write(f"<b>Tickers in cluster {i}</b>", unsafe_allow_html=True)
                                st.write(ticker_cluster_prob[ticker_cluster_prob['cluster_' + str(i)] > 0.5].index)
                                st.write(ticker_cluster_prob)
                                st.text(f"Monte Carlo simulation with {n_clusters} clusters complete ✅")
                    
                    # Visualize the ticker-cluster probability data as a heatmap
                    if st.button('Visualize ticker-cluster probability data'):
                        plt.figure(figsize=(10, 8))
                        sns.heatmap(ticker_cluster_prob, cmap='YlGnBu')
                        plt.xlabel("Clusters")
                        plt.ylabel("Tickers")
                        plt.title("Probability of each ticker belonging to each cluster")
                        st.pyplot()
                        
                        
                    # Save the ticker-cluster probability data to a CSV file
                    if st.button('Save ticker-cluster probability data to CSV'):
                        file_name = "ticker_cluster_probability.csv"
                        ticker_cluster_prob.to_csv(file_name)
                        st.write(f"Ticker-cluster probability data saved to {file_name}")
                    
                    # Display the tickers in each cluster
                    
                    # Show in a table

                    # Ability to Save cluster tickers
                    
                    
                with col2:
                    st.empty()

                # Save the results to a file or a database
                if st.button("Save Results"):
                    export_file = st.file_uploader("Choose a CSV file", type=["csv"])
                    if export_file is not None:
                        with open(export_file, "w") as f:
                            writer = csv.writer(f)
                            writer.writerows(clusters)
                            st.balloons("File exported successfully")
                                                                       

#-------------------------------------------------------------------#

# Tab 3 - Supervised Learning
with tab3:
    stock_df=pd.DataFrame(data)
    #st.write(stock_df)   
    weekly_data=stock_df.resample('W').last()
    # st.write(f"Show weekly data")
    # st.write(weekly_data)
    signals_df = weekly_data.loc[:, ["Open","High","Low","Volume","Close","Adj Close"]]
    signals_df["Actual Returns"] = signals_df["Close"].pct_change()
    signals_df = signals_df.dropna()
    st.write(f"Show Actual returns of the signal data")
    st.write(signals_df)

    X = signals_df[["Open","High","Low","Volume","Adj Close"]]
    y = signals_df['Close']
    
    rf_mean = 0
    knn_mean = 0
    svm_mean = 0
    rf_r2 = 0
    knn_r2 = 0
    svm_r2 = 0

    #Random Foresh Regressor
    def random_forest(X,y):
        global rf_mean
        global rf_r2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        regressor = RandomForestRegressor()
        regressor.fit(X_train, y_train)
        y_pred = regressor.predict(X_test)
        rf_mean=mean_squared_error(y_test, y_pred)
        rf_r2=r2_score(y_test, y_pred)
        return y_pred

    #KNN 
    def KNN(X,y):
        global knn_mean
        global knn_r2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        knn = KNeighborsRegressor(n_neighbors=2)
        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_test)
        knn_mean=mean_squared_error(y_test, y_pred)
        knn_r2=r2_score(y_test, y_pred)
        return y_pred

    #SVM
    def SVM(X,y):    
        global svm_mean
        global svm_r2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        svr = SVR(kernel='linear', gamma=0.1)
        svr.fit(X_train, y_train)
        y_pred = svr.predict(X_test)
        svm_mean=mean_squared_error(y_test, y_pred)
        svm_r2=r2_score(y_test, y_pred)
        return y_pred  

    def best_accuracy_model(rf_mean, knn_mean, svm_mean):
        mean = [rf_mean, knn_mean, svm_mean]
        Best_Model = min(mean)
        return Best_Model


    if __name__ =="__main__":
        model = st.selectbox("Choose from one of the models below",("random_forest","KNN","SVM"),label_visibility="visible")
        if model == 'random_forest':
            st.write(random_forest(X,y))
        elif model == 'KNN':        
            st.write(KNN(X,y))
        elif model == 'SVM':        
            st.write(SVM(X,y))
        else:    
            st.write(f'Model is not valid')     
    st.write(f'Mean of Random Forest model',rf_mean)
    st.write(f'Mean of KNN model',knn_mean)
    st.write(f'Mean of SVM model',svm_mean)
    st.write(f'Model with minimum error is',best_accuracy_model(rf_mean, knn_mean, svm_mean))        
    st.write(f'R2 of Random Forest model',rf_r2)
    st.write(f'R2 of KNN Forest model',knn_r2)
    st.write(f'R2 of SVM model',svm_r2)
    st.write(f'Model with maximum r2 value is',max(rf_r2, knn_r2, svm_r2))

#-------------------------------------------------------------------#

# Tab 4 - Recommendations
with tab4:
    st.write("HELLOOOOO")
        
        