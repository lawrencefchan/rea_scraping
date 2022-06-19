# rea_scraping
Scripts for scraping historical dwelling price data from realestate.com.au

Uses selenium (download chrome driver 90.0.4430.24 [here](https://chromedriver.storage.googleapis.com/index.html?path=90.0.4430.24/)).

Note: internet connection is required to render mapbox map (house.html and unit.html).

## Allhomes

### **scrape_sales_prices.py**
Scrapes historical sales prices from allhomes.com.au using requests and bs4. Separate results are saved for each suburb in the following json format:
```
results = {
    'suburb_name': {
        'street_name': {
            'property_name': {
                'transfers': [list of dicts],  # completed properties
                'type': str,  # dwelling type
                'bed': int,  # number of bedrooms
                'bath': int,  # number of bathrooms
                'garage': int,  # number of garages
            },
            'complete': bool  # street is completed
        },
        'complete': bool  # suburb is completed
    }
}
```
where `transfers` is a list of dictionaries, each with keys including (but not limited to?) `Contract`, `Transfer`, `Listed`, `Days on market`, `Block size`, `Transfer type`, `Purpose`, `Price`, corresponding to a sale.

### **munge_results.py**
Various helper functions for allhomes results.

## Resources
https://digitalfinanceanalytics.com/blog/mortgage-stress-grinds-higher-before-rate-rises/

https://www.finder.com.au/how-to-find-out-property-past-sales-history

https://www.allhomes.com.au/ah/research/quay-street-haymarket-nsw-2000/1933521212/sale-history
* faster way to scrape sales history??