from flask import Flask, request, jsonify
import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import mimetypes
import os
import tempfile
import uuid
import smtplib
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def log_message(task_id, message):
    """Simple logging function to replace the original conductor logger"""
    logging.info(f"Task {task_id}: {message}")

def package_to_eml(input_data):
    """
    Function to package email data into an EML file.
    Expects input_data: case_id, email_body, attachments (list),
    sender_email (optional), recipient_email (optional),
    email_subject (optional)
    Returns: dict with status, output_data, and logs
    """
    task_id = str(uuid.uuid4())[:8]  # Generate a short task ID
    log_message(task_id, f"Starting package_to_eml for task: {task_id}")

    try:
        # --- 1. Extract Input Parameters ---
        case_id = input_data.get('case_id')
        email_body = input_data.get('email_body', '')  # Default to empty string
        attachments_data = input_data.get('attachments', [])  # Default to empty list
        sender = input_data.get('sender_email', 'sender@example.com')
        recipient = input_data.get('recipient_email', 'recipient@example.com')
        subject = input_data.get('email_subject', f'Packaged Email for Case {case_id}')

        if not case_id:
            raise ValueError("Missing required input parameter: case_id")
        if not isinstance(attachments_data, list):
            raise ValueError("Attachments parameter must be a list")

        log_message(task_id, f"Processing Case ID: {case_id}")
        log_message(task_id, f"Number of attachments received: {len(attachments_data)}")

        # --- 2. Create the Email Message Structure ---
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        # Attach the body (assuming plain text, use 'html' if body is HTML)
        body_type = input_data.get('body_type', 'plain')  # Allow HTML bodies
        msg.attach(MIMEText(email_body, body_type))
        log_message(task_id, "Attached email body.")

        # --- 3. Process and Attach Attachments ---
        for i, attachment in enumerate(attachments_data):
            filename = attachment.get('filenames')  # Fixed typo from 'filenames'
            # *** Assuming attachment_data is Base64 encoded string ***
            base64_data = attachment.get('attachment_data')

            if not filename or not base64_data:
                logging.warning(f"Skipping attachment {i} due to missing filename or data for task {task_id}")
                continue

            try:
                # Decode Base64 data to bytes
                attachment_bytes = base64.b64decode(base64_data)

                # Guess the MIME type
                ctype, encoding = mimetypes.guess_type(filename)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'  # Default if guess fails
                maintype, subtype = ctype.split('/', 1)

                # Create the attachment part
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment_bytes)
                encoders.encode_base64(part)  # EML standard needs base64 encoding
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)
                log_message(task_id, f"Attached file: {filename}")

            except (TypeError, ValueError) as decode_err:
                logging.error(f"Error decoding or processing attachment '{filename}' for task {task_id}: {decode_err}")
                continue  # Skip this attachment and continue
            except Exception as attach_err:
                logging.error(f"Unexpected error attaching file '{filename}' for task {task_id}: {attach_err}")
                raise  # Re-raise unexpected errors

        # --- 4. Generate Unique Filename and Save EML ---
        temp_dir = tempfile.gettempdir()  # Get system temp directory
        unique_filename = f"{case_id}_{uuid.uuid4()}.eml"
        output_path = os.path.join(temp_dir, unique_filename)

        log_message(task_id, f"Attempting to save EML file to: {output_path}")
        with open(output_path, 'wb') as f:  # Use 'wb' (write binary) as msg.as_bytes() returns bytes
            f.write(msg.as_bytes())

        log_message(task_id, f"Successfully created EML file: {output_path} for task {task_id}")

        # --- 4.1. Send Notification Email (Optional) ---
        send_notification = input_data.get('send_notification', False)
        if send_notification:
            try:
                smtp_config = input_data.get('smtp_config', {})
                smtp_server = smtp_config.get('server', 'smtp.gmail.com')
                smtp_port = smtp_config.get('port', 587)
                smtp_username = smtp_config.get('username', 'your-email@gmail.com')
                smtp_password = smtp_config.get('password', 'your-app-password')
                notification_recipient = smtp_config.get('notification_recipient', smtp_username)

                notification_subject = f"Task {task_id} Completed"
                notification_body = f"The EML file for Case ID {case_id} has been successfully created at {output_path}."

                notification_msg = MIMEText(notification_body, 'plain')
                notification_msg['Subject'] = notification_subject
                notification_msg['From'] = smtp_username
                notification_msg['To'] = notification_recipient

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()  # Upgrade the connection to secure
                    server.login(smtp_username, smtp_password)
                    server.sendmail(smtp_username, notification_recipient, notification_msg.as_string())
                    log_message(task_id, f"Notification email sent to {notification_recipient}.")
            except Exception as email_err:
                logging.error(f"Failed to send notification email for task {task_id}: {email_err}")

        # --- 5. Return Success Status and Output ---
        return {
            'status': 'COMPLETED',
            'task_id': task_id,
            'output_data': {
                'eml_file_path': output_path,
                'case_id': case_id,
                'filename': unique_filename
            },
            'logs': [f"EML file created at {output_path}"]
        }

    except Exception as e:
        logging.exception(f"Error in package_to_eml for task {task_id}: {e}")
        
        # Send error notification if configured
        send_notification = input_data.get('send_notification', False)
        if send_notification:
            try:
                smtp_config = input_data.get('smtp_config', {})
                smtp_server = smtp_config.get('server', 'smtp.gmail.com')
                smtp_port = smtp_config.get('port', 587)
                smtp_username = smtp_config.get('username', 'your-email@gmail.com')
                smtp_password = smtp_config.get('password', 'your-app-password')
                notification_recipient = smtp_config.get('notification_recipient', smtp_username)

                notification_subject = f"Task {task_id} Failed"
                notification_body = f"Failed to create EML file for Case ID {case_id}. Error: {str(e)}"

                notification_msg = MIMEText(notification_body, 'plain')
                notification_msg['Subject'] = notification_subject
                notification_msg['From'] = smtp_username
                notification_msg['To'] = notification_recipient

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(smtp_username, notification_recipient, notification_msg.as_string())
                    log_message(task_id, f"Error notification email sent to {notification_recipient}.")
            except Exception as email_err:
                logging.error(f"Failed to send error notification email for task {task_id}: {email_err}")

        return {
            'status': 'FAILED',
            'task_id': task_id,
            'reason_for_failure': 'EML_Packaging_Error',
            'error_message': str(e),
            'logs': [f"Error processing task {task_id}: {str(e)}"]
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'EML Package Service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/create-eml', methods=['POST'])
def create_eml():
    """
    Main endpoint to create EML files
    Expected JSON payload:
    {
        "case_id": "CASE123",
        "email_body": "This is the email content",
        "email_subject": "Subject of the email",
        "sender_email": "sender@example.com",
        "recipient_email": "recipient@example.com",
        "body_type": "plain",  # or "html"
        "attachments": [
            {
                "filename": "document.pdf",
                "attachment_data": "base64_encoded_string_here"
            }
        ],
        "send_notification": false,  # optional
        "smtp_config": {  # optional, only needed if send_notification is true
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "notification_recipient": "admin@example.com"
        }
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'status': 'FAILED',
                'error': 'Content-Type must be application/json'
            }), 400

        input_data = request.get_json()
        
        if not input_data:
            return jsonify({
                'status': 'FAILED',
                'error': 'No JSON data provided'
            }), 400

        # Process the EML creation
        result = package_to_eml(input_data)
        
        # Return appropriate HTTP status code
        status_code = 200 if result['status'] == 'COMPLETED' else 500
        
        return jsonify(result), status_code

    except Exception as e:
        logging.exception(f"Error in create_eml endpoint: {e}")
        return jsonify({
            'status': 'FAILED',
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/create-eml/batch', methods=['POST'])
def create_eml_batch():
    """
    Batch endpoint to create multiple EML files
    Expected JSON payload:
    {
        "requests": [
            {
                "case_id": "CASE123",
                "email_body": "Email content 1",
                ...
            },
            {
                "case_id": "CASE124", 
                "email_body": "Email content 2",
                ...
            }
        ]
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'status': 'FAILED',
                'error': 'Content-Type must be application/json'
            }), 400

        batch_data = request.get_json()
        requests_list = batch_data.get('requests', [])
        
        if not requests_list:
            return jsonify({
                'status': 'FAILED',
                'error': 'No requests provided in batch'
            }), 400

        results = []
        for req in requests_list:
            result = package_to_eml(req)
            results.append(result)

        # Count successes and failures
        completed = sum(1 for r in results if r['status'] == 'COMPLETED')
        failed = len(results) - completed

        return jsonify({
            'status': 'BATCH_COMPLETED',
            'total_requests': len(results),
            'completed': completed,
            'failed': failed,
            'results': results
        }), 200

    except Exception as e:
        logging.exception(f"Error in batch create_eml endpoint: {e}")
        return jsonify({
            'status': 'FAILED',
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Create a basic uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Makes it accessible from outside localhost
        port=6000,
        debug=True  # Set to False in production
    )