# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import pandas as pd
import datetime as dt

def scrape_all():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image_urls" : hemisphere_data(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data



# # Parse the title & news paragraph
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p


# # Get the full image
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    #Anytime you load a new page you must parse it 
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:    
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url


# # Get Mars Facts

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    #Assign columns and a set of index of df 
    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_data(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # HTML Object
    html_hemispheres = browser.html

    # Parse HTML with Beautiful Soup
    astro_soup = soup(html_hemispheres, 'html.parser')

    items= astro_soup.find_all("div", class_="item")

    main_hemi_url = "https://astrogeology.usgs.gov"

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in items:
        #Find the title
        title = astro_soup.find('h3').text
        
        #Find the partial url for one of the hemispheres
        partial_img_url = astro_soup.find('a', class_='itemLink product-item')['href']
        
        #Find the full url for that hemispgere
        full_img_url = main_hemi_url + partial_img_url
        
        #Visit the url for that hemisphere
        browser.visit(full_img_url)
        
        #HTML object
        partial_img_html = browser.html
        
        #Parse HTML
        hemi_soup = soup(partial_img_html, 'html.parser')
        
        #Retrieve image link
        img_url = main_hemi_url + hemi_soup.select_one("img.wide-image").get("src")
        
        #Append the retrieved information into the list 
        
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())






