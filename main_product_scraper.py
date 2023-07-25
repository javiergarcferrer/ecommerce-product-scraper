import inquirer
import product_scraper

# Define the scraper configurations for each website
sites = {
    'LifestyleGarden': {
        'url': 'https://lifestylegarden.com/all-outdoor',
        'link_tag': '.woocommerce-LoopProduct-link',
        'fields': {
            'title': '.et_pb_wc_title',
            'brief': '.et_pb_wc_description',
            'description': '.et-dynamic-content-woo--product_description',
            'category': '.et_pb_accordion_item_5_tb_body h5'
        },
        'image_tag': '.et_pb_gallery_image a',
        'filename': 'muebles.json',
        'pagination': 'c-pagination'
    },
    'El Catador': {
        'url': 'https://tiendaenlinea.elcatador.com/collections/all',
        'link_tag': '.c-product-card__top',
        'fields': {
            'name': '.c-product__title',
            'hook': '.c-product-description__title',
            'description': '.c-product-description__info span:last-child',
            'price': '.c-price'
        },
        'image_tag': '.c-product-slide img',
        'filename': 'vinos.json',
        'pagination': '.c-pagination'
    }
}

def main():
    # Ask the user to select a site from the list
    questions = [
        inquirer.List('site',
                      message="Which site do you want to scrape?",
                      choices=sites.keys(),
                  ),
    ]
    answers = inquirer.prompt(questions)
    site = answers['site']

    # Get the configuration for the selected website
    site_config = sites[site]

    # Call the scraper with the selected site's configuration
    product_scraper.scrape_site(
        site_config['url'], 
        site_config['link_tag'], 
        site_config['fields'], 
        site_config['filename'], 
        site_config['image_tag'], 
        site_config['pagination']
    )

if __name__ == "__main__":
    main()

