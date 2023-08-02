import argparse
import inquirer
import json
import logging
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from product_scraper import ProductScraper

logging.basicConfig(level=logging.INFO)

SHOPIFY_STORE_DOMAIN = ''
ACCESS_TOKEN = ''

def load_sites(filename):
    """Load site data from given JSON file."""
    try:
        with open(filename, 'r') as f:
            sites = json.load(f)
        return sites
    except FileNotFoundError:
        logging.error(f'File {filename} not found.')
    except json.JSONDecodeError:
        logging.error(f'Error decoding JSON from {filename}.')
    except Exception as e:
        logging.error(f'Unexpected error: {e}')

def get_user_input(sites):
    """Prompts user to select a site for scraping."""
    questions = [
        inquirer.List('site',
                      message="Which site do you want to scrape?",
                      choices=sites.keys(),
                      ),
    ]
    return inquirer.prompt(questions)

def post_product(product: dict) -> None:
    try:
        response = requests.post(
            f'https://{SHOPIFY_STORE_DOMAIN}/admin/api/2023-04/products.json',
            headers={
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': ACCESS_TOKEN
            },
            data=json.dumps({'product': product['product']})
        )
        response.raise_for_status()
        product_id = response.json()['product']['id']
        print(f'Product created successfully with ID: {product_id}')
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(f'Failed to create product. Exception: {str(e)}')
    except requests.exceptions.HTTPError as errh:
        print(f'An Http Error occurred: {str(errh)}')
        print('Response content:', errh.response.content)
    except requests.exceptions.RequestException as err:
        print(f'An Unknown Error occurred: {str(err)}')

def main():
    """Main function to load site data and initiate the scraping process."""
    parser = argparse.ArgumentParser(description='Scrape and optionally post product data.')
    parser.add_argument('--post', action='store_true', help='If set, scraped products will be posted to the store.')
    args = parser.parse_args()

    sites = load_sites("sites_config.json")

    if sites:
        answers = get_user_input(sites)
        site = answers['site']

        scraper = ProductScraper(sites[site]['url'], 
                                 sites[site]['link_tag'], 
                                 sites[site]['fields'], 
                                 sites[site]['filename'], 
                                 sites[site]['image_tag'], 
                                 sites[site].get('pagination'))
        products = scraper.scrape_site()

        if args.post:
            for product in products:
                post_product(product)

if __name__ == "__main__":
    main()
