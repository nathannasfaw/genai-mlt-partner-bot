# Name: Nathan Asfaw
# Date: 2025-07-27
# Description: This module contains the CIK class, which is used to manage the CIK (Central Index Key) for SEC filings.

import requests
import datetime
from typing import Optional, List
import boto3
import json
import os 
from typing import Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

'''
The SECEdgar class is used to parse the public
filings from the SEC Edgar database. It then builds a 
hashmap to store the CIK of each company. They are then easily
retrievable by either the company name or ticker symbol.
It does not accept incomplete or invalid company names or ticker symbols.
'''
class SECEdgar: 
    def __init__(self, fileurl=None, use_s3=False, s3_bucket=None, s3_key=None):
        self.fileurl = fileurl
        # initialize two dictionaries to store CIKs
        self.name_dict = {}
        self.ticker_dict = {}
        # headers used to follow SEC EDGAR Fair Access Policy 
        self.headers = {'User-Agent': 'MLT CP nathanrasfaw@gmail.com'}

        if use_s3:
            # Use S3 data source
            if s3_bucket is None:
                s3_bucket = "nathanasfaw-sec-edgar-files"
            if s3_key is None:
                s3_key = "company_tickers.json"
            
            try:
                # Check if running in Lambda or local environment
                if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
                    # Running in Lambda - use execution role
                    print("Detected Lambda environment, using execution role")
                    s3_client = boto3.client('s3')
                else:
                    # Running locally - try profile first, fallback to default
                    print("Detected local environment, trying profile configuration")
                    try:
                        session = boto3.Session(profile_name='mlt-course-730128023791')
                        s3_client = session.client('s3')
                        print("Using profile: mlt-course-730128023791")
                    except (ProfileNotFound, NoCredentialsError) as profile_error:
                        print(f"Profile not found ({profile_error}), falling back to default credentials")
                        s3_client = boto3.client('s3')
                
                # Attempt to get the object from S3
                response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
                self.filejson = json.loads(response['Body'].read().decode('utf-8'))
                print(f"Successfully loaded data from S3: s3://{s3_bucket}/{s3_key}")

            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"S3 ClientError ({error_code}): {e}")
                print("Falling back to direct SEC API call...")
                use_s3 = False
            except Exception as e:
                print(f"Error loading from S3: {e}")
                print("Falling back to direct SEC API call...")
                use_s3 = False
        
        if not use_s3:
            # Fallback to direct SEC API call
            if fileurl is None:
                fileurl = "https://www.sec.gov/files/company_tickers.json"
            # send a GET request to the SEC EDGAR database and stores the response
            r = requests.get(fileurl, headers=self.headers)
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
                    doc = primary_documents[i].strip().rstrip('\\/')
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
                            doc = primary_documents[i].strip().rstrip('\\/')
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

        # Collect all 10-Q filings for the year from recent filings
        quarterly_filings = []
        
        # 1. Search in recent filings
        recent = response_json.get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        filing_dates = recent.get('filingDate', [])
        accession_numbers = recent.get('accessionNumber', [])
        primary_documents = recent.get('primaryDocument', [])

        for i, form in enumerate(forms):
            if form == '10-Q' and i < len(filing_dates):
                if filing_dates[i].startswith(str(year)):
                    acc_num = accession_numbers[i].replace('-', '')
                    doc = primary_documents[i].strip().rstrip('\\/')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                    quarterly_filings.append((filing_dates[i], filing_url))

        # 2. If not enough filings found, check each file in "files"
        if len(quarterly_filings) < quarter:
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
                                acc_num = accession_numbers[i].replace('-', '')
                                doc = primary_documents[i].strip().rstrip('\\/')
                                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc}"
                                quarterly_filings.append((filing_dates[i], filing_url))
                else:
                    print(f"Failed to fetch {file_url} (status {resp.status_code})")

        # Sort filings by date (most recent first)
        quarterly_filings.sort(key=lambda x: x[0], reverse=True)
        
        # Return the nth quarterly filing (1st, 2nd, 3rd, or 4th)
        if 1 <= quarter <= len(quarterly_filings):
            print(f"Found {len(quarterly_filings)} quarterly filings for {year}, returning #{quarter}")
            return quarterly_filings[quarter - 1][1]  # Return URL
        
        print(f"No 10-Q filing found for year {year} and quarter {quarter}. Found {len(quarterly_filings)} total quarterly filings.")
        return None

    # Simple method to get filing content from URL
    def get_filing_content(self, filing_url: str) -> Optional[str]:
        """Get the content of a SEC filing document."""
        if not filing_url:
            return None
        try:
            response = requests.get(filing_url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error getting filing content: {e}")
            return None
