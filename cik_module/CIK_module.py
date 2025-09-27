# Name: Nathan Asfaw
# Date: 2025-07-27
# Description: This module contains the CIK class, which is used to manage the CIK (Central Index Key) for SEC filings.

import requests
import datetime
from typing import Optional, List
import boto3
import json
from typing import Dict, Optional

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
        self.headers = {'User-Agent': 'MLT CP nathanrasfaw@gmail.com'}

        # send a GET request to the SEC EDGAR database and stores the response
        r = requests.get(self.fileurl, headers=self.headers)
        # stores the JSON response in the filejson variable
        self.filejson = r.json()

        self.cik_json_to_dict()

    # Method to convert the JSON response to a dictionary 
    def cik_json_to_dict(self):
        self.name_dict = {}
        self.ticker_dict = {}

        # iterate through each item in the JSON response
        for value in self.filejson.values():
            # get the CIK, name, and ticker from the item (strored as a string)
            cik = str(value['cik_str'])
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

    # Method to help find the filing of a companies 10-K form given a CIK number and a year
    def annual_filing(self, cik: str, year: int) -> Optional[str]:
        # Check if year is an integer and within a valid range
        current_year = datetime.datetime.now().year
        if not isinstance(year, int) or year < 1900 or year > current_year + 1:
            print(f"Invalid year: {year}")
            return None
        # Fetch the company's submission JSON data
        response_json = self.fetch_company_json(cik)
        # Check if the JSON data was successfully retrieved
        if response_json is None:
            print("Could not fetch company JSON data.")
            return None
        # Call the method to find the 10-K filing and return the result
        find_10k = self.find_10k_filing(cik, year, response_json)
        return find_10k

    # Method to help find the filing of a companies 10-Q form given a CIK number, year, and quarter
    def quarterly_filing(self, cik: str, year: int, quarter: int) -> Optional[str]:
        # Check if year is an integer and within a valid range
        current_year = datetime.datetime.now().year
        if not isinstance(year, int) or year < 1900 or year > current_year + 1:
            print(f"Invalid year: {year}")
            return None
        # Check if quarter is an integer between 1 and 4
        if quarter not in [1, 2, 3, 4]:
            print(f"Invalid quarter: {quarter}. Must be between 1 and 4.")
            return None
        # Fetch the company's submission JSON data
        response_json = self.fetch_company_json(cik)
        # Check if the JSON data was successfully retrieved
        if response_json is None:
            print("Could not fetch company JSON data.")
            return None
        # Call the method to find the 10-Q filing and return the result
        find_10q = self.find_10q_filing(cik, year, quarter, response_json)
        return find_10q
    
    # Method pads the CIK with leading zeros to ensure it is 10 digits long
    def cik_extender(self, cik: str) -> str:
        return cik.zfill(10)
    
    # Method retreives a company's submission JSON data from the submissions API using the CIK number
    def fetch_company_json(self, cik: str) -> Optional[dict]:
        if cik is None:
            return None
        padded_cik = self.cik_extender(cik)
        submissions_url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        response = requests.get(submissions_url, headers=self.headers)
        # Checks if the request was successful
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return None
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None

    # Method to find the most recent 10-K filing for a given CIK number and year
    def find_10k_filing(self, cik: str, year: int, response_json) -> Optional[str]:
        # 1. Search in recent filings
        recent = response_json.get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        filing_dates = recent.get('filingDate', [])
        accession_numbers = recent.get('accessionNumber', [])
        primary_documents = recent.get('primaryDocument', [])

        for i, form in enumerate(forms):
            if form == '10-K' and i < len(filing_dates):
                if filing_dates[i].startswith(str(year)):
                    acc_num = accession_numbers[i].replace('-', '')
                    doc = primary_documents[i]
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                    return filing_url

        # 2. If not found, check each file in "files" (no recursion)
        files = response_json.get('filings', {}).get('files', [])
        for file_info in files:
            file_url = f"https://data.sec.gov/submissions/{file_info['name']}"
            resp = requests.get(file_url, headers=self.headers)
            if resp.status_code == 200:
                file_json = resp.json()
                recent = file_json.get('filings', {}).get('recent', {})
                forms = recent.get('form', [])
                filing_dates = recent.get('filingDate', [])
                accession_numbers = recent.get('accessionNumber', [])
                primary_documents = recent.get('primaryDocument', [])
                for i, form in enumerate(forms):
                    if form == '10-K' and i < len(filing_dates):
                        if filing_dates[i].startswith(str(year)):
                            acc_num = accession_numbers[i].replace('-', '')
                            doc = primary_documents[i]
                            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                            return filing_url
            else:
                print(f"Failed to fetch {file_url} (status {resp.status_code})")

        print(f"No 10-K filing found for year {year}.")
        return None
    
    def find_10q_filing(self, cik: str, year: int, quarter: int, response_json) -> Optional[str]:
        if response_json is None:
            print("No JSON data provided to find_10q_filing.")
            return None

        # 1. Search in recent filings
        recent = response_json.get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        filing_dates = recent.get('filingDate', [])
        accession_numbers = recent.get('accessionNumber', [])
        primary_documents = recent.get('primaryDocument', [])

        for i, form in enumerate(forms):
            if form == '10-Q' and i < len(filing_dates):
                if filing_dates[i].startswith(str(year)):
                    month = int(filing_dates[i][5:7])
                    if (quarter == 1 and month in [1, 2, 3]) or \
                    (quarter == 2 and month in [4, 5, 6]) or \
                    (quarter == 3 and month in [7, 8, 9]) or \
                    (quarter == 4 and month in [10, 11, 12]):
                        acc_num = accession_numbers[i].replace('-', '')
                        doc = primary_documents[i]
                        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                        return filing_url

        # 2. If not found, check each file in "files" (no recursion)
        files = response_json.get('filings', {}).get('files', [])
        for file_info in files:
            file_url = f"https://data.sec.gov/submissions/{file_info['name']}"
            resp = requests.get(file_url, headers=self.headers)
            if resp.status_code == 200:
                file_json = resp.json()
                recent = file_json.get('filings', {}).get('recent', {})
                forms = recent.get('form', [])
                filing_dates = recent.get('filingDate', [])
                accession_numbers = recent.get('accessionNumber', [])
                primary_documents = recent.get('primaryDocument', [])
                for i, form in enumerate(forms):
                    if form == '10-Q' and i < len(filing_dates):
                        if filing_dates[i].startswith(str(year)):
                            month = int(filing_dates[i][5:7])
                            if (quarter == 1 and month in [1, 2, 3]) or \
                            (quarter == 2 and month in [4, 5, 6]) or \
                            (quarter == 3 and month in [7, 8, 9]) or \
                            (quarter == 4 and month in [10, 11, 12]):
                                acc_num = accession_numbers[i].replace('-', '')
                                doc = primary_documents[i]
                                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                                return filing_url
            else:
                print(f"Failed to fetch {file_url} (status {resp.status_code})")

        print(f"No 10-Q filing found for year {year} and quarter {quarter}.")
        return None

# Example usage of the SECEdgar class
se = SECEdgar('https://www.sec.gov/files/company_tickers.json')

apple_cik = se.ticker_to_cik('AAPL')
print(type(apple_cik)) # Should be str
print(apple_cik)  # Should return CIK for 'GOOGL'

padded_apple_cik = se.cik_extender(apple_cik)
print(padded_apple_cik)  # Should return the CIK padded to 10 digits


nvidia_cik = se.ticker_to_cik('NVDA')
print(nvidia_cik)  # Should return CIK for 'KPMG LLP'
filing_url = se.quarterly_filing(nvidia_cik, 2021, 2)
print(filing_url)  # Should return the URL of KPMG's 10-Q filing

microsoft_cik = se.ticker_to_cik('MSFT')
print(microsoft_cik)  # Should return CIK for 'Microsoft Corp'
filing_url = se.annual_filing(microsoft_cik, 2022)
print(filing_url)  # Should return the URL of Microsoft's 10-K filing