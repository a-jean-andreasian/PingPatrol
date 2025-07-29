import os
import smtplib
import requests
import base64
import json

from email.message import EmailMessage


class LogReporter:
    @classmethod
    def help(cls):
        return f"""
        {cls.__name__} is a base class for reporting logs.
        Supporting email, Telegram and Google Sheets reporting.
        
        - Telegram reporting requires the 'telegram_chat_id' and 'telegram_token' environment variables to be set. 
        
        """


    def __init__(
        self,
        destination=os.environ.get('destination'),
        destination_type=os.environ.get('destination_type'),
        protocol=os.environ.get('protocol')
    ):
        self.destination = destination
        self.destination_type = destination_type
        self.protocol = protocol

    def report(self, content: str, encoding: str = 'utf-8'):
        raise NotImplementedError("Subclasses must implement report()")




class EmailReporter(LogReporter):
    def report(self, content: str, encoding: str = 'utf-8'):
        sender = os.environ.get('email_sender')
        password = os.environ.get('email_password')
        smtp_server = os.environ.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('smtp_port', '587'))

        msg = EmailMessage()
        msg.set_content(content, subtype='plain', charset=encoding)
        msg['Subject'] = 'Log Report'
        msg['From'] = sender
        msg['To'] = self.destination

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)


class GoogleSheetsReporter(LogReporter):
    def report(self, content: str, encoding: str = 'utf-8'):
        """
        Assumes you set up a Google Apps Script web app with a POST endpoint that appends data.
        The destination should be the script URL.
        """
        payload = {
            "log": content
        }
        headers = {
            "Content-Type": "application/json"
        }
        requests.post(self.destination, json=payload, headers=headers)
