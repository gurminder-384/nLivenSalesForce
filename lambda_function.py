"""
AWS Lambda Middleware Function for Salesforce Webhook Proxy

This Lambda function acts as a middleware/proxy that:
1. Authenticates to Salesforce using OAuth 2.0 Client Credentials flow
2. Forwards incoming requests to Salesforce Apex REST endpoint
3. Returns the Salesforce response to the caller
4. Supports multiple environments (dev, qa, uat, production)
"""

import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Token cache to avoid unnecessary OAuth calls
# Structure: {environment: {'token': str, 'expires_at': datetime, 'instance_url': str}}
_token_cache = {}


def get_salesforce_token(environment='production'):
    """
    Authenticate to Salesforce using OAuth 2.0 Client Credentials flow
    
    Args:
        environment: 'dev', 'qa', 'uat', or 'production' - determines which credentials to use
    
    Returns:
        dict: Contains 'access_token' and 'instance_url'
    """
    # Check if we have a valid cached token for this environment
    if environment in _token_cache:
        cache_entry = _token_cache[environment]
        if cache_entry.get('token') and cache_entry.get('expires_at'):
            if datetime.utcnow() < cache_entry['expires_at']:
                logger.info(f"Using cached token for {environment} environment")
                return {
                    'access_token': cache_entry['token'],
                    'instance_url': cache_entry['instance_url']
                }
    
    # Determine secret name based on environment
    secret_name = f"liventus/salesforce/lambda-credentials-{environment}"
    
    # Get region from Lambda environment or default to us-east-1
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Create a Secrets Manager client with explicit region
    session = boto3.session.Session()
    secrets_client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        # Get credentials from Secrets Manager
        secret_response = secrets_client.get_secret_value(
            SecretId=secret_name
        )
        credentials = json.loads(secret_response['SecretString'])
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.error(f"ERROR: Secret '{secret_name}' not found. Available environments: dev, qa, uat, production")
            raise Exception(f"Secret '{secret_name}' not found in region '{region_name}'. Please create the secret for the {environment} environment.")
        else:
            logger.error(f"ERROR: Failed to retrieve secret '{secret_name}': {error_code} - {str(e)}")
            raise
    
    # Determine base URL based on environment
    # Non-production environments (dev, qa, uat) typically use test.salesforce.com
    if environment in ['dev', 'qa', 'uat']:
        base_url = credentials.get('instance_url', 'https://test.salesforce.com')
    else:
        # Production uses login.salesforce.com
        base_url = credentials.get('instance_url', 'https://login.salesforce.com')
    
    # Request access token using Client Credentials grant type
    token_url = f"{base_url}/services/oauth2/token"
    
    try:
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret']
            },
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Cache the token (typically expires in 2 hours, cache for 1.5 hours to be safe)
            _token_cache[environment] = {
                'token': token_data['access_token'],
                'instance_url': token_data['instance_url'],
                'expires_at': datetime.utcnow() + timedelta(hours=1, minutes=30)
            }
            
            logger.info(f'SUCCESS: OAuth token obtained for {environment} environment')
            return {
                'access_token': token_data['access_token'],
                'instance_url': token_data['instance_url']
            }
        else:
            logger.error(f"Salesforce OAuth failed: Status {response.status_code}, Response: {response.text}")
            raise Exception(f"Salesforce OAuth authentication failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during OAuth token request: {str(e)}")
        raise Exception(f"Failed to connect to Salesforce OAuth endpoint: {str(e)}")


