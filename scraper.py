#!/usr/bin/env python

"""Scraper.py: scrapes contact details from Interspire Email Marketer. Tested on 6.1.2 """

import datetime
import re
import requests
import csv
from bs4 import BeautifulSoup

# Modify values below

URL = 'http://www.example.com/emailmarketer/'  # url must have a trailing slash
USERNAME = 'username'
PASSWORD = 'password'

LIST_ID = 1
START_ID = 1
FINISH_ID = 10

OUT_FILE = 'contacts.csv'

# Leave these values

LOGIN_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

LOGIN_PAYLOAD = {'ss_username': USERNAME, 'ss_password': PASSWORD, 'ss_takemeto': 'index.php',
                 'SubmitButton': 'Login'}


class Contact:

    def __init__(self, email, first_name, last_name, confirmed, subscribed, confirmed_date, subscribed_date):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.confirmed = confirmed
        self.subscribed = subscribed
        self.confirmed_date = confirmed_date
        self.subscribed_date = subscribed_date

    def to_row(self):
        return [self.email, self.first_name, self.last_name, self.confirmed, self.subscribed,
                self.confirmed_date.strftime("%s") if self.confirmed_date is not None else '0',
                self.subscribed_date.strftime("%s") if self.subscribed_date is not None else '0']


class ContactsFile:

    def __init__(self):
        self.contacts = list()

    def save(self):
        with open(OUT_FILE, 'w', newline='') as file:
            writer = csv.writer(file)

            for contact in self.contacts:
                writer.writerow(contact.to_row())


def login_correct(content):
    parsed = BeautifulSoup(content, 'html.parser')

    login_error_count = parsed.find_all("span", {"class": "LoginError"})

    if len(login_error_count) == 1:
        return False
    else:
        return True


def has_permission(content):
    """checks to see if page received is an error page"""
    parsed = BeautifulSoup(content, 'html.parser')

    page_text = parsed.get_text()

    if page_text.__contains__("Permission denied. You do not have access to this area"):
        return False
    else:
        return True


def extract_value(parsed_html, key):
    """extracts a given field from the parsed html"""
    key_regex = re.compile("[\t*\n*][^A-Za-z]{}".format(key))
    tds = parsed_html.find(text=key_regex).parent.parent.find_all('td')
    raw_string = tds[1].text
    return raw_string.replace("\t", "").replace("\n", "")


def process_page_for_contact(content):
    """only extracts some values however others can be easily added for e.g if you wante"""
    parsed = BeautifulSoup(content, 'html.parser')

    # remove all tooltips which make extracting difficult
    [x.extract() for x in parsed.find_all("span", {"class": "HelpToolTip"})]

    email = extract_value(parsed, 'Email Address:')
    confirmed = True if extract_value(parsed, 'Confirmation Status:') == 'Confirmed' else False
    subscribed = True if extract_value(parsed, 'Status:') == 'Active' else False
    first_name = extract_value(parsed, 'First Name:')
    last_name = extract_value(parsed, 'Last Name:')
    subscribed_date = extract_value(parsed, 'Contact Request Date:').rstrip()
    subscribed_date_object = None
    confirmed_date = extract_value(parsed, 'Contact Confirm Date:').rstrip()
    confirmed_date_object = None

    if confirmed_date != "Unknown":
        confirmed_date_object = datetime.datetime.strptime(confirmed_date, '%B %d %Y, %I:%M %p')

    if subscribed_date != "Unknown":
        subscribed_date_object = datetime.datetime.strptime(subscribed_date, '%B %d %Y, %I:%M %p')

    return Contact(email, first_name, last_name, confirmed, subscribed, confirmed_date_object, subscribed_date_object)


def main():
    contacts_file = ContactsFile()

    s = requests.Session()

    # initial get to grab session cookie, which is upgraded inside email marketer on successful login
    r1 = s.get("{}/admin/index.php".format(URL))

    if r1.ok:

        r2 = s.post('{}admin/index.php?Page=&Action=Login'.format(URL), data=LOGIN_PAYLOAD, headers=LOGIN_HEADERS)

        if r2.ok:
            if login_correct(r2.content):

                current_id = START_ID

                while current_id <= FINISH_ID:
                    print("Currently processing id no. {}".format(current_id))

                    contact_request = s.get("{url}admin/index.php?Page=Subscribers&Action=View&List={list_id}"
                                            "&id={contact_id}".format(url=URL, list_id=LIST_ID, contact_id=current_id))

                    if contact_request.ok:
                        if has_permission(contact_request.content):
                            contacts_file.contacts.append(process_page_for_contact(contact_request.content))
                        else:
                            print("Failed to retrieve contact {} - Permission Denied!".format(current_id))
                    else:
                        print("Failed to retrieve contact {}".format(current_id))

                    current_id += 1

            else:
                print("Login Request Failed: Incorrect username or password")

        else:
            print("Login Request Failed - Status Code {}".format(r2.status_code))
    else:
        print("Initial request failed - Status Code {}".format(r1.status_code))

    contacts_file.save()


if __name__ == '__main__':
    main()