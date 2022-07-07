from flask import Flask, render_template
from flask import Flask, render_template, jsonify
from fhirclient.client import FHIRClient

import smtplib
import datetime

gmail_user = "pulseappserver@gmail.com"
gmail_pwd = "qzkigrfvlolpqwuz"

class Mail:


    def send_mail(address):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_pwd)
        except Exception as e:
            print(e)

        subject  =  'Änderung in Ihren Diagnosen vom '+ str(datetime.date.today())
        body = 'Ihr Arzt hat soeben eine Diagnose zu Ihrem EKG hinzugefuegt. \n' \
               'Sie koennen diese unter http:0.0.0.0:8080 einsehen'
        email_text = """\
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (gmail_user, ", ".join(address), subject, body)
        email_text = email_text.encode("UTF-8")
        try:
            server.sendmail(gmail_user, address, email_text)
            server.close()
            print("success")
            resp = jsonify(success=True)
            return resp
        except Exception as e:
            print(e)

    def send_mail_created(address, username, password):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_pwd)
        except Exception as e:
            print(e)

        subject = "Herzlich willkommnen bei Pulse"
        body = "Ihr Arzt hat soeben einen Nutzeraccount für Pulse angelegt." \
               f"Sie können sich ab sofort mit Ihrem Nutzernamen {username} und " \
               f"dem sicher generierten Passwort {password} unter 127.0.0.1:5000 einloggen"
        email_text = """\
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (gmail_user, ", ".join(address), subject, body)
        email_text = email_text.encode("UTF-8")
        try:
            server.sendmail(gmail_user, address, email_text)
            server.close()
            print("success")
            resp = jsonify(success=True)
            return resp
        except Exception as e:
            print(e)
