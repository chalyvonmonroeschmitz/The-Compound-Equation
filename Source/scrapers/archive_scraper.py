#!/usr/bin/python
import asyncio
import datetime
import json
import os
import re
import skimage as ski
import numpy as np
from urllib.parse import urlparse, unquote
from skimage.util import img_as_ubyte
import imageio.v3 as iio
from ibm_cloud_sdk_core import ApiException
from ibm_watson.natural_language_understanding_v1 import EntitiesOptions, RelationsOptions, Features, KeywordsOptions
from selenium.common import InvalidArgumentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from classes.archiver import Archiver
from selenium.webdriver.common.by import By
# begin pytesseract config
from pytesseract import pytesseract
# Configure tesseract path similarly to Archiver for standalone runs
# Order: env var, repo-local .lib, Program Files
_env = os.environ.get("TESSERACT_CMD") or os.environ.get("TESSERACT_PATH")
if _env and os.path.exists(_env):
    pytesseract.tesseract_cmd = _env
else:
    _here = os.path.abspath(os.path.dirname(__file__))
    _local = os.path.join(_here, ".lib", "tesseract4win64", "x64", "tesseract.exe")
    if os.path.exists(_local):
        pytesseract.tesseract_cmd = _local
    else:
        _common = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        if os.path.exists(_common):
            pytesseract.tesseract_cmd = _common
# end pytesseract config


