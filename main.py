import datetime
import os
import smtplib
import time

import pymysql as sql
from dotenv import load_dotenv

load_dotenv("data.env")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def sender(email, title, body):
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("PASSWORD")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            message = f"Subject: {title}\n\n{body}"
            smtp.sendmail(sender_email, email, message)
            print(f"Email sent successfully to {email}")
            return True
    except smtplib.SMTPException as smtp_e:
        print(f"SMTP error occurred: {str(smtp_e)}")
        return False
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def process_emails():
    try:

        connection = sql.connect(
            host=DB_HOST,
            user=DB_USER,
            database=DB_NAME,
            password=DB_PASSWORD,

        )
        cursor = connection.cursor()

        while True:
            cursor.execute("SELECT id, email, title, body, time_stamp FROM email_table")
            emails = cursor.fetchall()

            for email_record in emails:
                record_id, email, title, body, entry_date = email_record

                if isinstance(entry_date, str):
                    entry_date = datetime.datetime.strptime(entry_date, "%Y-%m-%d %H:%M:%S")

                time_difference = datetime.datetime.now() - entry_date

                if time_difference.total_seconds() >= 12 * 60 * 60:
                    print(f"Record {record_id} is older than 12 hours. Deleting record.")
                    cursor.execute("DELETE FROM email_table WHERE id = %s", (record_id,))
                    connection.commit()
                else:

                    if sender(email, title, body):
                        print(f"Email for record {record_id} sent successfully. Deleting record.")
                        cursor.execute("DELETE FROM email_table WHERE id = %s", (record_id,))
                        connection.commit()

            time.sleep(1)

    except sql.MySQLError as db_error:
        print(f"Database error occurred: {str(db_error)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")


process_emails()
