from flask import Flask, render_template, jsonify

import smtplib
import datetime

from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

gmail_user = "pulseappserver@gmail.com"
gmail_pwd = "qzkigrfvlolpqwuz"
#!ToDo Move password to a config file for production settings

class Mail:
    """
    Klasse zum Erstellen und Senden von Emails über einen existierenden SMTP-Server
    Hier Gmail mit Autorisierung über App-Tokens
    """

    def send_mail(address, web_address):
        """
        :param username Nutzername des Patienten für den das Konto erstellt wurde
        :web_address Die URL der Web-Anwendung
        Schreiben und senden einer Mail, die die Parameter beinhaltet
        """
        msg = EmailMessage()
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_pwd)
        except Exception as e:
            print(e)

        subject  =  'Änderung in Ihren Diagnosen vom '+ str(datetime.date.today())
        body = 'Ihr Arzt hat soeben eine Diagnose zu Ihrem EKG hinzugefuegt. \n' \
               'Sie koennen diese unter ' + web_address +' einsehen'
        msg['Subject'] = "Es gibt neue Diagnosen bei Pulse"
        msg['From'] = gmail_user
        msg['To'] = address
        msg.set_content(body)
        try:
            server.send_message(msg)
            server.close()
            print("success")
            resp = jsonify(success=True)
            return resp
        except Exception as e:
            print(e)

    def send_mail_created(address, username, password, web_address):
        """
        :param username Nutzername des Patienten für den das Konto erstellt wurde
        :param password das zugewiesene Passwort
        :web_address Die URL der Web-Anwendung
        Schreiben und senden einer Mail, die die Parameter beinhaltet
        """
        msg = EmailMessage()
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_pwd)
        except Exception as e:
            print(e)

        subject = "Herzlich willkommnen bei Pulse"
        body = "Ihr Arzt hat soeben einen Nutzeraccount für Pulse angelegt." \
               f"Sie können sich ab sofort mit Ihrem Nutzernamen {username} und " \
               f"dem sicher generierten Passwort \"{password}\" unter " + web_address + " einloggen"
        msg['Subject'] = "Herzlich willkommen bei Pulse"
        msg['From'] = gmail_user
        msg['To'] = address
        msg.set_content(body)
        try:
            server.send_message(msg)
            server.close()
            print("success")
            resp = jsonify(success=True)
            return resp
        except Exception as e:
            print(e)
