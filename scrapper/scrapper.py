"""
This module defines the MainScrapper class, which is responsible for scraping news articles from a specified website.

The MainScrapper class includes methods to:
- Initialize the scraper with a target URL, time range, and search term.
- Perform a search on the target website.
- Retrieve and process news articles based on the search term and date range.
- Download images associated with the news articles.
- Save the processed news data to an Excel file.
- Check if a text contains monetary values.
- Convert date strings to datetime objects.

Dependencies:
- logging: For logging messages and errors.
- re: For regular expression operations.
- requests: For making HTTP requests.
- os: For file and directory operations.
- datetime: For working with dates and times.
- RPA.Excel.Files: For working with Excel files.
- RPA.Browser.Selenium: For browser automation using Selenium.
- selenium.webdriver.common.by: For locating elements by various strategies.
- selenium.webdriver.support.ui: For waiting until conditions are met.
- selenium.webdriver.support.expected_conditions: For defining expected conditions.

Note: This module requires the 'locators' module to define the locators for various elements on the target website.
"""
import logging
import re
import requests
import os

from datetime import datetime as dt

from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium, WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .locators import (
    ENABLE_SEARCH_BUTTON_BIG,
    SEARCH_INPUT_BIG,
    ENABLE_SEARCH_BUTTON_SMALL,
    SEARCH_INPUT_SMALL,
    SEARCH_BUTTON_ID,
    SEARCH_SORT_OPTIONS,
    MAIN_CONTENT,
    LOAD_MODE_BUTTON,
    NEWS_TITLE_CLASS,
    NEWS_DESCRIPTION_CLASS,
    NEWS_FOOTER_CLASS,
    NEWS_IMAGE_CLASS
)


