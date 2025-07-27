# Name: Nathan Asfaw
# Date: 2025-07-27
# Description: This module contains the CIK class, which is used to manage the CIK (Central Index Key) for SEC filings.

import requests
from typing import Optional, List

'''
The SECEdgar class is used to parse the public
filings from the SEC Edgar database. It then builds a 
hashmap to store the CIK of each company. They are then easily
retrievable by either the company name or ticker symbol.
It does not accept incomplete or invalid company names or ticker symbols.
'''
class SECEdgar: 
    def __init__(self, fileurl):
        self.fileurl = fileurl
        # initialize two dictionaries to store CIKs
        self.name_dict = {}
        self.ticker_dict = {}
        # headers used to follow SEC EDGAR Fair Access Policy 
        headers = {'User-Agent': 'MLT CP nathanrasfaw@gmail.com'}

        # send a GET request to the SEC EDGAR database and stores the response
        r = requests.get(self.fileurl, headers=headers)
        # stores the JSON response in the filejson variable
        self.filejson = r.json()

        self.cik_json_to_dict()

    # Method to convert the JSON response to a dictionary 
    def cik_json_to_dict(self):
        self.name_dict = {}
        self.ticker_dict = {}

        # iterate through each item in the JSON response
        for value in self.filejson.values():
            # get the CIK, name, and ticker from the item
            cik = value['cik_str']
            # Both name and ticker are converted to lowercase for case-insensitive matching
            name = value['title'].lower()
            ticker = value['ticker'].lower()

            # add the CIK to the name dictionary
            self.name_dict[name] = cik
            # add the CIK to the ticker dictionary
            self.ticker_dict[ticker] = cik


    # Method takes a given company name and returns the CIK number if applicable
    def name_to_cik(self, name: str) -> Optional[str]:
        try:
            return self.name_dict[name.lower()]
        except KeyError:
            print(f"Company name '{name}' not found.")
            return None
            

    # Method takes a given ticker symbol and returns the CIK number if applicable        
    def ticker_to_cik(self, ticker: str) -> Optional[str]:
        try:
            return self.ticker_dict[ticker.lower()]
        except KeyError:
            print(f"Ticker symbol '{ticker}' not found.")
            return None


    # (ADDITION) Method to search for company names that contain a given partial string
    def search_names(self, partial: str) -> List[str]:
        # Returns a list of all matching company names
        partial = partial.lower()
        return [name for name in self.name_dict if partial in name]     
    

se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
# Example usage:
# print(se.search_names('pineapple'))  # Should return list of names containing 'pineapple'
# print(se.name_to_cik('toro co')) # Should return CIK for 'Toro Co'
# print(se.ticker_to_cik('AAPL'))  # Should return CIK for 'AAPL'