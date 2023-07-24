import json
import requests
import product_scraper
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

SHOPIFY_STORE_DOMAIN = ''
ACCESS_TOKEN = ''

# URL of the page where product links are listed
url = 'https://lifestylegarden.com/all-outdoor'
link_tag = '.woocommerce-LoopProduct-link'
fields = {
    'title': '.et_pb_wc_title',
    'brief': '.et_pb_wc_description',
    'description': '.et-dynamic-content-woo--product_description',
    'category': '.et_pb_accordion_item_5_tb_body h5'
}
image_tag = '.et_pb_gallery_item'
filename = 'muebles.json'

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

if __name__ == "__main__":
    products = product_scraper.scrape_products_to_file(url, link_tag, fields, filename, image_tag)
    for product in products:
        post_product(product)
