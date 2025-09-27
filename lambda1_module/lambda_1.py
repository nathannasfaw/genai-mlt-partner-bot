import boto3
import requests
import json

'''
This function will download the SEC Edgar JSON files, 
which are used by the SEC Module to create dictionaries 
for finding company CIKs based on their name or their stock ticker. 
The Lambda function will then upload these JSON files to an S3 bucket. 
This Lambda function should be scheduled to run daily and update the same S3 locations. 
The S3 bucket should have version history enabled.'''

# This Lambda function will be responsible for downloading the SEC Edgar JSON files and uploading them to an S3 bucket.
def lambda_handler(event, context):
    
    # Making an s3 client
    s3 = boto3.client('s3')

    bucket_name = 'nathanasfaw-sec-edgar-files'
    # URLs for the SEC Edgar JSON files
    url = "https://www.sec.gov/files/company_tickers.json"
    # Headers for SEC requests
    headers = { 'User-Agent': 'MLT CP nathanrasfaw@gmail.com'}

    try:
        print(f'Fetching data from {url}')

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        print('Data fetched successfully. Uploading to S3...')

        # Uploading the JSON file to S3 
        s3.put_object(Bucket=bucket_name, Key='company_tickers.json', Body=response.content)
        print('Upload to S3 successful')
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Upload successful'})
        }

    except Exception as e:
        # Handle S3 or other errors
        error_message = f"Error uploading to S3: {str(e)}"
        print(error_message)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Upload failed',
                'message': error_message
            })
        }