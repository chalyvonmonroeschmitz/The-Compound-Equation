#!/usr/bin/python
import asyncio
import os
import pytesseract
from classes.scraper import Scraper
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = os.getcwd() + r"\.lib\tesseract4win64\x64\tesseract.exe"


class Archiver(Scraper):
    def __init__(self):
        self.init()

    def init(self):
        # watson image visualizer
        # watson nlu
        self.nlu_authenticator = IAMAuthenticator('y8j8DDb68p7HiUVZIqNP1Fjha3mGEXrQ4HPRhxKrk_9-')
        self.watson_nlu = NaturalLanguageUnderstandingV1(
            version='2020-08-01',
            authenticator=self.nlu_authenticator
        )
        self.watson_nlu.set_service_url("https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/7ebfc6d1-a484-4bde-8ae6-e04b24f78e72")


async def main():
    print("Archiver")


if __name__ == "__main__":
    # loop to keep main thread running
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
