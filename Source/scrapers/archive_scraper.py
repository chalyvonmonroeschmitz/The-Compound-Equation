#!/usr/bin/python
import asyncio
import datetime
import json
import os
import sys
import re
from time import sleep
from urllib.request import urlopen
from PIL import Image
from ibm_cloud_sdk_core import ApiException
from ibm_watson.natural_language_understanding_v1 import EntitiesOptions, RelationsOptions, Features, KeywordsOptions
from pytesseract import pytesseract
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from classes.archiver import Archiver
from selenium.webdriver.common.by import By

class Google_Scraper(Archiver):
    def __init__(self):
        self.filepath = os.getcwd() + "/Data"
        super().__init__()

    async def google_scraper(self, driver, search_term, domain_region=""):
        working_path = self.filepath + f"/{search_term}-{str(datetime.date.today())}"
        os.makedirs(working_path, exist_ok=True)
        driver.get(url=f"https://www.google.com{domain_region}/search?q={search_term}")
        await asyncio.sleep(2)
        actions = ActionChains(driver)
        actions.send_keys(search_term).send_keys(Keys.RETURN).perform()
        await asyncio.sleep(20)
        hrefs = []

        while True:
            try:
                found_pages = [driver.find_elements(By.XPATH, "//*[@id='rso']//a")]
                for l in found_pages[0]:
                    hrefs += [l.get_attribute("href")]
            except NoSuchElementException as nse:
                print(nse)
                continue

            try:
                next = driver.find_element(By.XPATH, ".//*[@id='pnnext']").get_attribute("href")
                driver.get(next)
                await asyncio.sleep(2)
            except NoSuchElementException as nse:
                print(nse)
                break

        # Start going through pages
        fileOut = working_path + '/' + search_term + str(datetime.date.today()) + ".txt"
        with open(fileOut, "w") as outfile:
            outfile.write("\n".join(hrefs))

        completed = []
        for r in hrefs:
            if r not in completed:
                completed.append(r)
                await self.scrape_page(driver, r, working_path)
            else:
                continue

        print("Search NLU Extraction completed! Exiting Program!")

    async def scrape_page(self, driver, url, working_path):
        driver.get(url)
        body = driver.find_element(By.XPATH, "//body")
        html = driver.find_element(By.XPATH, "//html")
        extracted_text = body.text
        images = body.find_elements(By.XPATH, "//img")
        title = re.findall("([^/]+)(?=[^/]*/?$)", url)[0]
        title = re.sub(r"[^a-zA-Z0-9]", "", title)
        keywords_js = []
        relations_js = []
        entities_js = []

        if len(extracted_text) > 0:
            entities_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                entities=EntitiesOptions(sentiment=True))).get_result())]
            relations_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                relations=RelationsOptions())).get_result())]
            keywords_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                keywords=KeywordsOptions(sentiment=True, emotion=True))).get_result())]
            data_set = {
                "document": title,
                "url": url,
                "entities": entities_js,
                "relations": relations_js,
                "keywords": keywords_js
            }

            fileOut = open(working_path + '/' + title.strip('.') + ".json", "w")
            fileOut.write(json.dumps(data_set))
            fileOut.close()
            print(title + " NLU extraction complete! Running NLU Image Extraction...")

        if len(images) > 0:
            for i in driver.find_elements(By.XPATH, "//img"):
                try:
                    img = Image.open(urlopen(i.get_attribute("src")))
                    img.save(working_path + "/" + i.get_attribute("src").split("/")[-1])
                    extracted_text = pytesseract.image_to_string(Image.open(urlopen(i.get_attribute("src"))))
                    await asyncio.sleep(3)
                    entities_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                        entities=EntitiesOptions(sentiment=True))).get_result())]
                    relations_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                        relations=RelationsOptions())).get_result())]
                    keywords_js += [json.dumps(self.watson_nlu.analyze(text=extracted_text, features=Features(
                        keywords=KeywordsOptions(sentiment=True, emotion=True))).get_result())]
                except ApiException as ex:
                    print("Method failed with status code " + str(ex.code) + ": " + ex.message)
                    continue
                except OSError as OSe:
                    print("Method failed with status code " + str(OSe))
                    continue
                except ValueError as ve:
                    print(str(ve))
                    continue

        data_set = {
            "document": title + "_IMAGES_DATA",
            "url": url,
            "entities": entities_js,
            "relations": relations_js,
            "keywords": keywords_js
        }
        fileOut = open(working_path + '/' + title.strip('.') + "-image_nlu.json", "w")
        fileOut.write(json.dumps(data_set))
        fileOut.close()
        print(title + " extraction complete!")

async def main():
    search = ""
    scraper = Google_Scraper()
    driver = scraper.initChromeDriver(False)
    await scraper.google_scraper(driver, search)


if __name__ == "__main__":
    # Loop to keep main thread running
    asyncio.run(main())