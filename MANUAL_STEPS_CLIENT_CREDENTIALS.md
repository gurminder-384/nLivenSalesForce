# Manual Steps for Lambda OAuth 2.0 Client Credentials Authentication

This document provides detailed step-by-step instructions for completing the remaining manual steps required to deploy the updated Lambda function with OAuth 2.0 Client Credentials authentication.

**Note:** This approach is simpler than JWT Bearer Token as it doesn't require PEM files or certificates.

---

## Step 1: Setup Salesforce Connected App

**Time Required:** 10-15 minutes

### 1.1 Create/Update Connected App

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

4. **Fill in Basic Information:**
   - **Connected App Name:** `Lambda OAuth Client Credentials` (or your preferred name)
   - **API Name:** `Lambda_OAuth_Client_Credentials` (auto-filled)
   - **Contact Email:** Your email address
   - **Enable OAuth Settings:** ✅ Check this box

5. **Configure OAuth Settings:**
   - **Callback URL:** `https://localhost` (required but not used for Client Credentials)
   - **Selected OAuth Scopes:** 
     - Move `Full access (full)` from Available to Selected
     - Move `Perform requests on your behalf at any time (refresh_token, offline_access)` to Selected
   - **Require Secret for Web Server Flow:** ✅ Check this box (to get client_secret)
   - **Enable Client Credentials Flow:** ✅ Check this if available (some orgs may not have this option)

6. **Save the Connected App:**
   - Click **Save**
   - Click **Continue** (if prompted)

7. **Note the Credentials:**
   - **Consumer Key (Client ID):** Copy this immediately - you'll need it for AWS Secrets Manager
   - **Consumer Secret (Client Secret):** 
     - Click **Click to reveal** to show the secret
     - **Copy immediately** - you can only see it once!
     - If you miss it, you'll need to reset it: Click **Reset** next to Consumer Secret

### 1.2 Verify Connected App Settings

1. **Check OAuth Policies:**
   - In the Connected App page, scroll to **OAuth Policies**
   - **Permitted Users:** Can be "All users may self-authorize" or "Admin approved users are pre-authorized"
   - **IP Relaxation:** Set as needed for your Lambda function

2. **Verify Scopes:**
   - Ensure scopes include necessary permissions for your Lambda operations
   - Common scopes needed:
     - `Full access (full)` - For full API access
     - `Perform requests on your behalf at any time (refresh_token, offline_access)` - For background operations

---

## Step 2: Setup AWS Secrets Manager

**Time Required:** 5-10 minutes

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
   - `YOUR_CONSUMER_KEY_FROM_SALESFORCE`: Paste the Consumer Key from Step 1.1
   - `YOUR_CONSUMER_SECRET_FROM_SALESFORCE`: Paste the Consumer Secret from Step 1.1
   - **Note:** For `instance_url`:
     - Production: `https://login.salesforce.com`
     - Sandbox: `https://test.salesforce.com`
     - Custom domain: Use your custom Salesforce URL

4. **Configure Secret Name:**
   - Click **Next**
   - **Secret name:** `salesforce/lambda-credentials`
   - **Description:** `Salesforce OAuth Client Credentials for Lambda function`

5. **Configure Rotation (Optional):**
   - Select **Disable automatic rotation** (recommended for Client Credentials)
   - Click **Next**

6. **Review and Store:**
   - Review all information carefully
   - Ensure `client_id` and `client_secret` are correct
   - Click **Store**

7. **Note the Secret ARN:**
   - After creation, note the ARN (Amazon Resource Name)
   - Format: `arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:salesforce/lambda-credentials-XXXXXX`

---

## Step 3: Update Lambda IAM Role Permissions

**Time Required:** 5-10 minutes

### 3.1 Locate Lambda Function

1. **Navigate to AWS Lambda Console:**
   - Go to: https://console.aws.amazon.com/lambda/
   - Find and click on your Lambda function

2. **Access Configuration:**
   - Click **Configuration** tab
   - Click **Permissions** in the left sidebar
   - Note the **Execution role** name (e.g., `lambda-execution-role`)

### 3.2 Update IAM Role

