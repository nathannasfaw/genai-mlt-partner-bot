import boto3
import requests

'''
This function will download the SEC Edgar JSON files, 
which are used by the SEC Module to create dictionaries 
for finding company CIKs based on their name or their stock ticker. 
The Lambda function will then upload these JSON files to an S3 bucket. 
This Lambda function should be scheduled to run daily and update the same S3 locations. 
The S3 bucket should have version history enabled.'''

# This Lambda function will be responsible for downloading the SEC Edgar JSON files and uploading them to an S3 bucket.
def lambda_handler(event, context):
    
    
    s3 = boto3.client('s3')