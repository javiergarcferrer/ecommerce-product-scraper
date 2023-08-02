import inquirer
from product_scraper import ProductScraper
import json
import logging

logging.basicConfig(level=logging.INFO)


def load_sites(filename):
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
    questions = [
        inquirer.List('site',
                      message="Which site do you want to scrape?",
                      choices=sites.keys(),
                      ),
    ]
    return inquirer.prompt(questions)


def main():
    sites = load_sites("sites_config.json")

    if sites:
        answers = get_user_input(sites)
        site = answers['site']
        site_config = sites[site]

        scraper = ProductScraper(
            url=site_config['url'], 
            link_tag=site_config['link_tag'], 
            fields=site_config['fields'], 
            filename=site_config['filename'], 
            image_tag=site_config['image_tag'], 
            pagination=site_config['pagination']
        )
        scraper.scrape_site()


if __name__ == "__main__":
    main()
