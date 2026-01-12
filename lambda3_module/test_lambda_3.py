# test_lambda_3.py - Comprehensive tests for Lambda 3 (SEC Question Answering)
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the current directory to Python path so we can import lambda_3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lambda_3 import (
    determine_filing_type,
    get_sec_document_url,
    download_sec_document,
    ask_claude_question,
    lambda_handler
)

class TestFilingTypeDetection:
    """Test the filing type detection logic"""
    
    def test_annual_questions(self):
        """Test questions that should be detected as annual"""
        annual_questions = [
            "What was Apple's total revenue in 2023?",
            "What is the annual profit for Microsoft?",
            "Show me the yearly earnings",
            "What was the full year revenue?",
            "Annual report analysis"
        ]
        
        for question in annual_questions:
            filing_type, quarter = determine_filing_type(question)
            assert filing_type == "Annual", f"Failed for: {question}"
            assert quarter is None, f"Quarter should be None for: {question}"
    
    def test_quarterly_questions_specific(self):
        """Test questions with specific quarters"""
        quarterly_tests = [
            ("What was revenue in Q1 2023?", "1"),
            ("Q2 earnings report", "2"),
            ("Show me Q3 data", "3"),
            ("Q4 results analysis", "4"),
            ("First quarter revenue", "1"),
            ("Second quarter profit", "2"),
            ("Third quarter earnings", "3"),
            ("Fourth quarter sales", "4")
        ]
        
        for question, expected_quarter in quarterly_tests:
            filing_type, quarter = determine_filing_type(question)
            assert filing_type == "Quarter", f"Failed filing type for: {question}"
            assert quarter == expected_quarter, f"Expected Q{expected_quarter}, got Q{quarter} for: {question}"
    
    def test_general_quarterly_questions(self):
        """Test general quarterly questions (should default to Q1)"""
        general_quarterly = [
            "What are the quarterly earnings?",
            "Show me quarterly data",
            "Quarterly revenue analysis",
            "10-Q filing information"
        ]
        
        for question in general_quarterly:
            filing_type, quarter = determine_filing_type(question)
            assert filing_type == "Quarter", f"Failed for: {question}"
            assert quarter == "1", f"Should default to Q1 for: {question}"

class TestLambdaIntegration:
    """Test Lambda 2 integration"""
    
    @patch('lambda_3.boto3.client')
    def test_get_sec_document_url_success(self, mock_boto):
        """Test successful SEC document URL retrieval"""
        # Mock Lambda client and response
        mock_lambda_client = Mock()
        mock_boto.return_value = mock_lambda_client
        
        # Mock successful response from Lambda 2
        mock_payload = Mock()
        mock_payload.read.return_value = json.dumps({
            'statusCode': 200,
            'body': json.dumps({'filing_url': 'https://test-sec-url.com'})
        }).encode()
        
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=mock_payload)
        mock_lambda_client.invoke.return_value = mock_response
        
        # Test the function
        result = get_sec_document_url("AAPL", 2023, "What was revenue in 2023?")
        
        # Assertions
        assert result == 'https://test-sec-url.com'
        mock_lambda_client.invoke.assert_called_once()
        
        # Check the payload sent to Lambda 2
        call_args = mock_lambda_client.invoke.call_args
        payload = json.loads(call_args[1]['Payload'])
        assert payload['company'] == 'AAPL'
        assert payload['year'] == '2023'
        assert payload['request_type'] == 'Annual'
    
    @patch('lambda_3.boto3.client')
    def test_get_sec_document_url_quarterly(self, mock_boto):
        """Test quarterly request to Lambda 2"""
        mock_lambda_client = Mock()
        mock_boto.return_value = mock_lambda_client
        
        mock_payload = Mock()
        mock_payload.read.return_value = json.dumps({
            'statusCode': 200,
            'body': json.dumps({'filing_url': 'https://test-q3-url.com'})
        }).encode()
        
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=mock_payload)
        mock_lambda_client.invoke.return_value = mock_response
        
        # Test with Q3 question
        result = get_sec_document_url("MSFT", 2023, "What was Q3 revenue?")
        
        # Check the payload includes quarter
        call_args = mock_lambda_client.invoke.call_args
        payload = json.loads(call_args[1]['Payload'])
        assert payload['request_type'] == 'Quarter'
        assert payload['quarter'] == '3'
    
    @patch('lambda_3.boto3.client')
    def test_get_sec_document_url_failure(self, mock_boto):
        """Test handling of Lambda 2 failure"""
        mock_lambda_client = Mock()
        mock_boto.return_value = mock_lambda_client
        
        # Mock failed response
        mock_payload = Mock()
        mock_payload.read.return_value = json.dumps({
            'statusCode': 404,
            'body': json.dumps({'error': 'Filing not found'})
        }).encode()
        
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=mock_payload)
        mock_lambda_client.invoke.return_value = mock_response
        
        result = get_sec_document_url("INVALID", 2023, "What was revenue?")
        assert result is None

