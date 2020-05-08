import requests
import json
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

def get_properties_by_subscriber(base_url, subscriber_id, api_key):
    properties_url = "{}/digest/api/subscribers/{}/properties?key={}".format(base_url, subscriber_id, api_key)
    req = requests.get(properties_url)
    return req.json()

def get_all_subscribers(base_url, api_key):
    all_subscribers_url = "{}/digest/api/subscribers?key={}".format(base_url, api_key)
    req = requests.get(all_subscribers_url)
    return req.json()

def send_email(bodyContent, subscriber_info, EMAIL_INFO):
    to_email = subscriber_info["email"]
    from_email = EMAIL_INFO["EMAIL"]
    subject = 'Your Weekly Email Digest from SHS'
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    message.attach(MIMEText(bodyContent, 'html'))
    msgBody = message.as_string()

    server = SMTP(EMAIL_INFO["SERVER"], EMAIL_INFO["PORT"])
    server.ehlo()

    server.starttls()
    server.login(from_email, EMAIL_INFO["PASSWORD"])
    server.sendmail(from_email,to_email, msgBody)

    server.quit()

def renderTemplate(env, subscriber_info, properties, base_url):
    if len(properties) == 1:
        template = env.get_template('1properties.html')
    elif len(properties) == 2:
        template = env.get_template('2properties.html')
    elif len(properties) == 3:
        template = env.get_template('3properties.html')
    else:
        template = env.get_template('4properties.html')
    output = template.render(properties=properties, base_url=base_url)
    return output


if __name__ == "__main__":
    # load config file
    with open('config.json', 'r') as file:
        config = json.load(file)
    env = Environment(
        loader=FileSystemLoader(searchpath="./templates")
    )
    API_KEY = config["API_KEY"]
    BASE_URL = config["BASE_URL"]
    EMAIL_INFO = config["EMAIL_INFO"]
    FRONTEND_URL = config["FRONTEND_URL"]
    print("Getting list of subscribers from API...")
    subscribers = get_all_subscribers(BASE_URL, API_KEY)
    print("Amount of subscribers:",len(subscribers))
    for num, subscriber in enumerate(subscribers):
        # do stuff
        print("Subscriber", num)
        subscriber_info = subscriber["user"]
        subscriber_id = subscriber_info["id"]
        print("Checking API for properties fitting filters...")
        subscriber_properties = get_properties_by_subscriber(BASE_URL, subscriber_id, API_KEY)

        if(len(subscriber_properties) != 0):
            print("Generating email for properties....")
            temp = renderTemplate(env, subscriber_info, subscriber_properties, FRONTEND_URL)
            send_email(temp, subscriber_info, EMAIL_INFO)
            print("Email Sent to", subscriber_info["email"])
        else:
            print("No properties, skipping...")