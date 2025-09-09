import pytest
from CIK_module import SECEdgar


# Test for the name_to_cik method
def test_name_to_cik():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
    
    # Test with a valid company name
    cik = se.name_to_cik('Apple Inc.')
    assert cik == '320193', "Should return the correct CIK for Apple Inc."

    # Test with an invalid company name
    cik = se.name_to_cik('Nonexistent Company')
    assert cik is None, "Should return None for a nonexistent company name"


# Test for the ticker_to_cik method
def test_ticker_to_cik():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
    
    # Test with a valid ticker symbol
    cik = se.ticker_to_cik('AXP')
    assert cik == '4962', "Should return the correct CIK for AXP"

    # Test with an invalid ticker symbol
    cik = se.ticker_to_cik('NONEXISTENT')
    assert cik is None, "Should return None for a nonexistent ticker symbol"


# Test for the search_names method
def test_search_names():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')

    # Test with a partial string that matches multiple names
    results = se.search_names('bank')
    assert len(results) > 0, "Should return a list of names containing 'bank'"

    # Test with a partial string that matches no names
    results = se.search_names('nonexistent')
    assert len(results) == 0, "Should return an empty list for a nonexistent partial string"


# Test for the cik_extender method
def test_cik_extender():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')

    # Test with a CIK that is less than 10 digits
    extended_cik = se.cik_extender('123456')
    assert extended_cik == '0000123456', "Should pad the CIK with leading zeros to make it 10 digits"

    # Test with a CIK that is already 10 digits
    extended_cik = se.cik_extender('0000123456')
    assert extended_cik == '0000123456', "Should return the CIK unchanged if it is already 10 digits"

# Test for the fetch_company_json method
def test_fetch_company_json():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')

    # Test with a valid CIK, Google Inc.
    response_json = se.fetch_company_json('1652044')
    assert response_json is not None, "Should return JSON data for a valid CIK"

    # Test with an invalid CIK
    response_json = se.fetch_company_json('0000000')
    assert response_json is None, "Should return None for an invalid CIK"

    # Test with None as CIK
    response_json = se.fetch_company_json(None)
    assert response_json is None, "Should return None when CIK is None"

    # Test with leading zeros in CIK
    response_json = se.fetch_company_json('0001652044')
    assert response_json is not None, "Should handle CIK with leading zeros"

     
# Test for the find_10k_filing method
def test_find_10k_filing():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')

    # Fetch JSON data for Apple Inc.
    apple_json = se.fetch_company_json('0000320193')  # CIK for Apple Inc.
    filing_url = se.find_10k_filing('0000320193', 2021, apple_json)
    assert filing_url is not None, "Should return the URL of Apple's 10-K filing"

    # Test with a year that has no 10-K filing
    filing_url = se.find_10k_filing('0000320193', 1990, apple_json)
    assert filing_url is None, "Should return None for a year with no 10-K filing"

    # Test with Microsoft Corp.
    msft_json = se.fetch_company_json('0000789019')  # CIK for Microsoft Corp.
    filing_url = se.find_10k_filing('0000789019', 2022, msft_json)
    assert filing_url is not None, "Should return the URL of Microsoft's 10-K filing"

# Test for the find_10q_filing method
def test_find_10q_filing():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
    # Fetch JSON data for Tesla Inc.
    tesla_json = se.fetch_company_json('0001318605')  # CIK for Tesla Inc.
    filing_url = se.find_10q_filing('0001318605', 2021, 2, tesla_json)
    assert filing_url is not None, "Should return the URL of Tesla's 10-Q filing"

    # Test with a quarter that has no 10-Q filing
    filing_url = se.find_10q_filing('0001318605', 1990, 1, tesla_json)
    assert filing_url is None, "Should return None for a quarter with no 10-Q filing"