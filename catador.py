import product_scraper

url = 'https://tiendaenlinea.elcatador.com/collections/all'
link_tag = '.c-product-card__top'
fields = {
    'name': '.c-product__title',
    'hook': '.c-product-description__title',
    'description': '.c-product-description__info span:last-child',
    'price': '.c-price'
}
image_tag = '.c-product-slide img'
filename = 'vinos.json'
pagination = '.c-pagination'


if __name__ == "__main__":
    product_scraper.scrape_products_to_file(url, link_tag, fields, filename, image_tag, pagination)

