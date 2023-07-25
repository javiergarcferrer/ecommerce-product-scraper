import json
import requests
from requests_html import HTMLSession
import progressbar
import re

session = HTMLSession()

url = 'https://lifestylegarden.com/all-outdoor'
link_tag = '.woocommerce-LoopProduct-link'
fields = {
    'title': '.et_pb_wc_title',
    'brief': '.et_pb_wc_description',
    'description': '.et-dynamic-content-woo--product_description',
    'category': '.et_pb_accordion_item_5_tb_body h5'
}
image_tag = 'img'
filename = 'muebles.json'


def get_hlinks(url: str, link_tag: str, pagination=None) -> [str]:
    request = session.get(url)
    products = request.html.find(link_tag)
    base_url = re.search(r'(https?://[^/]+)/', url).group(1)
    hlinks = [product.find('a', first=True).attrs['href'] for product in products]
    hlinks = [link if link.startswith('http') else base_url + link for link in hlinks]
    
    if pagination:
        next_page = request.html.find(pagination, first=True)
        next_page = next_page.find('a')[-1].attrs['href']
        next_page = base_url + next_page if not next_page.startswith('http') else next_page
        if next_page == url:
            next_page = None

    return hlinks, next_page


def get_product(link: str, fields: dict, image_tag=None) -> dict:
    request = session.get(link)
    product = {}
    for key, selector in fields.items():
        el = request.html.find(selector, first=True)
        product[key] = el.full_text.strip() if el else ''
    product['url'] = link

    if image_tag:
        image_elements = request.html.find(image_tag)
        product['images'] = [{'src': image.find('a', first=True).attrs['href']} 
                             for image in image_elements if image.find('a', first=True)]

    return {'product': product}


def scrape_products_to_file(url: str, link_tag: str, fields: dict, filename: str, image_tag=None):
    hlinks = get_hlinks(url, link_tag)
    products = []

    with progressbar.ProgressBar(max_value=len(hlinks)) as bar:
        for i, hlink in enumerate(hlinks):
            product = get_product(hlink, fields, image_tag)
            products.append(product)
            bar.update(i)

    with open(filename, 'w') as f:
        json.dump(products, f, indent=4)


if __name__ == "__main__":
    scrape_products_to_file(url, link_tag, fields, filename, image_tag)
