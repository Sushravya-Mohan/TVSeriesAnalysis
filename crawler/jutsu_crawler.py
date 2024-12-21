import scrapy
from bs4 import BeautifulSoup


class BlogSpider(scrapy.Spider):
    # Define the spider's name and starting URLs
    name = 'narutospider'
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        """
        The main parsing method that is called for each page to extract links to individual jutsu pages.

        It iterates over the jutsu list and sends requests to each jutsu's page for further scraping.
        """
        # Extract all the jutsu links from the current page (first .smw-columnlist-container element)
        for href in response.css('.smw-columnlist-container')[0].css("a::attr(href)").extract():
            # For each jutsu link, send a request to its page and call `parse_jutsu` to process it
            extracted_data = scrapy.Request("https://naruto.fandom.com" + href, callback=self.parse_jutsu)
            yield extracted_data  # Yield the request so that Scrapy can handle it

        # Look for the "next page" link to continue crawling through the results
        for next_page in response.css('a.mw-nextlink'):
            yield response.follow(next_page, self.parse)  # Follow the next page link recursively

    
    def parse_jutsu(self, response):
        """
        Parse the individual jutsu page to extract details like name, type, and description.

        This method is called when the spider crawls to an individual jutsu page.
        """
        # Extract the jutsu name from the page's title element
        jutsu_name = response.css("span.mw-page-title-main::text").extract()[0]
        jutsu_name = jutsu_name.strip()  # Clean up the jutsu name by removing any surrounding whitespace

        # Extract the main content of the jutsu page (all content inside the div with class 'mw-parser-output')
        div_selector = response.css("div.mw-parser-output")[0]
        div_html = div_selector.extract()  # Get the raw HTML of the content

        # Use BeautifulSoup to parse and navigate the raw HTML content
        soup = BeautifulSoup(div_html).find("div")  # Find the main content div

        # Initialize a variable to store the jutsu type (classification)
        jutsu_type = ""
        # Check if there's an aside element which may contain the jutsu classification
        if soup.find("aside"):
            aside = soup.find("aside")  # Find the aside element (if it exists)

            # Loop through each div with class 'pi-data' inside the aside to extract classification info
            for cell in aside.find_all("div", {"class" : "pi-data"}):
                if cell.find("h3"):  # Check if the div contains an <h3> (section header)
                    cell_name = cell.find("h3").text.strip()  # Get the section header text (e.g., "Classification")
                    if cell_name == "Classification":  # If the section is for "Classification"
                        jutsu_type = cell.find("div").text.strip()  # Get the jutsu type (classification) text

        # Remove the aside section from the content as it's already processed
        soup.find("aside").decompose()

        # Extract the jutsu description (everything after the aside section)
        jutsu_description = soup.text.strip()  # Get the clean text of the content
        jutsu_description = jutsu_description.split("Trivia")[0].strip()  # Remove any "Trivia" section if it exists

        # Return the extracted data as a dictionary for storage or further processing
        return dict(
            jutsu_name=jutsu_name,  # Jutsu name
            jutsu_type=jutsu_type,  # Jutsu type (classification)
            jutsu_description=jutsu_description  # Jutsu description (main content)
        )
