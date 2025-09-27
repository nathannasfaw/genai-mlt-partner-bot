#!/usr/bin/env python3
"""
Test script to verify S3 integration with CIK_module.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from CIK_module import SECEdgar

def test_s3_integration():
    """Test the S3 integration functionality"""
    print("Testing S3 integration...")
    
    try:
        # Test 1: S3 data source (should use your Lambda-uploaded data)
        print("\n=== Test 1: Using S3 data source ===")
        sec_s3 = SECEdgar(use_s3=True)
        
        # Test some lookups
        apple_cik = sec_s3.ticker_to_cik("AAPL")
        microsoft_cik = sec_s3.ticker_to_cik("MSFT")
        tesla_cik = sec_s3.name_to_cik("Tesla, Inc.")
        
        print(f"Apple (AAPL) CIK: {apple_cik}")
        print(f"Microsoft (MSFT) CIK: {microsoft_cik}")
        print(f"Tesla CIK: {tesla_cik}")
        
        # Test 2: Direct SEC API (fallback)
        print("\n=== Test 2: Using direct SEC API (fallback) ===")
        sec_direct = SECEdgar(use_s3=False)
        
        # Test same lookups
        apple_cik_direct = sec_direct.ticker_to_cik("AAPL")
        microsoft_cik_direct = sec_direct.ticker_to_cik("MSFT")
        tesla_cik_direct = sec_direct.name_to_cik("Tesla, Inc.")
        
        print(f"Apple (AAPL) CIK: {apple_cik_direct}")
        print(f"Microsoft (MSFT) CIK: {microsoft_cik_direct}")
        print(f"Tesla CIK: {tesla_cik_direct}")
        
        # Test 3: Compare results
        print("\n=== Test 3: Comparing results ===")
        print(f"Apple CIK match: {apple_cik == apple_cik_direct}")
        print(f"Microsoft CIK match: {microsoft_cik == microsoft_cik_direct}")
        print(f"Tesla CIK match: {tesla_cik == tesla_cik_direct}")
        
        # Test 4: Backward compatibility (old usage should still work)
        print("\n=== Test 4: Backward compatibility ===")
        sec_old = SECEdgar("https://www.sec.gov/files/company_tickers.json")
        apple_cik_old = sec_old.ticker_to_cik("AAPL")
        print(f"Apple (AAPL) CIK (old method): {apple_cik_old}")
        print(f"Backward compatibility: {apple_cik_old == apple_cik}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_s3_integration()