class Google_Scraper(Archiver):
    def __init__(self):
        self.filepath = os.getcwd() + "/Data"
        super().__init__()

    async def google_scraper(self, driver, search_term, domain_region=""):
        driver.command_executor.set_timeout(300)  # seconds
        working_path = self.filepath + f"/{search_term}-{str(datetime.date.today())}"
        os.makedirs(working_path, exist_ok=True)
        driver.get(url=f"https://www.google.com{domain_region}/search?q={search_term}")
        await asyncio.sleep(2)
        actions = ActionChains(driver)
        actions.send_keys(search_term).send_keys(Keys.RETURN).perform()
        print("Starting search capture... Please Verify Google Captcha Manually within 20 seconds")

        # Countdown loop for 20 seconds
        for remaining in range(20, 0, -1):
            print(f"Time remaining: {remaining} seconds", end="\r")
            await asyncio.sleep(1)

        print("\nCapturing search data...")
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
        driver.command_executor.set_timeout(300)  # seconds
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

        try:
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
        except ApiException as ex:
            print("Method failed with status code " + str(ex.code) + ": " + ex.message)
            data_set = {
                "document": title,
                "url": url,
                "entities": entities_js,
                "relations": relations_js,
                "keywords": keywords_js
            }
        except Exception as e:
            print(f"NLU text analysis failed: {e}")
            data_set = {
                "document": title,
                "url": url,
                "entities": entities_js,
                "relations": relations_js,
                "keywords": keywords_js
            }

        # Helper to sanitize and truncate filename base
        def short_name(name: str, max_len: int = 12) -> str:
            # remove leading/trailing whitespace and dots, then truncate
            cleaned = name.strip().strip('.')
            return cleaned[:max_len] if len(cleaned) > max_len else cleaned

        # ... inside your method where `title`, `working_path`, and `data_set` exist ...

        safe_base = short_name(title)

        # First JSON (text NLU)
        out_path = os.path.join(working_path, f"{safe_base}.json")
        with open(out_path, "w", encoding="utf-8") as fileOut:
            fileOut.write(json.dumps(data_set))
        print(f"{title} NLU extraction complete! Running NLU Image Extraction...")

        # Later, for images data JSON
        images_base = short_name(title)
        img_out_path = os.path.join(working_path, f"{images_base}-image_nlu.json")
        with open(img_out_path, "w", encoding="utf-8") as fileOut:
            fileOut.write(json.dumps({
                "document": f"{title}_IMAGES_DATA",
                "url": url,
                "entities": entities_js,
                "relations": relations_js,
                "keywords": keywords_js,
            }))
        print(title + " NLU extraction complete! Running NLU Image Extraction...")

        if len(images) > 0:
            for idx, i in enumerate(driver.find_elements(By.XPATH, "//img")):
                try:
                    src = i.get_attribute("src")

                    # Skip obviously unsupported sources
                    if not src or src.startswith("data:image/svg"):
                        img = ski.io.imread(src)
                        img = normalize_image_array(img)
                        # Ensure write-compatible dtype (uint8/uint16). If float, scale to uint8
                        if img.dtype not in (np.uint8, np.uint16):
                            img = img_as_ubyte(img)  # handles 0..1 floats safely

                        # Build a safe filename
                        parsed = urlparse(src)
                        base = os.path.basename(parsed.path)
                        base = unquote(base)
                        if not base:
                            base = f"{title}_{idx}.png"

                        # Strip query/fragment and illegal Windows characters
                        name, ext = os.path.splitext(base)
                        if not ext:
                            ext = ".png"  # default to PNG
                        safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", f"{name}{ext}")
                        out_path = os.path.join(working_path, safe_name)

                        # Prefer Pillow writer via imageio to avoid OpenCV writer errors
                        iio.imwrite(out_path, img)
                        continue

                    # OCR and NLU
                    extracted_text = pytesseract.image_to_string(img)
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
                    # Will catch path issues and writer backend problems
                    print("Write failed: " + str(OSe))
                    continue
                except ValueError as ve:
                    print(str(ve))
                    continue
                except AttributeError as aerr:
                    print(str(aerr))
                    continue
                except TypeError as terr:
                    print(str(terr))
                    continue

        try:
            data_set = {
                "document": title + "_IMAGES_DATA",
                "url": url,
                "entities": entities_js,
                "relations": relations_js,
                "keywords": keywords_js
            }
            fileOut = open(working_path + '/' + title.strip('./') + "-image_nlu.json", "w")
            fileOut.write(json.dumps(data_set))
            fileOut.close()
            print(title + " extraction complete!")
        except InvalidArgumentException as iae:
            print(str(iae))

    async def scrape_from_file(self, driver, urls_file: str, working_folder: str | None = None):
        """
        Read URLs from a text file and run `scrape_page` for each.

        Args:
            driver: Selenium WebDriver instance (already configured/logged in as needed).
            urls_file: Path to a text file with one URL per line. Lines starting with '#' are ignored.
            working_folder: Optional custom name for the output folder; defaults to the file's basename.
        """
        if not os.path.exists(urls_file):
            raise FileNotFoundError(f"URLs file not found: {urls_file}")

        # Derive a working directory similar to google_scraper
        base_name = working_folder or os.path.splitext(os.path.basename(urls_file))[0]
        working_path = os.path.join(self.filepath, f"{base_name}-{str(datetime.date.today())}")
        os.makedirs(working_path, exist_ok=True)

        seen: set[str] = set()
        driver.command_executor.set_timeout(300)  # seconds
        with open(urls_file, "r", encoding="utf-8") as fh:
            for raw in fh:
                url = raw.strip()

                # Skip blanks and comments
                if not url or url.startswith("#"):
                    continue

                # Basic URL check; keep it simple and non-invasive
                if not re.match(r"^https?://", url, flags=re.IGNORECASE):
                    print(f"Skipping non-HTTP URL: {url}")
                    continue

                if url in seen:
                    # Deduplicate within the same run
                    continue
                seen.add(url)

                try:
                    await self.scrape_page(driver, url, working_path)
                    # Optional: be polite to servers / avoid rate limiting
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
                    continue

        print("File-driven NLU extraction completed!")

def normalize_image_array(arr):
    arr = np.asarray(arr)

    # Drop a leading singleton dimension (batch/frame) if present
    if arr.ndim == 4 and arr.shape[0] == 1:
        arr = np.squeeze(arr, axis=0)

    # If still 4D, pick the first frame (HxWxCxF or FxHxWxC); adjust as needed
    if arr.ndim == 4:
        # Assume (frames, H, W, C)
        arr = arr[0]

    # If channels dimension is weird, try to coerce to RGB
    if arr.ndim == 3 and arr.shape[-1] not in (1, 3, 4):
        # Truncate or broadcast to 3 channels as a fallback
        if arr.shape[-1] > 3:
            arr = arr[..., :3]
        else:
            # Repeat the single channel to RGB
            arr = np.repeat(arr, 3, axis=-1)

    # Ensure write-friendly dtype
    if arr.dtype not in (np.uint8, np.uint16):
        arr = img_as_ubyte(arr)

    return arr

async def main():
    search = ""
    scraper = Google_Scraper()
    driver = scraper.initChromeDriver(False)
    await scraper.google_scraper(driver, search)


if __name__ == "__main__":
    # Loop to keep main thread running
    asyncio.run(main())
