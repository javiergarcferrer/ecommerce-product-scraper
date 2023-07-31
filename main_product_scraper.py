import inquirer
import product_scraper
import json
import logging

logging.basicConfig(level=logging.INFO)


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


def scrape_selected_site(site_config):
    """Calls the scraper with the selected site's configuration."""
    try:
        product_scraper.scrape_site(
            site_config['url'], 
            site_config['link_tag'], 
            site_config['fields'], 
            site_config['filename'], 
            site_config['image_tag'], 
            site_config['pagination']
        )
    except Exception as e:
        logging.error(f"Error occurred while scraping site: {e}")


def main():
    """Main function to load site data and initiate the scraping process."""
    sites = load_sites("sites_config.json")

    if sites:
        answers = get_user_input(sites)
        site = answers['site']

        scrape_selected_site(sites[site])


if __name__ == "__main__":
    main()
