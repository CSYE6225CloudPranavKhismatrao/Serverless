# Canvas Submission Lambda Function

This AWS Lambda function is designed to be triggered by an SNS notification. It performs the following tasks:

1. Extracts submission details (status, submission URL, user email, assignment ID) from the SNS message.
2. Downloads the submission from the provided URL.
3. Uploads the submission to a Google Cloud Storage bucket.
4. Sends a success email to the user and updates DynamoDB.
5. If an error occurs, it sends an error email to the user.

## Environment Variables

Make sure to set the following environment variables in your AWS Lambda environment:

- `GOOGLE_CREDENTIALS`: Base64-encoded Google Cloud credentials JSON.
- `GCP_BUCKET_NAME`: Google Cloud Storage bucket name.
- `FROM_ADDRESS`: Source email address for sending emails.
- `DYNAMO_TABLE_NAME`: DynamoDB table name.

## Dependencies

Ensure that the Lambda function has access to the necessary dependencies:

- `google-cloud-storage`: Google Cloud Storage library.
- `boto3`: AWS SDK for Python.
- `requests`: HTTP library.

## Usage

This Lambda function is designed to be triggered by an SNS notification. When the function is invoked, it processes the submission details and performs the specified actions.

Note: Ensure that the Lambda function has the necessary IAM roles and permissions to access AWS SNS, Google Cloud Storage, and DynamoDB.

Feel free to modify and adapt the code to suit your specific requirements.# Serverless
