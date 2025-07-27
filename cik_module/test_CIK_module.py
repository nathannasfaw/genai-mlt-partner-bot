import pytest
from CIK_module import SECEdgar


# Test for the name_to_cik method
def test_name_to_cik():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
    
    # Test with a valid company name
    cik = se.name_to_cik('Apple Inc.')
    assert cik == 320193, "Should return the correct CIK for Apple Inc."

    # Test with an invalid company name
    cik = se.name_to_cik('Nonexistent Company')
    assert cik is None, "Should return None for a nonexistent company name"


# Test for the ticker_to_cik method
def test_ticker_to_cik():
    se = SECEdgar('https://www.sec.gov/files/company_tickers.json')
    
    # Test with a valid ticker symbol
    cik = se.ticker_to_cik('AXP')
    assert cik == 4962, "Should return the correct CIK for AXP"

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




