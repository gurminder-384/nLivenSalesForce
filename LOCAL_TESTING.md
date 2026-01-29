# Local Testing Guide for Lambda Function

This guide explains how to test your Lambda function locally before deploying to AWS. This helps catch issues early and speeds up development.

---

## Prerequisites

1. **Python 3.8+** installed
2. **pip** package manager
3. **AWS credentials** configured (for Secrets Manager access, or use mocks)
4. **Virtual environment** (recommended)

---

## Step 1: Setup Local Environment

### 1.1 Create Virtual Environment

```bash
cd /var/projects/netherlan/nLivenSalesforceSeasonPackage

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install additional testing tools (optional but recommended)
pip install moto boto3-stubs pytest
```

---

## Step 2: Setup Local Testing Structure

### 2.1 Create Test Directory

```bash
mkdir -p tests
cd tests
```

### 2.2 Create Test Event File

Create `test_event.json`:

```json
{
  "headers": {
    "Authorization": "Bearer YOUR_SECRET_KEY"
  },
  "body": "{\"webhookType\":\"OrderCreated\",\"data\":{\"id\":\"test123\",\"customer\":{\"email\":\"test@example.com\",\"firstName\":\"Test\",\"lastName\":\"User\"},\"salesChannel\":\"Web\",\"eventId\":\"event123\",\"total\":100,\"ticketQty\":2,\"deliveryMethodName\":\"Will Call\",\"localCreated\":\"2024-01-01T12:00:00\",\"paymentMethodName\":\"Credit Card\",\"orderStatus\":\"Completed\",\"billToAddress1\":\"123 Main St\",\"billToCity\":\"New York\",\"billToPostalCode\":\"10001\",\"billToCountryCode\":\"US\",\"event\":{\"name\":\"Test Show\",\"localDate\":\"2024-01-01T20:00:00\",\"date\":\"2024-01-01T20:00:00\",\"alternateName\":\"Test Performance\",\"externalEventId\":\"EXT123\"},\"venue\":{\"name\":\"Palace Theatre\"},\"orderItems\":[]}}"
}
```

**Replace `YOUR_SECRET_KEY`** with your actual SecretKey value.

### 2.3 Create Mock Context

Create `mock_context.py`:

```python
class MockContext:
    """Mock AWS Lambda context object"""
    def __init__(self):
        self.function_name = "test-lambda-function"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-lambda-function"
        self.memory_limit_in_mb = 128
        self.aws_request_id = "test-request-id"
        self.log_group_name = "/aws/lambda/test-lambda-function"
        self.log_stream_name = "2024/01/01/[$LATEST]test-stream"
        self.remaining_time_in_millis = lambda: 30000
```

---

## Step 3: Mock AWS Secrets Manager

Since you can't access real Secrets Manager locally, you have two options:

### Option A: Use Real AWS Secrets Manager (Requires AWS Credentials)

If you have AWS credentials configured:

```bash
# Configure AWS credentials
aws configure

# Set environment variable for region
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
```

Then your function will use real Secrets Manager (make sure the secret exists).

### Option B: Mock Secrets Manager (Recommended for Testing)

Create `test_local.py` with mocked Secrets Manager:

```python
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path to import lambda_function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda_function import lambda_handler
from mock_context import MockContext

# Mock credentials (use your actual test values)
MOCK_CREDENTIALS = {
    'client_id': 'YOUR_TEST_CLIENT_ID',
    'client_secret': 'YOUR_TEST_CLIENT_SECRET',
    'instance_url': 'https://test.salesforce.com'  # or https://login.salesforce.com
}

def mock_get_secret_value(SecretId):
    """Mock Secrets Manager get_secret_value response"""
    if SecretId == 'salesforce/lambda-credentials':
        return {
            'SecretString': json.dumps(MOCK_CREDENTIALS)
        }
    raise Exception(f"Secret {SecretId} not found")

def test_lambda_locally():
    """Test Lambda function locally with mocked Secrets Manager"""
    
    # Load test event
    with open('test_event.json', 'r') as f:
        test_event = json.load(f)
    
    # Set environment variables
    os.environ['SecretKey'] = 'YOUR_SECRET_KEY'  # Replace with actual key
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Mock Secrets Manager
    with patch('boto3.client') as mock_boto_client:
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value = MagicMock(side_effect=mock_get_secret_value)
        mock_boto_client.return_value = mock_secrets_client
        
        # Create mock context
        context = MockContext()
        
        # Invoke Lambda handler
        try:
            response = lambda_handler(test_event, context)
            print("\n✅ Lambda execution successful!")
            print(f"Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"\n❌ Lambda execution failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_lambda_locally()
```

**Update the mock credentials** with your test values.

---

## Step 4: Run Local Tests

### 4.1 Simple Test Script

Create `run_local_test.py` in the project root:

