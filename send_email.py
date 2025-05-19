import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from app_password import app_password

def send_email(subject, body, attachment=None):
    try:
        # Create a message object
        message = MIMEMultipart()
        message['From'] = 'shivam.mahajan117@gmail.com'
        message['To'] = 'shivam.mahajan@spectramedix.com'
        message['Subject'] = subject

        # Add body to the message
        message.attach(MIMEText(body, 'plain'))

        if attachment:
            with open(attachment, 'rb') as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                message.attach(part)

        # Create a secure connection to Gmail's SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        
        # Login to the server
        server.login('shivam.mahajan117@gmail.com', app_password)
        
        # Send the message
        server.send_message(message)
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            server.quit()  # Close the connection
        except:
            pass



# send_email('Success', 'Email check passed')