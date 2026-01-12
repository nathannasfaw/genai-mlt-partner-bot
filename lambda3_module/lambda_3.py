# lambda_3.py - Simplified SEC Question Answering Lambda with Claude Sonnet 4
import json
import boto3
import requests
from bs4 import BeautifulSoup

def determine_filing_type(question):
    """Analyze question to determine if it needs annual or quarterly data"""
    question_lower = question.lower()
    
    # Check for specific quarters
    if 'q1' in question_lower or 'first quarter' in question_lower:
        return "Quarter", "1"
    elif 'q2' in question_lower or 'second quarter' in question_lower:
        return "Quarter", "2"
    elif 'q3' in question_lower or 'third quarter' in question_lower:
        return "Quarter", "3"
    elif 'q4' in question_lower or 'fourth quarter' in question_lower:
        return "Quarter", "4"
    
    # Check for quarterly keywords
    quarterly_keywords = ['quarter', 'quarterly', 'q1', 'q2', 'q3', 'q4', '10-q']
    if any(keyword in question_lower for keyword in quarterly_keywords):
        return "Quarter", "1"  # Default to Q1
    
    # Default to annual
    return "Annual", None

def get_sec_document_url(company, year, question):
    """Get SEC document URL using Lambda 2"""
    filing_type, quarter = determine_filing_type(question)
    print(f"📋 DEBUG: Detected filing type: {filing_type}, quarter: {quarter}")  # ADD THIS LINE

    lambda_client = boto3.client('lambda')
    lambda2_request = {
        "request_type": filing_type,
        "company": company,
        "year": str(year)
    }
    
    if filing_type == "Quarter" and quarter:
        lambda2_request["quarter"] = quarter
    
    print(f"📤 DEBUG: Sending to Lambda 2: {lambda2_request}")  # ADD THIS LINE

    try:
        response = lambda_client.invoke(
            FunctionName='NathanAsfaw-SEC-Document-Processor',
            Payload=json.dumps(lambda2_request)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"📥 DEBUG: Lambda 2 response: {result}")  # ADD THIS LINE
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"✅ DEBUG: Extracted filing URL: {body['filing_url']}")  # ADD THIS
            return body['filing_url']
        print(f"❌ DEBUG: Lambda 2 returned status: {result['statusCode']}")  # ADD THIS
        return None
            
    except Exception as e:
        print(f"Error calling Lambda 2: {e}")
        return None