```python
#!/usr/bin/env python3
"""
Local testing script for Lambda function
"""
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Set up environment
os.environ['SecretKey'] = 'YOUR_SECRET_KEY'  # Replace with actual key
os.environ['AWS_REGION'] = 'us-east-1'

# Mock credentials
MOCK_CREDENTIALS = {
    'client_id': 'YOUR_TEST_CLIENT_ID',
    'client_secret': 'YOUR_TEST_CLIENT_SECRET',
    'instance_url': 'https://test.salesforce.com'
}

# Mock context
class MockContext:
    function_name = "test-lambda"
    function_version = "$LATEST"
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-lambda"
    memory_limit_in_mb = 128
    aws_request_id = "test-request-id"
    log_group_name = "/aws/lambda/test-lambda"
    log_stream_name = "test-stream"
    def get_remaining_time_in_millis(self):
        return 30000

def main():
    # Import lambda function
    from lambda_function import lambda_handler
    
    # Load test event
    test_event_path = 'tests/test_event.json'
    if not os.path.exists(test_event_path):
        print(f"❌ Test event file not found: {test_event_path}")
        sys.exit(1)
    
    with open(test_event_path, 'r') as f:
        test_event = json.load(f)
    
    # Mock Secrets Manager
    def mock_get_secret_value(SecretId):
        if SecretId == 'salesforce/lambda-credentials':
            return {'SecretString': json.dumps(MOCK_CREDENTIALS)}
        raise Exception(f"Secret {SecretId} not found")
    
    with patch('boto3.session.Session') as mock_session:
        mock_client = MagicMock()
        mock_client.get_secret_value = MagicMock(side_effect=mock_get_secret_value)
        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        
        # Create context
        context = MockContext()
        
        print("🚀 Starting local Lambda test...")
        print(f"📋 Test event: {json.dumps(test_event, indent=2)[:200]}...")
        print("\n" + "="*50)
        
        try:
            response = lambda_handler(test_event, context)
            print("\n✅ SUCCESS!")
            print(f"📤 Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
```

### 4.2 Run the Test

```bash
# Make script executable
chmod +x run_local_test.py

# Run the test
python3 run_local_test.py
```

---

## Step 5: Test with Real AWS Services (Optional)

If you want to test with real AWS Secrets Manager:

### 5.1 Configure AWS Credentials

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (json)
```

### 5.2 Set Environment Variables

```bash
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export SecretKey=YOUR_SECRET_KEY
```

### 5.3 Run Direct Test

Create `test_real_aws.py`:

```python
#!/usr/bin/env python3
import json
import os
import sys

# Set environment variables
os.environ['SecretKey'] = 'YOUR_SECRET_KEY'
os.environ['AWS_REGION'] = 'us-east-1'

# Import and run
from lambda_function import lambda_handler

class MockContext:
    function_name = "test-lambda"
    function_version = "$LATEST"
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-lambda"
    memory_limit_in_mb = 128
    aws_request_id = "test-request-id"
    log_group_name = "/aws/lambda/test-lambda"
    log_stream_name = "test-stream"
    def get_remaining_time_in_millis(self):
        return 30000

# Load test event
with open('tests/test_event.json', 'r') as f:
    test_event = json.load(f)

context = MockContext()

print("🚀 Testing with real AWS Secrets Manager...")
try:
    response = lambda_handler(test_event, context)
    print("✅ SUCCESS!")
    print(json.dumps(response, indent=2))
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
```

---

## Step 6: Advanced Testing with pytest

### 6.1 Install pytest

```bash
pip install pytest pytest-mock
```

### 6.2 Create Test File

Create `tests/test_lambda_function.py`:

```python
import pytest
import json
import os
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lambda_function import lambda_handler, get_salesforce_token

class MockContext:
    function_name = "test-lambda"
    function_version = "$LATEST"
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-lambda"
    memory_limit_in_mb = 128
    aws_request_id = "test-request-id"
    log_group_name = "/aws/lambda/test-lambda"
    log_stream_name = "test-stream"
    def get_remaining_time_in_millis(self):
        return 30000

@pytest.fixture
def test_event():
    """Load test event from file"""
    with open('tests/test_event.json', 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_context():
    """Create mock context"""
    return MockContext()

@pytest.fixture
def mock_credentials():
    """Mock Salesforce credentials"""
    return {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'instance_url': 'https://test.salesforce.com'
    }

@pytest.fixture
def mock_secrets_manager(mock_credentials):
    """Mock Secrets Manager"""
    with patch('boto3.session.Session') as mock_session:
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_credentials)
        }
        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        yield mock_client

def test_get_salesforce_token(mock_secrets_manager, mock_credentials):
    """Test get_salesforce_token function"""
    # Mock Salesforce OAuth response
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'instance_url': 'https://test.salesforce.com'
        }
        mock_post.return_value = mock_response
        
        result = get_salesforce_token()
        
        assert result['access_token'] == 'test_access_token'
        assert result['instance_url'] == 'https://test.salesforce.com'

