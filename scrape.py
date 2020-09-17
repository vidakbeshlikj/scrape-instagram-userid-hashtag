import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import random
import csv

class Scraper:

    def __init__(self):
        self.instagram_url = "https://www.instagram.com/{}"
        self.driver = None

        with open("user_agents.txt", "r") as f:
            user_agents = f.readlines()
            self.user_agents = [i.strip().strip("\n") for i in user_agents]

        self.output = None

    def write_csv(self,file,row):
        with open(file, "a", newline='', encoding="utf-8") as f:
            csv_writer = csv.writer(f,delimiter=',',quotechar='"')
            csv_writer.writerow(row)

    def get_driver(self):

        # caps = DesiredCapabilities().CHROME       
        # caps["pageLoadStrategy"] = "none"

        user_agent = random.choice(self.user_agents)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-agent="+str(user_agent))
        # chrome_options.add_argument("proxy-server="+str(next(self.proxypool)))
        chrome_options.add_argument("headless")
        chrome_options.add_argument("no-sandbox")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-logging")
        chrome_options.add_argument("log-level=3")
        
        self.driver = webdriver.Chrome(options=chrome_options,executable_path="c_driver/chromedriver.exe")

    def setup(self):
        self.output = os.path.join(os.getcwd(), "output.csv")
        self.write_csv(self.output,["ID","Data Type","Username","Number of followers", "Number of following", "Description", "Number of Likes","URL"])

    def scrape_userid(self):
        self.get_driver()
        username = "ronaldinho"
        url = self.instagram_url.format(username)
        self.driver.get(url)

        posts = self.driver.find_elements_by_tag_name("a")
        posts = [post for post in posts if "https://www.instagram.com/p/" in post.get_attribute("href")]
        print("Post links fetched")

        num_followers = self.driver.find_elements_by_class_name('g47SY')[1].text
        num_following = self.driver.find_elements_by_class_name('g47SY')[2].text


        print("Iterating trough posts...")
        id = 0
        for post in posts:
            id+=1
            data_type = ""
            description = ""


            post_url = post.get_attribute("href")
            self.get_driver()
            self.driver.get(post_url)
            print("Scraping: {}".format(post_url))

            #fetching description
            try:
                desc = self.driver.find_element_by_xpath("//div[@class='C4VMK']/span")
            except Exception as e:
                # Description is empty
                print("Description is empty")
            else:
                description = desc.text


            #VIDEO CHECK
            video_button = self.driver.find_elements_by_class_name('tWeCl')
            if len(video_button) != 0:
                print("VIDEO")
                data_type = "Video"
                num_likes = ""
                row = [id,data_type,username,num_followers,num_following,description,num_likes,post_url]
                self.write_csv(self.output,row)
                continue

            num_likes = self.driver.find_element_by_xpath("//button[@class='sqdOP yWX7d     _8A5w5    ']").text.rstrip(" likes")

            # SLIDESHOW CHECK
            slideshow = self.driver.find_elements_by_xpath("//div[@class='    coreSpriteRightChevron  ']")
            if len(slideshow) != 0:
                print("SLIDESHOW")
                data_type = "Slideshow"
                row = [id,data_type,username,num_followers,num_following,description,num_likes,post_url]
                self.write_csv(self.output,row)
                continue


            #IMAGE
            

            data_type = "Image"
            row = [id,data_type,username,num_followers,num_following,description,num_likes,post_url]
            self.write_csv(self.output,row)

            image = self.driver.find_element_by_xpath("//div[@class='KL4Bh']/img").get_attribute("src")
            print(image)



if __name__=="__main__":
    s = Scraper()
    s.setup()
    s.scrape_userid()
