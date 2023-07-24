import json
import requests
from requests_html import HTMLSession
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

SHOPIFY_STORE_DOMAIN = '24a907-3.myshopify.com'
ACCESS_TOKEN = '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'

session = HTMLSession()

# URL of the page where product links are listed
url = 'https://lifestylegarden.com/all-outdoor'

def get_hlinks(url: str) -> [str]:
    request = session.get(url)
    products = request.html.find('.woocommerce-LoopProduct-link') ## hyperlink identifier; tag, .css
    hlinks = [product.find('a', first=True).attrs['href'] for product in products]
    
    return hlinks

def get_product(link: str) -> {dict}:
    request = session.get(link)
    title = request.html.find('.et_pb_wc_title', first=True).full_text.strip() if request.html.find('.et_pb_wc_title', first=True) else ''
    brief = request.html.find('.et_pb_wc_description', first=True).full_text.strip() if request.html.find('.et_pb_wc_description', first=True) else ''
    description = request.html.find('.et-dynamic-content-woo--product_description', first=True).full_text.strip() if request.html.find('.et-dynamic-content-woo--product_description', first=True) else ''
    category = request.html.find('.et_pb_accordion_item_5_tb_body h5', first=True).full_text.strip() if request.html.find('.et_pb_accordion_item_5_tb_body a', first=True) else ''
    image_urls = [image.find('a', first=True).attrs['href'] for image in request.html.find('.et_pb_gallery_item') if image.find('a', first=True)]
    product = {
        'product': {
            'title': title,
            'body_html': description,
            'vendor': 'LifestyleGarden',
            'product_type': category,
            'metafields': [
                {
                    'key': 'brief',
                    'value': brief,
                    'type': 'multi_line_text_field',
                    'namespace': 'global'
                }
            ],
            'images': [{'src': url} for url in image_urls]
        }
    }

    return product

def post_product(product: {dict}) -> None:
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

# Get all product links
hlinks = get_hlinks(url)
for hlink in hlinks:
    product = get_product(hlink)
    post = post_product(product)