class TestDocumentDownload:
    """Test SEC document download and processing"""
    
    @patch('lambda_3.requests.get')
    def test_download_sec_document_success(self, mock_get):
        """Test successful document download"""
        # Mock successful HTTP response with simple clean HTML
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body>Total revenue was $100 billion in fiscal year 2023. Net income increased by 15% year over year.</body></html>'
        mock_get.return_value = mock_response
        
        result = download_sec_document("https://test-url.com")
        
        # Check that the content was processed
        assert result is not None
        assert "Total revenue was $100 billion" in result
        assert "Net income increased by 15%" in result
    
    @patch('lambda_3.requests.get')
    def test_download_sec_document_failure(self, mock_get):
        """Test handling of download failure"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = download_sec_document("https://invalid-url.com")
        assert result is None
    
    @patch('lambda_3.requests.get')
    def test_download_sec_document_large_content(self, mock_get):
        """Test that large documents are truncated"""
        mock_response = Mock()
        mock_response.status_code = 200
        # Create content larger than 40000 characters
        large_content = "<html><body>" + "A" * 50000 + "</body></html>"
        mock_response.content = large_content.encode()
        mock_get.return_value = mock_response
        
        result = download_sec_document("https://large-doc.com")
        
        # Should be truncated to 40000 characters or less
        assert result is not None
        assert len(result) <= 40000

class TestClaudeIntegration:
    """Test Claude Sonnet 4 integration"""
    
    @patch('lambda_3.boto3.client')
    def test_ask_claude_question_success(self, mock_boto):
        """Test successful Claude interaction"""
        mock_bedrock = Mock()
        mock_boto.return_value = mock_bedrock
        
        # Mock Claude's response
        mock_body = Mock()
        mock_body.read.return_value = json.dumps({
            'content': [{'text': 'According to the SEC filing, Apple\'s revenue was $383.3 billion in fiscal 2023.'}]
        }).encode()
        
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=mock_body)
        mock_bedrock.invoke_model.return_value = mock_response
        
        result = ask_claude_question(
            "What was Apple's revenue?",
            "Sample SEC document content about Apple's financials...",
            "AAPL",
            2023,
            "Annual"
        )
        
        assert "383.3 billion" in result
        
        # Verify the model call
        mock_bedrock.invoke_model.assert_called_once()
        call_args = mock_bedrock.invoke_model.call_args
        assert call_args[1]['modelId'] == "anthropic.claude-4-sonnet-20241022-v1:0"
    
    @patch('lambda_3.boto3.client')
    def test_ask_claude_question_quarterly(self, mock_boto):
        """Test Claude with quarterly data"""
        mock_bedrock = Mock()
        mock_boto.return_value = mock_bedrock
        
        mock_body = Mock()
        mock_body.read.return_value = json.dumps({
            'content': [{'text': 'Q3 2023 revenue was $22.1 billion according to the 10-Q filing.'}]
        }).encode()
        
        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=mock_body)
        mock_bedrock.invoke_model.return_value = mock_response
        
        result = ask_claude_question(
            "What was Q3 revenue?",
            "Q3 SEC filing content...",
            "MSFT",
            2023,
            "Quarter",
            "3"
        )
        
        assert "Q3 2023" in result
        assert "22.1 billion" in result

class TestLambdaHandler:
    """Test the main lambda handler"""
    
    def test_lambda_handler_missing_params(self):
        """Test error handling for missing parameters"""
        # Missing question
        event = {"ticker": "AAPL", "year": "2023"}
        result = lambda_handler(event, None)
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'question' in body['error'].lower()
        
        # Missing ticker
        event = {"question": "What is revenue?", "year": "2023"}
        result = lambda_handler(event, None)
        assert result['statusCode'] == 400
        
        # Missing year
        event = {"question": "What is revenue?", "ticker": "AAPL"}
        result = lambda_handler(event, None)
        assert result['statusCode'] == 400
    
    def test_lambda_handler_invalid_year(self):
        """Test error handling for invalid year"""
        event = {
            "question": "What is revenue?",
            "ticker": "AAPL",
            "year": "not_a_year"
        }
        result = lambda_handler(event, None)
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'year must be a number' in body['error'].lower()
    
    @patch('lambda_3.ask_claude_question')
    @patch('lambda_3.download_sec_document')
    @patch('lambda_3.get_sec_document_url')
    def test_lambda_handler_success(self, mock_get_url, mock_download, mock_claude):
        """Test successful lambda execution"""
        # Mock all the functions
        mock_get_url.return_value = "https://test-sec-url.com"
        mock_download.return_value = "Sample SEC document content with financial data..."
        mock_claude.return_value = "Apple's revenue was $383.3 billion in fiscal 2023."
        
        event = {
            "question": "What was Apple's revenue in 2023?",
            "ticker": "AAPL",
            "year": "2023"
        }
        
        result = lambda_handler(event, None)
        
        # Check successful response
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['company'] == 'AAPL'
        assert body['year'] == 2023
        assert body['filing_type'] == 'Annual'
        assert body['model_used'] == 'Claude Sonnet 4 v1'
        assert 'Apple\'s revenue' in body['answer']
    
    @patch('lambda_3.get_sec_document_url')
    def test_lambda_handler_no_filing_found(self, mock_get_url):
        """Test handling when no SEC filing is found"""
        mock_get_url.return_value = None
        
        event = {
            "question": "What was revenue?",
            "ticker": "INVALID",
            "year": "2023"
        }
        
        result = lambda_handler(event, None)
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert 'could not find sec filing' in body['error'].lower()

# Manual test for full workflow (requires AWS credentials)
def test_full_workflow_manual():
    """
    Manual test that requires AWS credentials
    Run this separately if you want to test with real AWS services
    """
    print("=== MANUAL FULL WORKFLOW TEST ===")
    print("This test requires AWS credentials and will make real API calls")
    
    test_event = {
        "question": "What was Apple's total revenue in fiscal year 2023?",
        "ticker": "AAPL",
        "year": "2023"
    }
    
    try:
        result = lambda_handler(test_event, None)
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print("✅ SUCCESS!")
            print(f"Filing Type: {body['filing_type']}")
            print(f"Answer: {body['answer'][:200]}...")
        else:
            body = json.loads(result['body'])
            print(f"❌ ERROR: {body['error']}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    # Run pytest tests
    import subprocess
    import sys
    
    print("Running Lambda 3 tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("\n" + "="*60)
    choice = input("Run manual full workflow test? (requires AWS credentials) (y/n): ")
    if choice.lower() == 'y':
        test_full_workflow_manual()
