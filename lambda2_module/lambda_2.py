"""
Lambda 2: SEC Document Processor
Processes JSON requests for 10-K (Annual) and 10-Q (Quarterly) documents.

This Lambda function integrates perfectly with your existing CIK module:
- Uses your Lambda 1 S3 data via CIK module's S3 integration
- Leverages all existing CIK lookup methods (ticker_to_cik, name_to_cik)
- Utilizes existing filing retrieval methods (annual_filing, quarterly_filing)
- Returns filing URL instead of full document content to avoid Lambda size limits

Author: Nathan Asfaw
Date: 2025-09-27
"""

import json
from CIK_module import SECEdgar

def lambda_handler(event, context):
    """
    AWS Lambda handler for processing SEC document requests.
    
    This function integrates with your existing CIK module methods:
    1. Uses SECEdgar with S3 integration
    2. Looks up CIK using ticker_to_cik() or name_to_cik() methods
    3. Gets filing URLs using annual_filing() or quarterly_filing() methods  
    4. Returns the filing URL for direct access to SEC documents
    
    Expected JSON input:
    {
        "request_type": "Annual" | "Quarter",
        "company": "AAPL" | "Apple Inc.",
        "year": "2023",
        "quarter": "Q1" (required only for Quarter requests)
    }
    
    Returns JSON response with filing URL or error message.
    """
    
    try:
        # Extract parameters from the incoming JSON event
        request_type = event.get('request_type')  # 'Annual' or 'Quarter'
        company = event.get('company')            # Ticker symbol or company name
        year = int(event.get('year'))             # Filing year as integer
        
        # Initialize CIK module with S3 integration
        # Uses Lambda 1's daily SEC data from S3 bucket
        sec_edgar = SECEdgar(use_s3=True)
        
        # Look up CIK using your existing methods
        # Try ticker first (AAPL), then company name (Apple Inc.)
        cik = sec_edgar.ticker_to_cik(company) or sec_edgar.name_to_cik(company)
        if not cik:
            return {'statusCode': 404, 'body': json.dumps({'error': f'Company {company} not found'})}
        
        # Get SEC filing URL using your existing methods
        if request_type == 'Annual':
            # Use your annual_filing method to get 10-K URL
            filing_url = sec_edgar.annual_filing(cik, year)
            document_type = '10-K'
        elif request_type == 'Quarter':
            # Check if quarter is provided for quarterly requests
            quarter_input = event.get('quarter')
            if not quarter_input:
                return {
                    'statusCode': 400, 
                    'body': json.dumps({'error': 'Quarter is required for quarterly requests'})
                }
            
            # Convert quarter format ('Q1' -> 1) and validate
            try:
                quarter = int(str(quarter_input).replace('Q', ''))
                if quarter not in [1, 2, 3, 4]:
                    return {
                        'statusCode': 400, 
                        'body': json.dumps({'error': 'Quarter must be 1, 2, 3, or 4'})
                    }
            except (ValueError, TypeError):
                return {
                    'statusCode': 400, 
                    'body': json.dumps({'error': 'Invalid quarter format'})
                }
                
            filing_url = sec_edgar.quarterly_filing(cik, year, quarter)
            document_type = '10-Q'
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid request_type'})}
        
        # Check if filing URL was found
        if not filing_url:
            return {'statusCode': 404, 'body': json.dumps({'error': f'No {document_type} found'})}
        
        # Return successful response with filing URL (no document content)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'company': company,
                'cik': cik,
                'document_type': document_type,
                'year': year,
                'quarter': event.get('quarter') if request_type == 'Quarter' else None,
                'filing_url': filing_url,
                'message': 'Use the filing_url to access the full SEC document'
            })
        }
        
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}