class MainScrapper():
    """
    A class to scrape news articles from Aljazeera news website, process the data, and save it to an Excel file.

    Attributes:
        target_url (str): The URL of the website to scrape.
        number_of_months (int): The range of months to consider for the news articles.
        search_phrase (str): The term to search for in the news articles.
        browser (Selenium): An instance of the Selenium browser for web scraping.
        month_limit (int): The limit of months for filtering news articles.
        window_size (tuple): The size of the browser window.
        img_directory (str): The directory to save downloaded images.
    """
    def __init__(
        self,
        target_url='https://www.aljazeera.com/',
        number_of_months=0,
        search_phrase=None
    ):
        """
        Initialize the MenuScrapper with a target URL, time range, and search term.

        Args:
            target_url (str): The URL of the website to scrape. Defaults to 'https://www.aljazeera.com/'.
            number_of_months (int): The range of months to consider for the news articles. Defaults to 1.
            search_phrase (str): The term to search for in the news articles. Defaults to None.
        """
        self.browser = Selenium()
        self.month_limit = dt.now().month - max(number_of_months - 1, 0)

        self.search_phrase = search_phrase

        self.browser.open_available_browser(url=target_url, headless=True)
        self.browser.set_selenium_implicit_wait(3)

        self.window_size = self.browser.get_window_size()
        self.img_directory = 'output/imgs'

    def scrape(self) -> None:
        """
        Scrape all news articles based on the given search term, process the data, and save it to an Excel file.

        Parameters:
            self (MainScrapper): The instance of the MainScrapper class.

        Returns:
            None
        """
        try:
            self.search_news()

            WebDriverWait(self.browser.driver, 2).until(
                EC.presence_of_element_located((By.ID, 'search-sort-option'))
            )

            self.save_payload_to_excel(
                self.process_news_payload(
                    news_list=self.get_news_list_by_date()
                )
            )

        except Exception as error:
            logging.error(
                f'Unexpected error while trying to perform scraping: {error}'
            )
            self.browser.close_all_browsers()
            raise Exception from error

        finally:
            self.browser.close_all_browsers()

    def get_news_image(self, img_src: str, idx: int) -> str:
        """
        Download a news image from the given source URL and return the file name.

        Args:
            img_src (str): The source URL of the image.
            idx (int): The index of the image in the list of articles.

        Returns:
            str: The file name of the downloaded image.
        """
        if not os.path.exists(self.img_directory):
            os.makedirs(self.img_directory)
            logging.info('-- Image directory created')
        
        resp = requests.get(img_src, timeout=1.5)

        if resp.status_code == 200:
            img_file_name = f'img_{idx}.png'

            with open(f'output/imgs/{img_file_name}', 'wb') as f:
                f.write(resp.content)
                logging.info(f'-- Image {img_file_name} saved')

        else:
            logging.warning(
                f'-- Unable to fetch image from source: {resp.status_code} {resp.content}'
            )
            img_file_name = 'Unavailable'
        
        return img_file_name

    def search_news(self) -> None:
        """
        Perform a search on the target website using the specified search term.
        """
        self.browser.set_window_size(*self.window_size)

        if self.browser.get_window_size()[0] > 992:
            self.browser.click_element(ENABLE_SEARCH_BUTTON_BIG)
            self.browser.input_text(SEARCH_INPUT_BIG, self.search_phrase)
        
        else:
            self.browser.click_element(ENABLE_SEARCH_BUTTON_SMALL)
            self.browser.input_text(SEARCH_INPUT_SMALL, self.search_phrase)

        self.browser.click_button(SEARCH_BUTTON_ID)

    def get_news_list_by_date(self) -> list[WebElement]:
        """
        Get a list of news articles sorted by date from the target website.

        Returns:
            list: A list of Selenium web elements representing the news articles.
        """
        self.browser.select_from_list_by_value(SEARCH_SORT_OPTIONS, 'date')

        WebDriverWait(self.browser.driver, 3).until(
            EC.presence_of_element_located((By.XPATH, MAIN_CONTENT.replace('xpath:', '')))
        )

        while self.browser.does_page_contain_element(LOAD_MODE_BUTTON):
            self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
            self.browser.click_element(LOAD_MODE_BUTTON)

        return self.browser.find_elements(MAIN_CONTENT)

    def process_news_payload(self, news_list: list[WebElement]) -> list[dict]:
        """
        Process the list of news articles and return the data payload.

        Args:
            news_list (list): A list of Selenium web elements representing the news articles.

        Returns:
            list of dict: A list of dictionaries containing the processed news data.
        """
        _news_payload = []

        for i, element in enumerate(news_list):
            try:
                title = self.browser.find_element(NEWS_TITLE_CLASS, parent=element).text
                description = self.browser.find_element(NEWS_DESCRIPTION_CLASS, parent=element).text.split('...')
                description = description[len(description) - 2].strip()
                date = self.convert_string_to_datetime(
                    self.browser.find_element(locator=NEWS_FOOTER_CLASS, parent=element).text
                )

                if date:
                    if date.month >= self.month_limit:
                        _news_payload.append(
                            {
                                'title': title,
                                'date': date.strftime('%d %b %Y'),
                                'description': description,
                                'search_term_occurrence': title.count(self.search_phrase) + description.count(self.search_phrase),
                                'contains_money': self.contains_money(title) or self.contains_money(description),
                                'img_file_name': self.get_news_image(
                                    img_src=self.browser.find_element(NEWS_IMAGE_CLASS, parent=element).get_attribute('src'),
                                    idx=i
                                )
                            }
                        )
                    else:
                        break

            except Exception as error:
                logging.warning(f'-- Error while processing news element {error}')

        return _news_payload

    @staticmethod
    def save_payload_to_excel(payload: list[dict]) -> None:
        """
        Save the processed news data to an Excel file.

        Args:
            payload (list of dict): The list of dictionaries containing the processed news data.
        """
        excel = Files()
        file_name = 'output/output.xlsx'

        if not os.path.exists(file_name):
            excel.create_workbook(file_name)
        else:
            excel.open_workbook(file_name)

        keys = payload[0].keys()

        for col_num, key in enumerate(keys, start=1):
            excel.set_cell_value(1, col_num, key)

        for row_num, dictionary in enumerate(payload, start=2):
            for col_num, (key, value) in enumerate(dictionary.items(), start=1):
                excel.set_cell_value(row_num, col_num, value)

        excel.save_workbook(file_name)
        excel.close_workbook()

    @staticmethod
    def contains_money(text: str) -> bool:
        """
        Check if the given text contains any monetary values.

        Args:
            text (str): The text to check for monetary values.

        Returns:
            bool: True if the text contains monetary values, False otherwise.
        """
        patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{1,2})?',
            r'\b\d+(?:,\d{3})*\s+dollars\b',
            r'\b\d+(?:,\d{3})*\s+USD\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False

    @staticmethod
    def convert_string_to_datetime(date_string: str) -> dt:
        """
        Convert a date string to a datetime object.

        Args:
            date_string (str): The date string to convert.

        Returns:
            datetime: The converted datetime object, or None if the conversion fails.
        """        
        date_patterns = [
            r'Published On (\d{1,2} \w{3} \d{4})',
            r'Last update (\d{1,2} \w{3} \d{4})'
        ]

        if date_string.strip():
            for pattern in date_patterns:
                match = re.search(pattern, date_string)
                if match:
                    try:
                        return dt.strptime(match.group(1), '%d %b %Y')
                    
                    except ValueError as e:
                        logging.warning(f"Error parsing date: {e}")
                return None
