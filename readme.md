# NSO-BFF-Notification
When me and my BFF play together every time but have no contact(except NSO).

# How to run

* Clone repository 

  ```
  git clone https://github.com/pufflope/NSO-BFF-Notification.git
  ```


* Install requirements 

  ```
  pip install -r requirements.txt
  ```

* Mortify `config.ini`

* Send a test message to Telegram to check configration.

  ```
  python3 test_send_msg.py
  ```

* Run

  ```
  python3 nso_bff.py
  ```


# Note

Using this program means your Nintendo account's access_token and id_token will be sent to [a third-party server](https://github.com/imink-app/f-API), in order to get necessary parameters. Or you can self-host on your server. For more detail, see [this discussion](https://github.com/samuelthomas2774/nxapi/discussions/10)


# Credits

Thanks:
* [imink-app/f-API](https://github.com/imink-app/f-API) for providing an API to get `f` parameters.
* [tedkim7/nxsence](https://github.com/tedkim7/nxsence/) & [samuelthomas2774/nxapi](https://github.com/samuelthomas2774/nxapi) & [frozenpandaman/s3s](https://github.com/frozenpandaman/s3s) & [zeroday0619/Nintendo_Switch_Online_API_Bridge](https://github.com/zeroday0619/Nintendo_Switch_Online_API_Bridge) 
  for identify parameters and the method of create parameters.
* [digitalmethodsinitiative/itunes-app-scraper](https://github.com/digitalmethodsinitiative/itunes-app-scraper)
for App information from iTunes App Store.
* [dbader/schedule](https://github.com/dbader/schedule) for a simple to use API for scheduling jobs.
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for an incredible wrapper I certainly can't refuse.
* [Nintendo](https://www.nintendo.com/) for sure.