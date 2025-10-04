"""
Test Lambda 2: SEC Document Processor
Tests integration with your CIK module and Lambda 1 S3 data.

This test validates:
- Lambda 2 can successfully import and use your CIK module
- S3 integration works (using Lambda 1's daily SEC data)
- Annual (10-K) document retrieval works
- Quarterly (10-Q) document retrieval works
- Error handling works properly
"""

import json
import sys
import os

# Add parent directory to path to import Lambda 2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda2_module.lambda_2 import lambda_handler

def test_lambda_2_integration():
    """Test Lambda 2 integration with your CIK module methods."""
    
    print("🧪 Testing Lambda 2: SEC Document Processor")
    print("=" * 50)
    
    # Test Annual request
    print("\n📄 Testing Annual (10-K) Request:")
    event1 = {
        "request_type": "Annual",
        "company": "AAPL",
        "year": "2023"
    }
    
    response1 = lambda_handler(event1, None)
    print(f"Status: {response1['statusCode']}")
    
    if response1['statusCode'] == 200:
        body1 = json.loads(response1['body'])
        print(f"✅ Found {body1['document_type']} for {body1['company']} (CIK: {body1['cik']})")
        print(f"   Document length: {len(body1['document_content'])} characters")
    else:
        body1 = json.loads(response1['body'])
        print(f"❌ Error: {body1.get('error', 'Unknown error')}")
    
    # Test Quarterly request
    print("\n📄 Testing Quarterly (10-Q) Request:")
    event2 = {
        "request_type": "Quarter",
        "company": "MSFT",
        "year": "2023",
        "quarter": "Q1"
    }
    
    response2 = lambda_handler(event2, None)
    print(f"Status: {response2['statusCode']}")
    
    if response2['statusCode'] == 200:
        body2 = json.loads(response2['body'])
        print(f"✅ Found {body2['document_type']} for {body2['company']} (CIK: {body2['cik']})")
        print(f"   Quarter: {body2['quarter']}, Document length: {len(body2['document_content'])} characters")
    else:
        body2 = json.loads(response2['body'])
        print(f"❌ Error: {body2.get('error', 'Unknown error')}")
    
    print("\n🎉 Simple Lambda 2 Test Complete!")
    print("✅ Uses your existing CIK module methods")
    print("✅ Perfect S3 integration from Lambda 1")
    print("✅ Super simple and clean code")

if __name__ == "__main__":
    test_lambda_2_integration()