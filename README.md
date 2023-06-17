# rea_scraping
This package contains scripts used to scrape realestate data from:
- realestate.com.au
- Allhomes
- Domain (to be implemented)

## realestate_com
### scrape_historical_prices
Uses `sel_scrape` to pull suburb-level historical data for houses/units. Includes:
* Historical sales/rental data (written to `prices_volumes`):
    - **median:** 12 month median price trend for houses/units
    - **volume:** 12 month total sales/leases
* Sales/rental summaries (written to `current_snapshot`):
    - **daysOnSite:** median time on market in the past 12 months
    - **rentalYield:** current rental yield (owned propreties only)
    - **demand:** no. buyers/renters interested in the past month
    - **supply:** no. dwellings available in the past month

Data is saved to `./data/historical_trends.db`.

__TODO__
- fix multiple print statements on write

### recent_sales
Scrapes recent sales results for all states including clearance rates and number of homes sold etc.

Data is saved to `./data/recent_sales.db`.

### saved_properties
Todo

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
* TODO: check faster way to scrape sales history??

## Data sources
NSW postcode regions: https://www.training.nsw.gov.au/about_us/postcodes_byregion.html

NSW regions maps: https://www.training.nsw.gov.au/about_us/sts_contacts.html


Sydney postcode regions: https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF60VG7nzs5QxID3ADwr3DGJh71qFg

Postcode mapping method: https://greenash.net.au/thoughts/2014/07/australian-lga-to-postcode-mappings-with-postgis-and-intersects/


## Achive/old scripts/old notes
Uses selenium (download chrome driver 90.0.4430.24 [here](https://chromedriver.storage.googleapis.com/index.html?path=90.0.4430.24/)).  
Note: internet connection is required to render mapbox map (house.html and unit.html).

__TODOs__

EDA - points of interest
* check correlation between house and unit price changes
* areas of highest growth (range of years)
* areas of lowest growth (range of years)
* areas of highest yield 
* measures of variance: z-score, r^2 against linear fit
* discard series with low count values and lots mising data 

Hypotheses:
* low variance implies stable pricing, possibly low growth
* house and unit prices should be complementary (both in terms of variance and growth). 
    Deviation from this implies data skewed by outliers (e.g. enormous, 1-off land purchases)

Other:
* geographic plotting
    * https://github.com/KerryHalupka/plotly_choropleth
    * https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-spatial-data/customize-raster-plots/interactive-maps/

* scatter plot - last month % delta vs last year % delta

Sources:
* LGA dataset for test_plot.py:
https://data.aurin.org.au/dataset/au-govt-abs-census-lga-g43b-labour-force-status-by-age-by-sex-census-2016-lga2016/resource/48cc24f4-c710-4e23-a260-06a5fd573551
