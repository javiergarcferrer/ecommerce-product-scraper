import json
import logging
from requests_html import HTMLSession
import requests
import progressbar
import re
import os
import argparse
import inquirer
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

class ProductScraper:
    def __init__(self, urls, link_tag, fields, filename, image_tag=None, pagination=None, thumbnail_tag=None, metafields=None):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.link_tag = link_tag
        self.fields = fields
        self.filename = filename
        self.image_tag = image_tag
        self.pagination = pagination
        self.thumbnail_tag = thumbnail_tag
        self.metafields = metafields or {}
        self.all_products_data = []
        self.session = HTMLSession()

    def get_next_page_link(self, request, base_url):
        if self.pagination:
            pagination_element = request.html.find(self.pagination, first=True)
            if pagination_element:
                next_page_link = pagination_element.find('a')[-1].attrs['href']
                next_page_link = f"{base_url}/{next_page_link}" if not next_page_link.startswith('http') else next_page_link
                return next_page_link
        return None


    def get_product_links(self, url):
        request = self.session.get(url)
        products = request.html.find(self.link_tag)
        base_url = re.search(r'(https?://[^/]+)/', url).group(1)
        product_links_with_thumbnails = []

        for product in products:
            link_element = product.find('a', first=True)
            link = link_element.attrs['href']
            if not link.startswith('http'):
                link = f"{base_url}{link}"

            # Extract the thumbnail for each product
            thumbnail_element = product.find(self.thumbnail_tag, first=True)
            thumbnail_src = thumbnail_element.attrs.get('src') if thumbnail_element else None

            product_links_with_thumbnails.append((link, thumbnail_src))

        next_page_link = self.get_next_page_link(request, base_url)
        return product_links_with_thumbnails, next_page_link


    def extract_images(self, request):
        image_elements = request.html.find(self.image_tag)
        image_sources = [image.attrs.get('href') for image in image_elements]
        return image_sources

    def scrape_product_info(self, product_link, thumbnail_src):
        request = self.session.get(product_link)
        product_data = {}
        for key, selector in self.fields.items():
            el = request.html.find(selector, first=True)
            product_data[key] = el.text.strip() if el else ''
        product_data['url'] = product_link

        if self.image_tag:
            image_sources = self.extract_images(request)
            product_data['images'] = [thumbnail_src] + image_sources if thumbnail_src else image_sources

        return {'product': product_data}

    def scrape_site(self):
        for url in self.urls:
            page_number = 1
            current_url = url

            while current_url:
                product_links_with_thumbnails, next_page_url = self.get_product_links(current_url)
                with progressbar.ProgressBar(max_value=len(product_links_with_thumbnails), prefix=f'Page {page_number}: ') as bar:
                    for i, (product_link, thumbnail_src) in enumerate(product_links_with_thumbnails):
                        try:
                            product_data = self.scrape_product_info(product_link, thumbnail_src)
                            self.all_products_data.append(product_data)
                            bar.update(i)
                        except Exception as e:
                            logging.error(f'Error occurred while scraping {product_link}: {e}')

                    current_url = next_page_url if self.pagination else None
                    page_number += 1

        with open(self.filename, 'w') as f:
            json.dump(self.all_products_data, f, indent=4)

def load_sites(filename):
    try:
        with open(filename, 'r') as f:
            sites = json.load(f)
        return sites
    except FileNotFoundError:
        logging.error(f'File {filename} not found.')
        return None
    except json.JSONDecodeError:
        logging.error(f'Error decoding JSON from {filename}.')
        return None
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return None

def get_user_input(sites):
    questions = [inquirer.List('site', message="Which site do you want to scrape?", choices=sites.keys())]
    return inquirer.prompt(questions)

def post_product(product: dict):
    shop_url = os.environ.get('SHOPIFY_STORE_DOMAIN')
    access_token = os.environ.get('ACCESS_TOKEN')
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    # Construct the product data with metafields
    product_data = {
        "product": {
            "title": product.get('title'),
            "body_html": product.get('body_html'),
            "images": [{"src": img} for img in product.get('images', [])],
            "product_type": product.get('product_type')
        }
    }

    # Add metafields if present
    if 'metafields' in product:
        product_data["product"]["metafields"] = [
            {
                "namespace": "global",
                "key": key,
                "value": value,
                "type": "single_line_text_field"
            } for key, value in product['metafields'].items()
        ]

    try:
        # Create the product
        response = requests.post(f"https://{shop_url}/admin/api/2023-10/products.json", 
                                 headers=headers, json=product_data)
        response.raise_for_status()

        # Extract product ID
        product_id = response.json().get("product", {}).get("id")
        return True, product.get('title')  # Return success status and product title
    except requests.exceptions.RequestException as e:
        return False, product.get('title')  # Return failure status and product title


def main():
    parser = argparse.ArgumentParser(description='Scrape and optionally post product data.')
    parser.add_argument('--post', action='store_true', help='If set, scraped products will be posted to the store.')
    args = parser.parse_args()

    sites = load_sites("sites_config.json")
    if not sites:
        return

    answers = get_user_input(sites)
    site_config = sites[answers['site']]

    scraper = ProductScraper(
        site_config['url'],
        site_config['link_tag'],
        site_config['fields'],
        site_config['filename'],
        site_config.get('image_tag'),
        site_config.get('pagination'),
        site_config.get('thumbnail_tag')
    )

    scraper.scrape_site()

    if args.post:
        total_products = len(scraper.all_products_data)
        with progressbar.ProgressBar(max_value=total_products, redirect_stdout=True) as bar:
            for i, product in enumerate(scraper.all_products_data):
                success, title = post_product(product['product'])
                bar.update(i)
                if success:
                    print(f"Uploaded: {title}")
                else:
                    print(f"Failed to upload: {title}")

if __name__ == "__main__":
    main()

