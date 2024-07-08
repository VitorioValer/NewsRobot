"""
This module defines the locators for various elements on the target website, used in conjunction with the MainScrapper class.

Locators:
- ENABLE_SEARCH_BUTTON_BIG: XPath for the search button in the large screen layout.
- SEARCH_INPUT_BIG: Class for the search input field in the large screen layout.
- ENABLE_SEARCH_BUTTON_SMALL: XPath for the search button in the small screen layout.
- SEARCH_INPUT_SMALL: XPath for the search input field in the small screen layout.
- SEARCH_BUTTON_ID: ID for the search button.
- SEARCH_SORT_OPTIONS: ID for the search sort options dropdown.
- MAIN_CONTENT: XPath for the main content area containing news articles.
- LOAD_MODE_BUTTON: XPath for the button to load more articles.
- NEWS_TITLE_CLASS: Class for the news article title element.
- NEWS_DESCRIPTION_CLASS: Class for the news article description element.
- NEWS_FOOTER_CLASS: Class for the news article footer element.
- NEWS_IMAGE_CLASS: Class for the news article image element.
"""
ENABLE_SEARCH_BUTTON_BIG = 'xpath://*[@id="root"]/div/div[1]/div[1]/div/header/div[4]/div[2]/button'
SEARCH_INPUT_BIG = 'class=search-bar__input'

ENABLE_SEARCH_BUTTON_SMALL = 'xpath://header/div[3]/button'
SEARCH_INPUT_SMALL = 'xpath://form/div[1]/input'

SEARCH_BUTTON_ID = 'Search'
SEARCH_SORT_OPTIONS = 'id=search-sort-option'

MAIN_CONTENT = 'xpath://*[@id="main-content-area"]/div[2]/div[2]/article'
LOAD_MODE_BUTTON = 'xpath://*[@id="main-content-area"]/div[2]/div[2]/button'

NEWS_TITLE_CLASS = 'class=gc__title'
NEWS_DESCRIPTION_CLASS = 'class=gc__body-wrap'
NEWS_FOOTER_CLASS = 'class=gc__footer'
NEWS_IMAGE_CLASS = 'class=gc__image'
