"""
This script contains the main task for running the news scraper robot.
It retrieves work item variables, initializes the MainScrapper with these variables,
and executes the scraping process.
"""
import logging

from robocorp.tasks import task
from robocorp import workitems

from scrapper import MainScrapper


@task
def minimal_task():
    """
    The main task function for the news scraper robot.
    
    This function sets up logging, retrieves input work item variables, initializes
    the MainScrapper with these variables, and runs the scrape method. It logs the 
    start and end of the scraping process.

    Returns:
        None
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S %z"
    )

    logging.info('-- Starting Up Scrapper')
    with workitems.inputs.current as item:
        MainScrapper(**item.payload).scrape()

    logging.info('-- Scrapper finished')