def download_sec_document(filing_url):
    """Download and clean SEC document"""
    try:
        headers = {'User-Agent': 'nathanrasfaw@gmail.com SEC Analysis'}
        response = requests.get(filing_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
        
        # Convert HTML to clean text
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.remove()
        
        text = soup.get_text()
        clean_text = ' '.join(text.split())
        
        # Increase size limit to capture financial statements
        return clean_text[:100000] if len(clean_text) > 100000 else clean_text  # Increased from 40000
        
    except Exception as e:
        print(f"Error downloading document: {e}")
        return None

def ask_claude_question(question, document_text, company, year, filing_type, quarter=None):
    """Ask Claude 3.5 Sonnet to answer the question using the SEC document"""
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        # Create filing description
        filing_desc = f"{filing_type} filing"
        if filing_type == "Quarter" and quarter:
            filing_desc = f"Q{quarter} quarterly (10-Q) filing"
        elif filing_type == "Annual":
            filing_desc = "annual (10-K) filing"
        
        # Modern Claude 3.5 Sonnet format (messages API)
        prompt = f"""You are a financial analyst. Answer this question about {company} ({year}) based on their {filing_desc}:

Question: {question}

SEC Document:
{document_text}

Answer based only on the document provided. Be specific and cite relevant details."""

        # Modern Claude 3.5 Sonnet request format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Use Claude 3.5 Sonnet (modern, non-legacy)
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        print(f"Error asking Claude: {e}")
        return f"Sorry, I couldn't process your question. Error: {e}"

def lambda_handler(event, context):
    """
    Main Lambda function - this is what AWS calls when someone uses your Lambda
    
    Expected input:
    {
        "question": "What was Apple's revenue in 2023?",
        "ticker": "AAPL",
        "year": "2023"
    }
    
    OR with optional explicit filing type:
    {
        "question": "What was Apple's Q3 revenue?",
        "ticker": "AAPL", 
        "year": "2023",
        "filing_type": "Quarter",
        "quarter": "3"
    }
    """
    print("Lambda 3 started - SEC Question Answering")
    
    try:
        # Step 1: Get the inputs
        question = event.get('question')
        company = event.get('ticker') or event.get('company')
        year = event.get('year')
        
        # Optional: User can specify filing type directly
        explicit_filing_type = event.get('filing_type')
        explicit_quarter = event.get('quarter')
        
        # Check if we have everything we need
        if not question:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide a question'})
            }
        
        if not company:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide a company ticker (like AAPL)'})
            }
        
        if not year:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide a year (like 2023)'})
            }
        
        # Convert year to number
        try:
            year = int(year)
        except:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Year must be a number'})
            }
        
        print(f"Processing: {question} for {company} in {year}")
        
        # Step 2: Get SEC document URL from Lambda 2
        filing_url = get_sec_document_url(company, year, question)
        print(f"🔍 DEBUG: Filing URL received from Lambda 2: {filing_url}")  # ADD THIS LINE
        if not filing_url:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Could not find SEC filing for {company} in {year}'})
            }
        
        # Step 3: Download and clean the SEC document
        document_text = download_sec_document(filing_url)
        print(f"📄 DEBUG: Document downloaded, length: {len(document_text) if document_text else 'None'}")  # ADD THIS LINE
        if not document_text:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Could not download SEC document'})
            }
        
        # Step 4: Determine what filing type was used
        if explicit_filing_type:
            filing_type = explicit_filing_type
            quarter = explicit_quarter
        else:
            filing_type, quarter = determine_filing_type(question)
        
        # Step 5: Ask Claude Sonnet 4 to answer the question
        answer = ask_claude_question(question, document_text, company, year, filing_type, quarter)
        
        # Step 6: Return the answer
        return {
            'statusCode': 200,
            'body': json.dumps({
                'question': question,
                'company': company,
                'year': year,
                'filing_type': filing_type,
                'quarter': quarter if filing_type == "Quarter" else None,
                'answer': answer,
                'sec_document_url': filing_url,
                'document_size': len(document_text),
                'model_used': 'Claude 3.5 Sonnet',
                'success': True
            })
        }
        
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Something went wrong: {e}'})
        }

# Test function you can run locally
def test_locally():
    """
    Test the Lambda locally (won't work without AWS credentials)
    """
    print("Testing different question types...")
    
    # Test 1: Annual question
    test_annual = {
        "question": "What was Apple's total revenue in 2023?",
        "ticker": "AAPL",
        "year": "2023"
    }
    print(f"\nTest 1 (Annual): {test_annual['question']}")
    filing_type, quarter = determine_filing_type(test_annual['question'])
    print(f"Detected: {filing_type}" + (f" Q{quarter}" if quarter else ""))
    
    # Test 2: Quarterly question
    test_quarterly = {
        "question": "How much did Amazon invest in Anthropic in Q3 2023?",
        "ticker": "AMZN",
        "year": "2023"
    }
    print(f"\nTest 2 (Quarterly): {test_quarterly['question']}")
    filing_type, quarter = determine_filing_type(test_quarterly['question'])
    print(f"Detected: {filing_type}" + (f" Q{quarter}" if quarter else ""))
    
    # Test 3: General quarterly question
    test_general = {
        "question": "What were the quarterly earnings?",
        "ticker": "MSFT",
        "year": "2023"
    }
    print(f"\nTest 3 (General Quarterly): {test_general['question']}")
    filing_type, quarter = determine_filing_type(test_general['question'])
    print(f"Detected: {filing_type}" + (f" Q{quarter}" if quarter else ""))

if __name__ == "__main__":
    test_locally()