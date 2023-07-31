import json
import requests
import logging
from requests_html import HTMLSession
import progressbar
import re

logging.basicConfig(level=logging.INFO)

def get_next_page_link(request, base_url, pagination):
    """Get link of the next page."""
    if pagination:
        pagination_element = request.html.find(pagination, first=True)
        if pagination_element:
            next_page_link = pagination_element.find('a')[-1].attrs['href']
            next_page_link = f"{base_url}/{next_page_link}" if not next_page_link.startswith('http') else next_page_link
            if next_page_link == base_url:
                next_page_link = None
            return next_page_link
    return None

def get_product_links(url: str, link_tag: str, pagination=None) -> [str]:
    """Get product links on a page."""
    session = HTMLSession()
    request = session.get(url)
    products = request.html.find(link_tag)
    base_url = re.search(r'(https?://[^/]+)/', url).group(1)
    product_links = [product.find('a', first=True).attrs['href'] for product in products]
    product_links = [link if link.startswith('http') else base_url + link for link in product_links]
    next_page_link = get_next_page_link(request, base_url, pagination)

    return product_links, next_page_link

def extract_images(request, image_tag):
    """Extract images from the product page."""
    image_elements = request.html.find(image_tag)
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

def scrape_product_info(product_link: str, fields: dict, image_tag=None) -> dict:
    """Scrape product information."""
    session = HTMLSession()
    request = session.get(product_link)
    product_data = {}
    for key, selector in fields.items():
        el = request.html.find(selector, first=True)
        product_data[key] = el.full_text.strip() if el else ''
    product_data['url'] = product_link

    if image_tag:
        product_data['images'] = extract_images(request, image_tag)

    return {'product': product_data}

def scrape_site(url: str, link_tag: str, fields: dict, filename: str, image_tag=None, pagination=None):
    """Scrape site for products information."""
    all_products_data = []
    page_number = 1

    while url:
        product_links, url = get_product_links(url, link_tag, pagination)

        with progressbar.ProgressBar(max_value=len(product_links), 
                                     prefix=f'Page {page_number}: ') as bar:
            for i, product_link in enumerate(product_links):
                try:
                    product_data = scrape_product_info(product_link, fields, image_tag)
                    all_products_data.append(product_data)
                except Exception as e:
                    logging.error(f'Error occurred while scraping {product_link}: {e}')
                bar.update(i)

        page_number += 1

    with open(filename, 'w') as f:
        json.dump(all_products_data, f, indent=4)
