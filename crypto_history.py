#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to gather historical cryptocurrency data from coinmarketcap.com (cmc) """

import json
import requests
from bs4 import BeautifulSoup
import csv
import sys
from time import sleep


def CoinNames():
    """Gets ID's of all coins on cmc"""
    api_key = "e6dcb452-c2cc-4f4f-8c7b-5d8ee58606f9"

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    parameters = {
        "start": "1",
        "limit": "100",
        "convert": "USD",
        "tag": "all",
        "cryptocurrency_type": "all",
    }

    headers = {
        "Accepts": "*/*",
        "X-CMC_PRO_API_KEY": api_key,
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers, params=parameters)

    if response.status_code == 200:
        try:
            respJSON = json.loads(response.text)
            print(respJSON)
            return [coin["symbol"] for coin in respJSON["data"]]
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print(f"HTTP request failed with status code: {response.status_code}")
        return None


def gather(startdate, enddate, names):
    headers = []
    historicaldata = []
    counter = 1

    if names is None or len(names) == 0:
        print("Coin names not available or empty.")
        sys.exit(1)

    for coin in names:
        sleep(10)
        coin_url = f"https://coinmarketcap.com/currencies/{coin}/historical-data/?start={startdate}&end={enddate}"
        response = requests.get(coin_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", attrs={"class": "table"})

            # Add table header to list
            if len(historicaldata) == 0:
                headers = [header.text for header in table.find_all("th")]
                headers.insert(0, "Coin")

            for row in table.find_all("tr"):
                currentrow = [val.text for val in row.find_all("td")]
                if len(currentrow) != 0:
                    currentrow.insert(0, coin)
                historicaldata.append(currentrow)

            print("Coin Counter -> " + str(counter), end="\r")
            counter += 1
        else:
            print(
                f"Failed to fetch data for {coin}. Status code: {response.status_code}"
            )

    return headers, historicaldata


def _gather(startdate, enddate):
    """Scrape data off cmc"""

    names = CoinNames()
    if names is None:
        print("Failed to get coin names. Exiting.")
        return

    headers, historicaldata = gather(startdate, enddate, names)
    Save(headers, historicaldata)


def Save(headers, rows):
    if len(sys.argv) == 3:
        FILE_NAME = "HistoricalCoinData.csv"
    else:
        FILE_NAME = sys.argv[3] + ".csv"

    with open(FILE_NAME, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(row for row in rows if row)
    print("Finished!")


if __name__ == "__main__":
    startdate = sys.argv[1]
    enddate = sys.argv[2]

    names = CoinNames()
    print(names)
    _gather(startdate, enddate)
