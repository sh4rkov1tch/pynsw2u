# PyNSW2u
This site is fucking horrible to navigate through so let's scrape it instead

## Pre-requisites
Clone the repository, create a virtualenv, install all the requirements, add your AWS Access Key and Secret Key to your environment (refer to [requests-ip-rotator](https://github.com/Ge0rg3/requests-ip-rotator#aws-authentication)) and you're ready to launch the main.py executable

```
git clone https://github.com/Sharqo78/pynsw2u
cd pynsw2u
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
python main.py
```
## What does it generate
A file that's called `final_scrape.json` that contains every game that the script could scrape.

## What's the Flask app for ?
Once you are done scraping, just launch the Flask app and go to `http://localhost:5000` to search for the games you want in a more intuitive way (reading JSON files is really tiring..)

## Why is the code so ugly ?
I just wanted it to work alright