def test_lambda_handler_success(test_event, mock_context, mock_secrets_manager):
    """Test successful Lambda execution"""
    os.environ['SecretKey'] = 'test_secret_key'
    
    # Mock Salesforce API calls
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Mock OAuth token response
        oauth_response = MagicMock()
        oauth_response.status_code = 200
        oauth_response.json.return_value = {
            'access_token': 'test_token',
            'instance_url': 'https://test.salesforce.com'
        }
        mock_post.return_value = oauth_response
        
        # Mock Salesforce query responses
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.json.return_value = {
            'totalSize': 0,
            'records': []
        }
        mock_get.return_value = query_response
        
        # Update test event with correct authorization
        test_event['headers']['Authorization'] = 'Bearer test_secret_key'
        
        response = lambda_handler(test_event, mock_context)
        
        assert response['statusCode'] == '200'

def test_lambda_handler_auth_failure(test_event, mock_context):
    """Test Lambda execution with invalid authorization"""
    os.environ['SecretKey'] = 'correct_key'
    test_event['headers']['Authorization'] = 'Bearer wrong_key'
    
    response = lambda_handler(test_event, mock_context)
    
    assert response['statusCode'] == '200'  # Function still returns 200, but logs error
```

### 6.3 Run pytest Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_lambda_function.py::test_get_salesforce_token -v
```

---

## Step 7: Testing Different Webhook Types

### 7.1 Create Multiple Test Events

Create different test event files:

**`tests/test_order_created.json`:**
```json
{
  "headers": {
    "Authorization": "Bearer YOUR_SECRET_KEY"
  },
  "body": "{\"webhookType\":\"OrderCreated\",\"data\":{...}}"
}
```

**`tests/test_order_updated.json`:**
```json
{
  "headers": {
    "Authorization": "Bearer YOUR_SECRET_KEY"
  },
  "body": "{\"webhookType\":\"OrderUpdated\",\"data\":{...}}"
}
```

### 7.2 Test Each Webhook Type

```bash
# Test OrderCreated
python3 -c "
import json, sys, os
sys.path.insert(0, '.')
os.environ['SecretKey'] = 'YOUR_SECRET_KEY'
from lambda_function import lambda_handler
with open('tests/test_order_created.json') as f:
    event = json.load(f)
    print(lambda_handler(event, None))
"
```

---

## Step 8: Debugging Tips

### 8.1 Enable Verbose Logging

Add to your test script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 8.2 Print Intermediate Values

Modify `lambda_function.py` temporarily for debugging:

```python
def get_salesforce_token():
    # ... existing code ...
    logger.info(f"DEBUG: Retrieved credentials: {credentials}")
    logger.info(f"DEBUG: Token URL: {token_url}")
    # ... rest of code ...
```

### 8.3 Use Python Debugger

```python
import pdb

def get_salesforce_token():
    pdb.set_trace()  # Breakpoint here
    # ... rest of code ...
```

Then run:
```bash
python3 run_local_test.py
```

---

## Step 9: Quick Test Script

Create a simple one-liner test script `quick_test.sh`:

```bash
#!/bin/bash

# Set environment
export SecretKey="YOUR_SECRET_KEY"
export AWS_REGION="us-east-1"

# Run test
python3 -c "
import json, sys, os
sys.path.insert(0, '.')
os.environ['SecretKey'] = os.environ.get('SecretKey')
os.environ['AWS_REGION'] = os.environ.get('AWS_REGION')

from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler

# Mock Secrets Manager
with patch('boto3.session.Session') as mock_session:
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        'SecretString': '{\"client_id\":\"test\",\"client_secret\":\"test\",\"instance_url\":\"https://test.salesforce.com\"}'
    }
    mock_session_instance = MagicMock()
    mock_session_instance.client.return_value = mock_client
    mock_session.return_value = mock_session_instance
    
    # Mock context
    class MockContext:
        function_name = 'test'
        def get_remaining_time_in_millis(self): return 30000
    
    # Load and run test event
    with open('tests/test_event.json') as f:
        event = json.load(f)
    
    try:
        result = lambda_handler(event, MockContext())
        print('✅ SUCCESS')
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f'❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
"
```

Make executable and run:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

## Step 10: Common Local Testing Issues

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: AWS Credentials Not Found

**Solution:**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Issue: Secrets Manager Access Denied

**Solution:**
- Use mocked Secrets Manager (Option B above)
- Or ensure your AWS credentials have Secrets Manager permissions

### Issue: Salesforce Authentication Fails

**Solution:**
- Use test/sandbox Salesforce credentials
- Verify mock credentials are correct
- Check Salesforce Connected App is active

---

## Summary

**Quick Start:**
1. Create virtual environment: `python3 -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Create test event: `tests/test_event.json`
4. Run test: `python3 run_local_test.py`

**Best Practices:**
- ✅ Use virtual environments
- ✅ Mock AWS services for faster testing
- ✅ Test different webhook types
- ✅ Use pytest for structured testing
- ✅ Test error scenarios
- ✅ Verify logging output

---

**Last Updated:** January 2024