def proxy_to_salesforce(event, environment='production'):
    """
    Proxy incoming request to Salesforce Apex REST endpoint
    
    Args:
        event: Lambda event containing the request
        environment: Environment to use ('dev', 'qa', 'uat', 'production')
    
    Returns:
        dict: Response from Salesforce
    """
    # Get OAuth token
    token_info = get_salesforce_token(environment)
    access_token = token_info['access_token']
    instance_url = token_info['instance_url']
    
    # Construct Salesforce endpoint URL
    salesforce_endpoint = f"{instance_url}/services/apexrest/webhook/seasonPackage"
    
    # Extract request body from Lambda event
    request_body = event.get('body', '{}')
    
    # If body is a string, parse it
    if isinstance(request_body, str):
        try:
            request_body = json.loads(request_body)
        except json.JSONDecodeError:
            # If not JSON, keep as string
            pass
    
    # Extract headers from event (excluding Lambda-specific headers)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add any custom headers from the original request (optional)
    if 'headers' in event:
        # Forward relevant headers (you can customize this list)
        forwarded_headers = ['X-Request-ID', 'X-Correlation-ID', 'User-Agent']
        for header_name in forwarded_headers:
            if header_name in event['headers']:
                headers[header_name] = event['headers'][header_name]
    
    # Make POST request to Salesforce
    try:
        logger.info(f"Proxying request to Salesforce: {salesforce_endpoint}")
        logger.info(f"Request body: {json.dumps(request_body)[:500]}...")  # Log first 500 chars
        
        response = requests.post(
            salesforce_endpoint,
            json=request_body if isinstance(request_body, dict) else None,
            data=request_body if isinstance(request_body, str) else None,
            headers=headers,
            timeout=30
        )
        
        # Log response details
        logger.info(f"Salesforce response status: {response.status_code}")
        logger.info(f"Salesforce response headers: {dict(response.headers)}")
        
        # Return response
        try:
            response_body = response.json()
        except json.JSONDecodeError:
            # If response is not JSON, return as text
            response_body = response.text
        
        return {
            'statusCode': response.status_code,
            'body': json.dumps(response_body) if isinstance(response_body, dict) else response_body,
            'headers': {
                'Content-Type': response.headers.get('Content-Type', 'application/json'),
                'X-Salesforce-Response': 'true'
            }
        }
        
    except requests.exceptions.Timeout:
        logger.error("Request to Salesforce timed out")
        return {
            'statusCode': 504,
            'body': json.dumps({'error': 'Gateway Timeout', 'message': 'Salesforce request timed out'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying to Salesforce: {str(e)}")
        return {
            'statusCode': 502,
            'body': json.dumps({'error': 'Bad Gateway', 'message': f'Failed to connect to Salesforce: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event containing request data
        context: Lambda context object
    
    Returns:
        dict: HTTP response with statusCode, body, and headers
    """
    logger.info('Lambda middleware handler called')
    logger.info(f"Event: {json.dumps(event)[:500]}...")  # Log first 500 chars
    
    try:
        # Determine environment from event or environment variable
        # Priority: 1. Event header/query param, 2. Environment variable, 3. Default to production
        environment = 'production'
        
        # Check for environment in query string parameters
        if 'queryStringParameters' in event and event['queryStringParameters']:
            environment = event['queryStringParameters'].get('env', environment)
        
        # Check for environment in headers
        if 'headers' in event and event['headers']:
            # Headers are often lowercase in API Gateway
            env_header = event['headers'].get('X-Environment') or event['headers'].get('x-environment')
            if env_header:
                environment = env_header
        
        # Check environment variable as fallback
        environment = os.environ.get('SALESFORCE_ENVIRONMENT', environment)
        
        # Validate environment
        valid_environments = ['dev', 'qa', 'uat', 'production']
        if environment not in valid_environments:
            logger.warning(f"Invalid environment '{environment}', defaulting to 'production'. Valid environments: {', '.join(valid_environments)}")
            environment = 'production'
        
        logger.info(f"Using Salesforce environment: {environment}")
        
        # Proxy request to Salesforce
        response = proxy_to_salesforce(event, environment)
        
        logger.info(f"Returning response with status code: {response['statusCode']}")
        return response
        
    except Exception as e:
        logger.error(f"ERROR in lambda_handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
