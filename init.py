import os
import telegram
import configparser
from itunes_app_scraper.scraper import AppStoreScraper

config = configparser.RawConfigParser(allow_no_value=True)
config.optionxform = lambda option: option
config.read("./config/config.ini", encoding="utf-8")
bot_token = config["TELEGRAM"]["bot_token"]
chat_id = config["TELEGRAM"]["Telegram_ID"]
show_image = config["OPTION"]["show_game_image"]
refresh_mins = int(config["OPTION"]["refresh_mins"])
program_name = config["VERSION"]["program_name"]
program_version = config["VERSION"]["program_version"]
bot = telegram.Bot(token=bot_token)
client_id = "71b963c1b7b6d119"
frds_status_file = "./config/frds_status.json"
path = "./log"
if not os.path.exists(path):
    os.makedirs(path)


def get_app_version():
    try:
        scraper = AppStoreScraper()
        app_id = scraper.get_app_ids_for_query("Nintendo Switch Online")[0]
        app_details = scraper.get_app_details(app_id)
        app_latest_version = app_details.get("version")
        return app_latest_version
    except Exception as Error:
        print(f"get_app_version {Error}" % Error)
        return app_version


app_version = get_app_version()


def request_headers_com():
    app_version = get_app_version()
    headers = {
        "Host": "accounts.nintendo.com",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US;q=1.0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": f"Coral/{app_version} (com.nintendo.znca; build:4882; iOS 17.2.1) NASDK/{app_version}",
    }
    return headers


def request_headers_net():
    app_version = get_app_version()
    headers = {
        "Host": "api-lp1.znc.srv.nintendo.net",
        "Accept": "application/json",
        "Accept-Language": "en-US;q=1.0",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": f"Coral/{app_version} (com.nintendo.znca; iOS 17.2.1)",
        "X-Platform": "iOS",
        "X-ProductVersion": f"{app_version}",
    }
    return headers


def send_message(text):
    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
    )
