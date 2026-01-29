# OAuth 2.0 Client Credentials Flow - Implementation Guide

This guide explains how to set up OAuth 2.0 Client Credentials authentication for the Lambda function. This approach is simpler than JWT Bearer Token as it doesn't require PEM files or certificates.

---

## Overview

**OAuth 2.0 Client Credentials Flow** uses only:
- `client_id` (Consumer Key from Salesforce Connected App)
- `client_secret` (Consumer Secret from Salesforce Connected App)

**No need for:**
- ❌ Private keys (PEM files)
- ❌ Certificates
- ❌ Username/password
- ❌ Security tokens

---

## Step 1: Create/Update Salesforce Connected App

### 1.1 Access Connected Apps

1. **Log in to Salesforce:**
   - Navigate to: https://login.salesforce.com (or your sandbox URL)
   - Log in with admin credentials

2. **Access Setup:**
   - Click the gear icon (⚙️) in the top right
   - Select **Setup**

3. **Navigate to Connected Apps:**
   - In the Quick Find box, type: `App Manager`
   - Click **App Manager**
   - Click **New Connected App** button (or edit existing one)

### 1.2 Configure Connected App

1. **Fill in Basic Information:**
   - **Connected App Name:** `Lambda OAuth Client Credentials` (or your preferred name)
   - **API Name:** `Lambda_OAuth_Client_Credentials` (auto-filled)
   - **Contact Email:** Your email address
   - **Enable OAuth Settings:** ✅ Check this box

2. **Configure OAuth Settings:**
   - **Callback URL:** `https://localhost` (required but not used for Client Credentials)
   - **Selected OAuth Scopes:** 
     - Move `Full access (full)` from Available to Selected
     - Move `Perform requests on your behalf at any time (refresh_token, offline_access)` to Selected
   - **Enable Client Credentials Flow:** ✅ Check this box (if available)
   - **Require Secret for Web Server Flow:** ✅ Check this box (to get client_secret)

3. **Save the Connected App:**
   - Click **Save**
   - Click **Continue** (if prompted)

4. **Note the Credentials:**
   - **Consumer Key (Client ID):** Copy this - you'll need it for AWS Secrets Manager
   - **Consumer Secret (Client Secret):** 
     - Click **Click to reveal** to show the secret
     - **Copy immediately** - you can only see it once!
     - If you miss it, you'll need to reset it

### 1.3 Important Notes

- **Client Credentials Flow** may require specific Salesforce edition or permissions
- Some Salesforce orgs may need to enable this flow in Setup → Security → Connected App Settings
- The Connected App must have appropriate OAuth scopes for the operations your Lambda performs

---

## Step 2: Setup AWS Secrets Manager

### 2.1 Create Secret

1. **Navigate to AWS Secrets Manager:**
   - Go to: https://console.aws.amazon.com/secretsmanager/
   - Click **Store a new secret**

2. **Select Secret Type:**
   - Choose **Other type of secret**
   - Select **Plaintext** tab

3. **Enter Secret JSON:**
   ```json
   {
     "client_id": "YOUR_CONSUMER_KEY_FROM_SALESFORCE",
     "client_secret": "YOUR_CONSUMER_SECRET_FROM_SALESFORCE",
     "instance_url": "https://login.salesforce.com"
   }
   ```

   **Replace placeholders:**
   - `YOUR_CONSUMER_KEY_FROM_SALESFORCE`: Paste the Consumer Key from Step 1.2
   - `YOUR_CONSUMER_SECRET_FROM_SALESFORCE`: Paste the Consumer Secret from Step 1.2
   - **Note:** For `instance_url`:
     - Production: `https://login.salesforce.com`
     - Sandbox: `https://test.salesforce.com`
     - Custom domain: Use your custom Salesforce URL

4. **Configure Secret Name:**
   - Click **Next**
   - **Secret name:** `salesforce/lambda-credentials`
   - **Description:** `Salesforce OAuth Client Credentials for Lambda function`

5. **Configure Rotation (Optional):**
   - Select **Disable automatic rotation** (recommended)
   - Click **Next**

6. **Review and Store:**
   - Review all information
   - Click **Store**

---

## Step 3: Update Lambda IAM Role Permissions

This step is the same as before - ensure your Lambda execution role has Secrets Manager read permissions.

1. **Navigate to Lambda Function:**
   - Go to: https://console.aws.amazon.com/lambda/
   - Click on your Lambda function
   - Click **Configuration** tab → **Permissions**

2. **Update IAM Role:**
   - Click on the execution role
   - Add policy: `SecretsManagerReadWrite` or create custom policy
   - Ensure access to: `arn:aws:secretsmanager:*:*:secret:salesforce/lambda-credentials*`

---

## Step 4: Code Changes Summary

The code has been updated to use Client Credentials flow:

### Updated `get_salesforce_token()` Function:

