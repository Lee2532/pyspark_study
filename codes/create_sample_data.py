"""
샘플 데이터 생성을 위한 파일
 * 트위치 스트리머 채팅 수집

"""
import pandas as pd

"""
트위치 웹드라이버를 통한 데이터 수집 (API는 미사용)
입력한 채널 기반으로 여러개의 웹드라이버를 띄워서 수집
"""
import logging
import time
from dataclasses import asdict
from datetime import datetime

import ray
from bs4 import BeautifulSoup
from selenium import webdriver

from codes.models.ChatModel import CHATMODEL
from common.DBConn import DBCONN


@ray.remote
class TwitchChat:
    """트위치 채팅 수집"""

    def __init__(self, channel: str):
        self.channel = channel
        self.url = f"""https://www.twitch.tv/{self.channel}"""

    def _driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless=new")
        options.add_argument(
            "--blink-settings=imagesEnabled=false"
        )  # 브라우저에서 이미지 로딩을 하지 않습니다.
        options.add_argument("incognito")  # 시크릿 모드의 브라우저가 실행됩니다.
        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")  # 이거인가

        driver = webdriver.Remote(
            "http://localhost:4444/wd/hub",
            options=options,
        )
        return driver

    def is_duplicate(self, existing_data: list, new_data: dict):
        for item in existing_data:
            if item['nickname'] == new_data['nickname'] and item['message'] == new_data['message']:
                return True
        return False

    def twitch_chat(self):
        driver = self._driver()
        driver.get(self.url)
        logging.info(f"goto {self.url}")

        result = []
        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            for i in soup.select(
                "section > div > div > div > div.scrollable-area > div.simplebar-scroll-content > div > div > div"
            ):
                try:
                    user_id = i.get("data-a-user", "")
                    nickname = i.select_one("span.chat-author__display-name").get_text()
                    message = i.select_one("span.text-fragment").get_text()

                    msg = {
                        "user_id": user_id,
                        "nickname": nickname,
                        "message": message,
                        "channel": self.channel,
                        "create_time": str(datetime.now()),
                    }

                    data = asdict(CHATMODEL(**msg))
                    logging.info(data)
                    if not self.is_duplicate(result, data):
                        result.append(data)

                except Exception as e:
                    logging.info(e)

            if len(result) > 500:
                # data save
                DBCONN().insert_df("twitch", pd.DataFrame(result))
                result = []
                time.sleep(2)

            time.sleep(0.5)


if __name__ == "__main__":
    ray.init()
    channels = [
        "handongsuk",
        "woowakgood",
        "hanryang1125",
        "zilioner",
        "kimdduddi",
        "tmxk319",
        "ayatsunoyuni_stellive",
    ]

    tasks = [TwitchChat.remote(channel) for channel in channels]
    logging.info(tasks)
    # 모든 작업을 동시에 실행
    ray.get([task.twitch_chat.remote() for task in tasks])
    ray.shutdown()
