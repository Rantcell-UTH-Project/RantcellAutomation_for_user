import imaplib, email, os
import re


def mail_reader_and_extract_specfic_word(email_address,password,Search_for_emails_with_specific_criteria,logic_for_extract):
    # Connect to the email server (IMAP example for Gmail)
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(email_address, password)
    mail.select("inbox")
    try:
        # Search for emails with specific criteria
        status, email_ids = mail.search(None, f'UNSEEN SUBJECT "{Search_for_emails_with_specific_criteria}"')
        # Check if any emails were found
        if status == 'OK':
            # Process the email IDs or perform other actions as needed
            email_ids_list = email_ids[0].split()
            latest_email_id = [email_ids_list[-1]]

            for email_id in latest_email_id:
                status, email_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    raw_email = email_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    # Iterate through email parts to find attachments
                    for part in email_message.walk():
                        content = None
                        if part.get_payload() is not None:
                            content = part.get_payload()
                            print(content)
                            four_digit_numbers = logic_for_extract(content)
                            if four_digit_numbers:
                                print(four_digit_numbers)
                                # Delete the email (use mail.store(email_id, '+FLAGS', '(\Deleted)' for deletion)
                                mail.store(email_id, '+FLAGS', '(\Deleted)')
                                print(f"Deleted email ID: {email_id}")
                                # Permanently remove the deleted emails
                                mail.expunge()
                                return four_digit_numbers
                else:
                    print(f"Error fetching email ID: {email_id}")
            # Permanently remove the deleted emails
            mail.expunge()
        else:
            print("No emails with the specified criteria were found.")
        # Logout and close the connection
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

def delete_specfic_mail_using_subject(email_address,password,Search_for_emails_with_specific_criteria):
    # Connect to the email server (IMAP example for Gmail)
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(email_address, password)
    mail.select("inbox")
    try:
        # Search for emails with specific criteria
        status, email_ids = mail.search(None, f'UNSEEN|SEEN SUBJECT "{Search_for_emails_with_specific_criteria}"')
        # Check if any emails were found
        if status == 'OK':
            # Process the email IDs or perform other actions as needed
            email_ids_list = email_ids[0].split()

            for email_id in email_ids_list:
                # Delete the email (use mail.store(email_id, '+FLAGS', '(\Deleted)' for deletion)
                mail.store(email_id, '+FLAGS', '(\Deleted)')
                print(f"Deleted email ID: {email_id}")
                # Permanently remove the deleted emails
                mail.expunge()
        else:
            print("No emails with the specified criteria were found.")
        # Logout and close the connection
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

# # Email account settings
# email_address = "archanacr594@gmail.com"
# password = "fsarbvzbowmgwupe"
# mail_reader_and_extract_specfic_word(email_address,password,Search_for_emails_with_specific_criteria="Request",logic_for_extract=lambda content: re.findall(r'RantCell account is (\d+)', content))