```python
def get_salesforce_token():
    """Authenticate to Salesforce using OAuth 2.0 Client Credentials flow"""
    # Get credentials from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret_response = secrets_client.get_secret_value(
        SecretId='salesforce/lambda-credentials'
    )
    credentials = json.loads(secret_response['SecretString'])
    
    # Request access token using Client Credentials grant type
    token_url = f"{credentials.get('instance_url', 'https://login.salesforce.com')}/services/oauth2/token"
    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': credentials['client_id'],
            'client_secret': credentials['client_secret']
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        return {
            'access_token': token_data['access_token'],
            'instance_url': token_data['instance_url']
        }
    else:
        logger.error(f"Salesforce authentication failed: {response.text}")
        raise Exception(f"Salesforce authentication failed: {response.status_code}")
```

### Removed Dependencies:
- ❌ `PyJWT` - No longer needed
- ❌ `cryptography` - No longer needed

### Updated requirements.txt:
```
requests==2.31.0
pytz==2023.3
uszipcode==1.0.1
boto3==1.34.0
```

---

## Step 5: Upload Updated Lambda Function

1. **Package Updated Code:**
   ```bash
   cd /var/projects/netherlan/nLivenSalesforceSeasonPackage
   mkdir -p deploy
   cp lambda_function.py requirements.txt deploy/
   cd deploy
   pip install -r requirements.txt -t .
   zip -r ../lambda_function_client_credentials.zip . -x "*.pyc" "__pycache__/*" "*.git*" "*.zip"
   ```

2. **Upload to Lambda:**
   - Via AWS Console: Upload `lambda_function_client_credentials.zip`
   - Via AWS CLI: `aws lambda update-function-code --function-name YOUR_FUNCTION --zip-file fileb://lambda_function_client_credentials.zip`

---

## Step 6: Test the Function

1. **Create Test Event:**
   - Use existing test event or create new one
   - Ensure it includes proper Authorization header

2. **Execute Test:**
   - Run the test in Lambda console
   - Check CloudWatch Logs for: `SUCCESS: Connection to Salesforce established via OAuth Client Credentials.`

3. **Verify:**
   - Check for any authentication errors
   - Verify Salesforce operations work correctly

---

## Benefits of Client Credentials Flow

### Advantages:
- ✅ **Simpler Setup:** No PEM files, certificates, or OpenSSL commands
- ✅ **Faster Implementation:** Can be set up in 10-15 minutes
- ✅ **Easier Maintenance:** Only need to manage client_id and client_secret
- ✅ **No Certificate Management:** No certificate expiration or renewal
- ✅ **Standard OAuth 2.0:** Well-supported flow

### Considerations:
- ⚠️ **Salesforce Edition:** Some editions may require specific permissions
- ⚠️ **User Context:** Client Credentials flow doesn't provide user context (uses Connected App's permissions)
- ⚠️ **Scope Limitations:** Ensure Connected App has appropriate scopes for your operations

---

## Troubleshooting

### Issue: "invalid_client" error
**Solution:**
- Verify `client_id` and `client_secret` are correct in Secrets Manager
- Check that Consumer Secret was copied correctly (no extra spaces)
- Ensure Connected App is active

### Issue: "unsupported_grant_type"
**Solution:**
- Verify `grant_type` is exactly `client_credentials` (lowercase)
- Check if your Salesforce org supports Client Credentials flow
- May need to enable in Setup → Security → Connected App Settings

### Issue: "insufficient_privileges"
**Solution:**
- Check Connected App OAuth scopes include necessary permissions
- Verify Connected App has access to required Salesforce objects/fields
- Check Connected App's assigned profiles/permission sets

### Issue: "Access denied to Secrets Manager"
**Solution:**
- Verify Lambda IAM role has Secrets Manager read permissions
- Check secret name matches exactly: `salesforce/lambda-credentials`
- Ensure secret exists in the same region as Lambda function

---

## Comparison: Client Credentials vs JWT vs Username-Password

| Feature | Client Credentials | JWT Bearer Token | Username-Password |
|---------|-------------------|------------------|-------------------|
| **Setup Complexity** | Low | High | Medium |
| **PEM Files** | ❌ No | ✅ Yes | ❌ No |
| **Certificates** | ❌ No | ✅ Yes | ❌ No |
| **Client Secret** | ✅ Required | ❌ No | ✅ Required |
| **Username/Password** | ❌ No | ✅ Yes (in JWT) | ✅ Yes |
| **Security Token** | ❌ No | ❌ No | ✅ Required |
| **Setup Time** | 10-15 min | 20-30 min | 10-15 min |
| **Security** | High | Highest | Medium |
| **User Context** | App-level | User-level | User-level |

---

## Security Best Practices

1. ✅ **Store credentials in AWS Secrets Manager** - Never in code
2. ✅ **Rotate client_secret periodically** - Update in Salesforce and Secrets Manager
3. ✅ **Use least privilege** - Grant only necessary OAuth scopes
4. ✅ **Monitor access** - Review CloudWatch logs regularly
5. ✅ **Use HTTPS** - All communication is encrypted
6. ✅ **Restrict IP ranges** - Configure in Salesforce if possible

---

## Next Steps

1. ✅ Create/Update Salesforce Connected App
2. ✅ Store credentials in AWS Secrets Manager
3. ✅ Update Lambda IAM role permissions
4. ✅ Upload updated Lambda function code
5. ✅ Test the function
6. ✅ Monitor CloudWatch logs

---

**Last Updated:** January 2024  
**Version:** 2.1-client-credentials
