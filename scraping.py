import requests
from requests.exceptions import RequestException

class Scraper():
    def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0'}
        self. data_json = {}

    def scrap_items(self):
        try:
            response = requests.get('https://dom.ria.com/node/searchEngine/v2/?addMoreRealty=false&excludeSold=1&category=1&realty_type=2&operation=1&state_id=0&city_id=0&in_radius=0&with_newbuilds=0&price_cur=1&wo_dupl=0&complex_inspected=0&sort=inspected_sort&period=0&notFirstFloor=0&notLastFloor=0&with_map=0&photos_count_from=0&with_video_only=0&firstIteraction=false&fromAmp=0&market=3&type=list&client=searchV2&polygonAreaId=0&operation_type=1&page=0&ch=242_239%2C247_252&mobileStatus=1'
                                    , headers=self.headers)
            response.raise_for_status()
            data = response.json()
            items_id = data.get('items')
            pages = []
            for item in items_id:
                pages.append(f'https://dom.ria.com/realty/data/{item}?lang_id=4&key=')
            return pages
        except RequestException as e:
            return f'An error occurred: {e}'

    def get_realty_data(self):
        pages = self.scrap_items()
        if isinstance(pages, str):
            return []
        details = []
        for data in pages:
            try:
                response = requests.get(data, headers=self.headers, timeout=10)
                response.raise_for_status()
                details.append(response.json())
            except RequestException as e:
                continue
        return details