1. **Open IAM Console:**
   - Click on the **Execution role** link (opens in new tab/window)
   - OR navigate to: https://console.aws.amazon.com/iam/
   - Click **Roles** in left sidebar
   - Search for and click your Lambda execution role

2. **Add Secrets Manager Policy:**
   - Click **Add permissions** dropdown
   - Select **Attach policies**

3. **Option A: Use Managed Policy (Easier):**
   - Search for: `SecretsManagerReadWrite`
   - Check the box next to **SecretsManagerReadWrite**
   - Click **Add permissions**
   - **Note:** This grants broader access than needed, but is simpler

4. **Option B: Create Custom Policy (More Secure - Recommended):**
   - Click **Add permissions** dropdown
   - Select **Create inline policy**
   - Click **JSON** tab
   - Paste the following policy (replace `REGION` and `ACCOUNT_ID` with your values):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "secretsmanager:GetSecretValue",
           "secretsmanager:DescribeSecret"
         ],
         "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:salesforce/lambda-credentials*"
       }
     ]
   }
   ```
   - Click **Review policy**
   - **Name:** `LambdaSecretsManagerAccess`
   - Click **Create policy**

5. **Verify Permissions:**
   - Return to Lambda function
   - The role should now have Secrets Manager access

---

## Step 4: Upload Lambda Function Code

**Time Required:** 5-10 minutes

### 4.1 Package Updated Code

1. **Create deployment package:**
   ```bash
   cd /var/projects/netherlan/nLivenSalesforceSeasonPackage
   mkdir -p deploy
   cp lambda_function.py requirements.txt deploy/
   cd deploy
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt -t .
   ```

3. **Create .zip file:**
   ```bash
   zip -r ../lambda_function_client_credentials.zip . -x "*.pyc" "__pycache__/*" "*.git*" "*.zip" "*.dist-info/*"
   cd ..
   ```

4. **Verify package size:**
   ```bash
   ls -lh lambda_function_client_credentials.zip
   ```
   - Should be smaller than JWT version (no cryptography libraries)

### 4.2 Upload to AWS Lambda

**Option A: Manual Upload via Console**

1. **Navigate to Lambda Function:**
   - Go to: https://console.aws.amazon.com/lambda/
   - Click on your Lambda function name

2. **Access Code Tab:**
   - Click **Code** tab
   - You should see the current function code

3. **Upload Deployment Package:**
   - Click **Upload from** dropdown button (top right)
   - Select **.zip file**

4. **Select Zip File:**
   - Click **Upload** button
   - Navigate to: `/var/projects/netherlan/nLivenSalesforceSeasonPackage/lambda_function_client_credentials.zip`
   - Select the file
   - Click **Open**

5. **Wait for Upload:**
   - AWS will upload and extract the package
   - Wait for "Changes deployed successfully" message
   - This should be faster than JWT version (smaller file size)

**Option B: AWS CLI (Command Line)**

1. **Upload Function Code:**
   ```bash
   cd /var/projects/netherlan/nLivenSalesforceSeasonPackage
   aws lambda update-function-code \
     --function-name YOUR_FUNCTION_NAME \
     --zip-file fileb://lambda_function_client_credentials.zip \
     --region YOUR_REGION
   ```

2. **Verify Upload:**
   - Check the response for `LastUpdateStatus: Successful`
   - Or check in AWS Console that the code was updated

---

## Step 5: Update Lambda Configuration

**Time Required:** 5 minutes

### 5.1 Verify Handler Configuration

1. **In Lambda Console:**
   - Click **Configuration** tab
   - Click **General configuration**
   - Verify **Handler:** `lambda_function.lambda_handler` (should be correct)

### 5.2 Update Environment Variables

1. **Access Environment Variables:**
   - Click **Configuration** tab
   - Click **Environment variables** in left sidebar

2. **Remove Hardcoded Credentials (if any):**
   - Look for any environment variables containing Salesforce credentials
   - **DO NOT DELETE** `SecretKey` or `ShubertKey` - these are for webhook authentication
   - If you see variables like `SALESFORCE_USERNAME`, `SALESFORCE_PASSWORD`, etc., you can remove them (they're no longer needed)

3. **Keep Existing Variables:**
   - Keep `SecretKey` - used for webhook authorization
   - Keep `ShubertKey` - used for deprecated webhook authorization

### 5.3 Update Timeout (if needed)

1. **Access General Configuration:**
   - Click **Configuration** tab
   - Click **General configuration**
   - Click **Edit**

2. **Adjust Timeout:**
   - **Timeout:** Keep current setting or increase to **30 seconds** for safety
   - Client Credentials flow is typically faster than JWT
   - Click **Save**

### 5.4 Update Memory (Optional)

1. **In General Configuration:**
   - **Memory:** Keep current setting (no increase needed)
   - Client Credentials flow doesn't require significant memory
   - Click **Save**

---

## Step 6: Test Lambda Function

**Time Required:** 10-15 minutes

### 6.1 Create Test Event

1. **Navigate to Test Tab:**
   - Click **Test** tab in Lambda console

2. **Create New Test Event:**
   - Click **Create new test event** (or **Edit** if one exists)
   - Select **Create new event**
   - **Event name:** `Client-Credentials-Test`

3. **Use Sample Event:**
   - Use an existing test event from your previous setup
   - OR create a minimal test event:
   ```json
   {
     "headers": {
       "Authorization": "Bearer YOUR_SECRET_KEY"
     },
     "body": "{\"webhookType\":\"OrderCreated\",\"data\":{\"id\":\"test123\",\"customer\":{\"email\":\"test@example.com\",\"firstName\":\"Test\",\"lastName\":\"User\"},\"salesChannel\":\"Web\",\"eventId\":\"event123\",\"total\":100,\"ticketQty\":2,\"deliveryMethodName\":\"Will Call\",\"localCreated\":\"2024-01-01T12:00:00\",\"paymentMethodName\":\"Credit Card\",\"orderStatus\":\"Completed\",\"billToAddress1\":\"123 Main St\",\"billToCity\":\"New York\",\"billToPostalCode\":\"10001\",\"billToCountryCode\":\"US\",\"event\":{\"name\":\"Test Show\",\"localDate\":\"2024-01-01T20:00:00\",\"date\":\"2024-01-01T20:00:00\",\"alternateName\":\"Test Performance\",\"externalEventId\":\"EXT123\"},\"venue\":{\"name\":\"Palace Theatre\"},\"orderItems\":[]}}"
   }
   ```
   - Replace `YOUR_SECRET_KEY` with your actual `SecretKey` from environment variables

4. **Save Test Event:**
   - Click **Save**

### 6.2 Execute Test

1. **Run Test:**
   - Click **Test** button
   - Wait for execution to complete

2. **Check Execution Results:**
   - **Status:** Should show "Succeeded" (green)
   - **Response:** Should show status code 200
   - **Duration:** Note the execution time (should be similar or faster than before)

### 6.3 Review CloudWatch Logs

1. **Access Logs:**
   - Click **Monitor** tab
   - Click **View CloudWatch logs** button
   - OR click **Logs** tab

2. **Check for Success Messages:**
   - Look for: `SUCCESS: Connection to Salesforce established via OAuth Client Credentials.`
   - This confirms Client Credentials authentication worked

3. **Check for Errors:**
   - Look for any error messages
   - Common issues:
     - **"Salesforce authentication failed"**: Check Secrets Manager configuration
     - **"invalid_client"**: Verify client_id and client_secret are correct
     - **"unsupported_grant_type"**: Check if Salesforce org supports Client Credentials flow
     - **"Access denied"**: Check IAM role permissions

### 6.4 Verify Salesforce Data

1. **Check Salesforce:**
   - Log in to Salesforce
   - Navigate to the object that should have been created/updated
   - Verify the test data was processed correctly

2. **Check for Errors in Salesforce:**
   - Look for any error logs in Salesforce
   - Verify the Connected App is properly configured

---

## Step 7: Monitor and Troubleshoot

**Time Required:** Ongoing

### 7.1 Set Up CloudWatch Alarms (Optional)

1. **Navigate to CloudWatch:**
   - Go to: https://console.aws.amazon.com/cloudwatch/
   - Click **Alarms** → **All alarms**

2. **Create Alarm:**
   - Click **Create alarm**
   - Select metric: Lambda function errors
   - Set threshold: Alert if errors > 0
   - Configure SNS notification (optional)

### 7.2 Common Issues and Solutions

#### Issue: "invalid_client" error
**Solution:**
- Verify `client_id` and `client_secret` in Secrets Manager match Salesforce Connected App
- Check that Consumer Secret was copied correctly (no extra spaces or newlines)
- Ensure Connected App is active and not deleted

#### Issue: "unsupported_grant_type"
**Solution:**
- Verify `grant_type` is exactly `client_credentials` (lowercase, no spaces)
- Check if your Salesforce org supports Client Credentials flow
- May need to enable in Setup → Security → Connected App Settings
- Some Salesforce editions may not support this flow

#### Issue: "insufficient_privileges" or "access_denied"
**Solution:**
- Check Connected App OAuth scopes include necessary permissions
- Verify Connected App has access to required Salesforce objects/fields
- Check Connected App's assigned profiles/permission sets
- Ensure scopes include `Full access (full)` for full API access

#### Issue: "Access denied to Secrets Manager"
**Solution:**
- Verify IAM role has Secrets Manager permissions
- Check secret name matches exactly: `salesforce/lambda-credentials`
- Verify secret exists in the same region as Lambda function
- Check IAM policy resource ARN matches your secret ARN

#### Issue: "Token expired" or "invalid_token"
**Solution:**
- Client Credentials tokens typically expire after a period
- Lambda function should request a new token for each invocation
- Check if token caching is causing issues
- Verify `instance_url` is correct for your Salesforce org

---

## Verification Checklist

Before considering the migration complete, verify:

- [ ] Salesforce Connected App created with OAuth enabled
- [ ] Consumer Key (client_id) copied and stored
- [ ] Consumer Secret (client_secret) copied and stored securely
- [ ] AWS Secrets Manager secret created with correct JSON structure
- [ ] Lambda IAM role has Secrets Manager permissions
- [ ] Lambda function code uploaded successfully
- [ ] Environment variables cleaned up (if needed)
- [ ] Test execution successful
- [ ] CloudWatch logs show "SUCCESS: Connection to Salesforce established via OAuth Client Credentials"
- [ ] Salesforce data is being created/updated correctly
- [ ] No errors in CloudWatch logs

---

## Benefits Summary

### Advantages of Client Credentials Flow:
- ✅ **Simpler Setup:** No PEM files, certificates, or OpenSSL commands
- ✅ **Faster Implementation:** Can be set up in 10-15 minutes
- ✅ **Easier Maintenance:** Only need to manage client_id and client_secret
- ✅ **No Certificate Management:** No certificate expiration or renewal
- ✅ **Standard OAuth 2.0:** Well-supported flow
- ✅ **Smaller Deployment Package:** No cryptography libraries needed

### What Changed from JWT:
- ❌ Removed: PEM file generation
- ❌ Removed: Certificate upload to Salesforce
- ❌ Removed: PyJWT and cryptography dependencies
- ✅ Added: Simpler credential management
- ✅ Added: Faster setup process

---

## Rollback Plan (If Needed)

If you need to rollback to the previous version:

1. **Download Previous Version:**
   - In Lambda Console, go to **Versions** tab
   - Find previous version
   - OR use Git: `git checkout v1.0-baseline`

2. **Revert Code:**
   - Upload previous deployment package
   - OR restore from Git tag

3. **Restore Environment:**
   - Re-add any environment variables that were removed
   - Restore previous timeout settings

---

## Support and Documentation

- **AWS Secrets Manager Docs:** https://docs.aws.amazon.com/secretsmanager/
- **Salesforce Connected Apps:** https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm
- **OAuth 2.0 Client Credentials:** https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_client_credentials_flow.htm
- **Lambda Deployment:** https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html

---

## Notes

- **Security:** Never commit client_id or client_secret to Git
- **Backup:** Keep a backup of the original Lambda function code
- **Testing:** Test thoroughly in a development/staging environment before production
- **Monitoring:** Set up CloudWatch alarms for production deployments
- **Rotation:** Consider implementing secret rotation for production use

---

**Last Updated:** January 2024  
**Version:** 2.1-client-credentials
