import datetime
import json
import logging
import os
import base64
import requests
from google.cloud import storage
from google.oauth2 import service_account
import boto3


# import requests

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Extract submission URL and user email from the SNS message
    message_str = event['Records'][0]['Sns']['Message']
    logger.info("message_str: %s", message_str)

    # Parse the message string as JSON
    message = json.loads(message_str)
    # message = message_str
    logger.info("message: %s", message)

    # Extract submission_url and user_email
    status = message['status']
    submission_url = message['submissionUrl']
    user_email = message['userEmail']
    assignment_id = message['assignmentId']
    logger.info("submission_url: %s", submission_url)
    logger.info("user_email: %s", user_email)
    logger.info("assignment_id: %s", assignment_id)

    # Download the submission from the submission_url
    response = requests.get(submission_url)
    # logger.info("response: %s", response)

    google_creds_base64 = os.environ['GOOGLE_CREDENTIALS']
    # google_creds_json = google_creds_base64
    # logger.
    google_creds_json = base64.b64decode(google_creds_base64).decode('utf-8')
    logger.info("google_creds_json: %s", google_creds_base64)

    try:
        # Parse the JSON string into a dictionary
        google_creds = json.loads(google_creds_json)
    except json.JSONDecodeError as e:
        print("Error parsing JSON: ", e)
        logger.info("Error " + e)
        print("JSON string: ", google_creds_json)
        # logger.info("GOOGLE_CREDENTIALS: JSON " + google_creds_json)
        raise e

    # Google Cloud authentication
    credentials = service_account.Credentials.from_service_account_info(google_creds)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.environ['GCP_BUCKET_NAME'])
    # logger.info("GCP_BUCKET_NAME: " + os.environ['GCP_BUCKET_NAME'])
    source_email = os.environ.get('FROM_ADDRESS')
    # logger.info("source_email : %s", source_email)

    try:
        if status == "SUCCESS":
            response = requests.get(submission_url)
            file_content = response.content
            if response.status_code != 200 or not file_content:
                raise ValueError("Invalid URL or empty content")

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            directory_path = f"{user_email}/{assignment_id}/"
            unique_file_name = f"submission_{timestamp}.zip"
            full_path = directory_path + unique_file_name
            blob = bucket.blob(full_path)
            blob.upload_from_string(file_content)
            logger.info("full_path : %s", full_path)

            logger.info("Sending Email")
            # Send success email
            send_email(user_email, submission_url, assignment_id, source_email, "Assignment Successfull Submission Confirmation",
                       f"Congratulations. This is an automated confirmation to inform you that your assignment with the ID {assignment_id} has been successfully submitted. The details of your submission are as "
                       "follows:")

            logger.info("Email Sent and updating dynamo DB")
            # Update DynamoDB
            update_dynamodb(user_email, assignment_id, submission_url, full_path, timestamp)

            logger.info("Table updated")
        else:
            raise ValueError("Non-success status received")

    except Exception as e:
        logger.error(f"Error in processing submission: {e}")
        send_email(user_email, submission_url, assignment_id, source_email, "Assignment Failed Submission Confirmation",
                   "There was an error with your submission. Please ensure the URL is correct and the content is not empty.")


def send_email(user_email, submission_url, assignment_id, source_email, subject, body):
    print("Sending email ", user_email, submission_url, assignment_id, source_email, subject, body)
    # Mailgun parameters
    logger = logging.getLogger()
    api_key = // Your Mailgun API Key
    to_address = user_email

    email_body = (f"\n"
                  f"    Dear {user_email},\n"
                  f"    {body}\n"
                  f"    - Assignment ID: {assignment_id}\n"
                  f"    - Submission URL: {submission_url}\n"
                  f"     \n"
                  f"    Your submission is now in our system, and our team will proceed with the evaluation process. You will receive further notifications regarding the results as soon as they are "
                  f"available.\n"
                  f" \n"
                  f"If you encounter any issues or have questions related to your submission, please contact us at info@pranavkhismatrao.me.\n"
                  f"Thank you for your prompt and diligent submission.\n"
                  f" \n"
                  f"    Best regards,\n"
                  f"    The Canvas Team\n"
                  f"    ").format(user_email=user_email, submission_url=submission_url, assignment_id=assignment_id)
    # Mailgun API endpoint
    url = "https://api.mailgun.net/v3/demo.pranavkhismatrao.me/messages"

    # Mailgun API key
    auth = ("api", api_key)

    # Email parameters
    data = {
        "from": "mailgun <noreply@pranavkhismatrao.me>",
        "to": to_address,
        "subject": subject,
        "text": email_body
    }

    #     Send mail using Mailgun
    try:
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        logger.info("Email sent successfully!")
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def update_dynamodb(user_email, assignment_id, submission_url, full_path, timestamp):
    table_name = os.environ.get('DYNAMO_TABLE_NAME')
    Id = f"{user_email}#{assignment_id}#{timestamp}"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'id': Id,
            'AssignmentId': assignment_id,
            'SubmissionUrl': submission_url,
            'FilePath': full_path,
            'Timestamp':  timestamp
        }
    )


# lambda_handler("https://github.com/tparikh/myrepo/archive/refs/tags/v1.0.0.zip")
