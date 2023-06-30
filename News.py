from bs4 import BeautifulSoup as bs 
import csv
import requests
import time
from datetime import datetime, timedelta


# returns the start time of yesterday
def get_yesterday_time():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    formatted_datetime = yesterday.strftime("%Y%m%dT%H%M")
    return formatted_datetime

# returns the start and end time of the ith day before today
def get_train_time(i):
    now = datetime.now()
    start = now - timedelta(days=i+1)
    end = now - timedelta(days=i)
    formatted_start = start.strftime("%Y%m%dT%H%M")
    formatted_end = end.strftime("%Y%m%dT%H%M")
    return (formatted_start, formatted_end)

# returns the sentiment score of the ticker in the last 24 hours
def get_todays_sentiment_score(ticker):
    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={}&time_from={}&limit=200&apikey=HQY4NMCEOKWDG9K3'.format(ticker, get_yesterday_time())
    r = requests.get(url)
    data = r.json()

    # in order to check if the ticker is valid OR there are no news for the ticker
    first_key = next(iter(data))
    if(first_key == "Information" and data['Information'].startswith("Invalid inputs")):
        feed = []
    else:
        feed = data['feed']

    ticker_sentiment = []

    for item in feed:
        ticker_sentiments = item['ticker_sentiment']
        for sentiment in ticker_sentiments:
            if sentiment['ticker'] == ticker:
                ticker_sentiment.append(float(sentiment['ticker_sentiment_score']))

    total_score = sum(ticker_sentiment)
    # to prevent division by 0
    if(len(ticker_sentiment) != 0):
        average_score = total_score / len(ticker_sentiment)
    else: average_score = 0

    return average_score

# creates a csv file with the sentiment score of the input stocks list for the last 24 hours
def get_todays_20stocks_sentiment_list(stocks_list):
    # Create the CSV file and write the header
    with open('newsSentimentScore.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Symbol", "News Sentiment Score"])

    for stock in stocks_list:
        print(stock)
        score = get_todays_sentiment_score(stock)
        # Append the ticker and average score to the CSV file
        with open('newsSentimentScore.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([stock, score])


# returns a list of the S&P500 tickers
def getSP500():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []

    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    all_stocks = [x.replace('\n','') for x in tickers] # remove the new line character
    return all_stocks



# Creates a csv file with the sentiment score of the S&P500 for the last 365 days
def get_SP500_train_sentiment_score():
    # Create the CSV file and write the header
    # with open('newsTrainSentimentScoreSP500.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(["Symbol", "Start Date", "News Sentiment Score"])


    # Get the list of all the tickers in the S&P 500
    sp500 = getSP500()
    for i in range(470, len(sp500)):
        ticker = sp500[i]
        print(ticker)
        for i in range(1, 366):
            start_time, end_time = get_train_time(i)
            url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={}&time_from={}&time_to={}&limit=200&apikey=HQY4NMCEOKWDG9K3'.format(ticker, start_time, end_time)

            try:
                r = requests.get(url)
                r.raise_for_status()  # Check for any HTTP errors
                data = r.json()
                # Rest of the code
            except requests.exceptions.RequestException as e:
                print("Error occurred during the request:", e)
                print("Response content:", r.content)  # Print the response content for debugging


            # in order to check if the ticker is valid OR there are no news for the ticker
            first_key = next(iter(data))
            if(first_key == "Information" and data['Information'].startswith("Invalid inputs")):
                feed = []
            else:


                feed = data['feed']

            ticker_sentiment = []


            for item in feed:
                ticker_sentiments = item['ticker_sentiment']
                for sentiment in ticker_sentiments:
                    if sentiment['ticker'] == ticker:
                        ticker_sentiment.append(float(sentiment['ticker_sentiment_score']))

            total_score = sum(ticker_sentiment)
            if(len(ticker_sentiment) != 0):
                average_score = total_score / len(ticker_sentiment)
            else: average_score = 0

            # Append the ticker, start time and average score to the CSV file
            with open('newsTrainSentimentScoreSP500.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([ticker, start_time, average_score])

def fix_and_remove_zeros():
    
    # Specify the path to your CSV file
    
    csv_file = "C:/Users/OR/‏‏newsTrainSentimentScoreSP50CHECK.csv"

    # Read the CSV file
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Create a dictionary to store the last part for each symbol
    last_parts = {}

    # Iterate over the rows and find the last part for each symbol
    current_symbol = None
    last_part_start = 0
    for i in range(1, len(rows)):
        symbol = rows[i][0]
        if symbol != current_symbol:
            if current_symbol is not None:
                last_parts[current_symbol] = rows[last_part_start:i]
            current_symbol = symbol
            last_part_start = i

    # Store the last part for the last symbol
    if current_symbol is not None:
        last_parts[current_symbol] = rows[last_part_start:]

    # Remove the row of zeros from the last parts
    for symbol, part in last_parts.items():
        if part and all(row == '0' for row in part[-1][1:]):
            last_parts[symbol] = part[:-1]

    # Write the last parts for each symbol to a single CSV file
    output_file = "C:/Users/OR/newsTrainSentimentScoreSP500CHECKafter.csv"
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(rows[0])  # Write the header row
        for symbol, part in last_parts.items():
            writer.writerows(part)

    print("The last parts for each symbol have been extracted and saved to", output_file)


