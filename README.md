# Email Marketer Scraper

Quick and dirty Python 3 script to scrape subscribers from Interspire Email Marketer. Tested on 6.1.2.

## About

Why is this needed? Email marketer's export feature doesn't support exporting custom variables such as first or 
last name. Yes you can use the database however that may not always be an option.

## Usage

Install requirements:

```
pip install -r requirements.txt
```

Open up scraper.py and modify the following variables:

```
URL = 'http://www.example.com/emailmarketer/'  # url must have a trailing slash
USERNAME = 'username'
PASSWORD = 'password'
LIST_ID = 1
START_ID = 1
FINISH_ID = 10
OUT_FILE = 'subscribers.csv'

```

List id and subscriber id can be found by viewing a subscriber in the email marketer admin panel:

Note: you may get a permission denied error for valid subscriber ids that arent in the given list

```
http://www.example.com/emailmarketer/admin/index.php?Page=Subscribers&Action=View&List=LIST_ID&id=CONTACT_ID
```

Then run

```
python3 scraper.py
```

## Modification

The script currently only pulls out email, first name, last name, confirmed status, subscribed status and confirmed and 
subscribed dates. It can however be easily modified to extract more info.

Simply pass the field name as it appears in email marketer, along with ```parsed``` to ```extract_value```.

For example if we wanted to also get the subscribers phone number:

```
phone_number = extract_value(parsed, 'Phone:')
```

Then modify the ```Contact``` class and ```Contact.to_row()``` to include the new variable.

If you do add more functionality, feel free to make a pull request. 

## License 
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details