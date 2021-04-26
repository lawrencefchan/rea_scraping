# %%
from bs4 import BeautifulSoup
import requests 
import pandas as pd

url_base = r'https://www.realestate.com.au/neighbourhoods/'
postcodes = pd.read_csv('suburb_postcodes.csv')
# https://www.realestate.com.au/neighbourhoods/north-epping-2121-nsw

urls = [f'{url_base}{s.lower().replace(" ", "-")}-{p}-nsw'
        for p, s in zip(postcodes['Postcode'], postcodes['Suburb'])]

headers = requests.utils.default_headers()
headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
})

for url in [i for i in urls if 'epping' in i]:
    print(url)
    r = requests.get(url, headers=headers)
    print(r.status_code)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    # c = soup.find_all('div', attrs={"class": "price h1 strong"})
    print(soup.prettify())

    break


# %%
soup.find_all('div', attrs={"class": "price h1 strong"})

