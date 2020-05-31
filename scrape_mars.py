from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "./chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    listings = {}

    ## Scrape the relevant news information
    news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    #browser.visit(url)
    #html = browser.html
    news_html = requests.get(news_url).text
    news_soup = bs(news_html, "html.parser")
    listings["news_title"] = news_soup.find('div', class_='content_title').get_text()
    listings["news_description"] = news_soup.find('div',class_='rollover_description_inner').get_text()
    
    ## Scrape relevant Mars image
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    browser.click_link_by_partial_text('FULL IMAGE')
    current_html = browser.html
    image_soup = bs(current_html,'html.parser')
    partial_img_url = image_soup.find('img',class_='fancybox-image')["src"]
    listings["featured_image_url"] = "https://www.jpl.nasa.gov" + partial_img_url

    ## Scrape relevant Weather information  
    driver = webdriver.Chrome()
    driver.get('https://twitter.com/marswxreport?lang=en')
    weather_html = driver.page_source
    driver.close()
    twitter_soup = bs(weather_html, 'html.parser')
    latest_tweets = twitter_soup.find_all('span', class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')
    tweet_list = []
    for tweet in latest_tweets:
        tweet_list.append(tweet.text)
    keyword = 'InSight'
    weather_tweet = [i for i in tweet_list if keyword in i] 
    listings['mars_weather'] = weather_tweet[0]

    ## Scrape relevant Mars facts
    mars_facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(mars_facts_url)
    mars_df = tables[0]
    mars_df.columns = ['Description','Value']
    listings['mars_description'] = mars_df['Description']
    listings['mars_value'] = mars_df['Value']

    ## Scrape relevant Mars Hemispheres data
    browser = init_browser()
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemisphere_url)
    hemisphere_html = browser.html
    hemisphere_soup = bs(hemisphere_html, 'html.parser')
    hemisphere_img_class = hemisphere_soup.find_all('div', class_='item')

    main_url = "https://astrogeology.usgs.gov"
    hemisphere_image_urls = []

    for i in hemisphere_img_class:
        img_title = i.find('h3').text
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
        browser.visit(main_url+partial_img_url)
        img_html = browser.html
        img_soup = bs(img_html, 'html.parser')
        individual_img_partial_url = img_soup.find('img', class_='wide-image')['src']
        individual_img_url = main_url + individual_img_partial_url
        hemisphere_image_urls.append({"title" : img_title, "img_url" : individual_img_url})
        browser.quit()
    listings['hemisphere_title'] = hemisphere_image_urls['title']
    listings['hemisphere_img'] = hemisphere_image_urls['img_url']

    return listings
