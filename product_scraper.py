import json
import requests
import logging
from requests_html import HTMLSession
import progressbar
import re

logging.basicConfig(level=logging.INFO)

class ProductScraper:
    
    def __init__(self, url, link_tag, fields, filename, image_tag=None, pagination=None):
        self.url = url
        self.link_tag = link_tag
        self.fields = fields
        self.filename = filename
        self.image_tag = image_tag
        self.pagination = pagination
        self.all_products_data = []
        self.session = HTMLSession()

    def get_next_page_link(self, request, base_url):
        """Get link of the next page."""
        if self.pagination:
            pagination_element = request.html.find(self.pagination, first=True)
            if pagination_element:
                next_page_link = pagination_element.find('a')[-1].attrs['href']
                next_page_link = f"{base_url}/{next_page_link}" if not next_page_link.startswith('http') else next_page_link
                if next_page_link == base_url:
                    next_page_link = None
                return next_page_link
        return None

    def get_product_links(self, url) -> [str]:
        """Get product links on a page."""
        request = self.session.get(url)
        products = request.html.find(self.link_tag)
        base_url = re.search(r'(https?://[^/]+)/', url).group(1)
        product_links = [product.find('a', first=True).attrs['href'] for product in products]
        product_links = [link if link.startswith('http') else base_url + link for link in product_links]
        next_page_link = self.get_next_page_link(request, base_url)

        return product_links, next_page_link

    def extract_images(self, request):
        """Extract images from the product page."""
        image_elements = request.html.find(self.image_tag)
        image_sources = []
        for image in image_elements:
            try:
                image_sources.append({'src': image.attrs['data-src']})
            except KeyError:
                try:
                    image_sources.append({'src': image.attrs['href']})
                except KeyError:
                    break
        return image_sources

    def scrape_product_info(self, product_link) -> dict:
        """Scrape product information."""
        session = self.session
        request = session.get(product_link)
        product_data = {}
        for key, selector in self.fields.items():
            el = request.html.find(selector, first=True)
            product_data[key] = el.full_text.strip() if el else ''
        product_data['url'] = product_link

        if self.image_tag:
            product_data['images'] = self.extract_images(request)

        return {'product': product_data}

    def scrape_site(self):
        """Scrape site for products information."""
        url = self.url
        page_number = 1

        while url:
            product_links, url = self.get_product_links(url)

            with progressbar.ProgressBar(max_value=len(product_links), 
                                         prefix=f'Page {page_number}: ') as bar:
                for i, product_link in enumerate(product_links):
                    try:
                        product_data = self.scrape_product_info(product_link)
                        self.all_products_data.append(product_data)
                    except Exception as e:
                        logging.error(f'Error occurred while scraping {product_link}: {e}')
                    bar.update(i)

            page_number += 1

        with open(self.filename, 'w') as f:
            json.dump(self.all_products_data, f, indent=4)
