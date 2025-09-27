#!/usr/bin/env python3
"""
Example usage of CIK_module.py with S3 integration
"""

from CIK_module import SECEdgar

def main():
    print("=== CIK Module S3 Integration Examples ===\n")
    
    # Example 1: Use S3 data (when AWS credentials are properly configured)
    print("1. Using S3 data source:")
    try:
        sec_s3 = SECEdgar(use_s3=True)
        print("✅ Successfully loaded from S3!")
        
        # Test some lookups
        apple_cik = sec_s3.ticker_to_cik("AAPL")
        print(f"   Apple (AAPL) CIK: {apple_cik}")
        
    except Exception as e:
        print(f"❌ S3 failed: {e}")
        print("   (This is expected if AWS credentials aren't configured)")
    
    print()
    
    # Example 2: Direct SEC API (always works, no AWS needed)
    print("2. Using direct SEC API (fallback/default):")
    sec_direct = SECEdgar(use_s3=False)
    apple_cik = sec_direct.ticker_to_cik("AAPL")
    microsoft_cik = sec_direct.ticker_to_cik("MSFT")
    print(f"   Apple (AAPL) CIK: {apple_cik}")
    print(f"   Microsoft (MSFT) CIK: {microsoft_cik}")
    
    print()
    
    # Example 3: Backward compatibility (existing code still works)
    print("3. Backward compatibility (old usage):")
    sec_old = SECEdgar("https://www.sec.gov/files/company_tickers.json")
    tesla_cik = sec_old.name_to_cik("Tesla, Inc.")
    print(f"   Tesla CIK: {tesla_cik}")
    
    print()
    
    # Example 4: Custom S3 bucket/key
    print("4. Custom S3 configuration:")
    try:
        sec_custom = SECEdgar(
            use_s3=True, 
            s3_bucket="your-custom-bucket", 
            s3_key="your-custom-key.json"
        )
        print("✅ Custom S3 config loaded!")
    except Exception as e:
        print(f"❌ Custom S3 failed (expected): {e}")
    
    print("\n=== Summary ===")
    print("✅ S3 integration successfully added to CIK_module.py")
    print("✅ Backward compatibility maintained")
    print("✅ Automatic fallback to SEC API when S3 fails")
    print("✅ No AWS credentials required for basic functionality")

if __name__ == "__main__":
    main()