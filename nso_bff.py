import os
import time
import init
import json
import html
import logging
import schedule
import nso_auth
import functools


class NSO_BFF:
    def __init__(self):
        logging.basicConfig(
            filename="./log/log.log",
            filemode="w",
            format="%(asctime)s - %(levelname)s: %(message)s",
        )

        schedule_logger = logging.getLogger("schedule")
        schedule_logger.setLevel(level=logging.DEBUG)

    def catch_exceptions(cancel_on_failure=False):
        def catch_exceptions_decorator(job_func):
            @functools.wraps(job_func)
            def wrapper(*args, **kwargs):
                try:
                    return job_func(*args, **kwargs)
                except:
                    import traceback

                    print(traceback.format_exc())
                    if cancel_on_failure:
                        return schedule.CancelJob

            return wrapper

        return catch_exceptions_decorator

    @catch_exceptions(cancel_on_failure=False)
    def main(self):
        """
        First run and schedule job.
        """

        def time_now():
            this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            return this_time

        print(time_now())

        self.clean_last_run()

        tokens = nso_auth.nso.login()
        global accessToken
        accessToken = tokens[0][0]
        birthday = tokens[0][1]
        session_token = tokens[1]

        def update_status():
            data = nso_auth.nso.get_friend_list(accessToken)
            self.parse_frd_list(data)

        update_status()
        text = "<b>NSO-BFF-Notification</b> is now online."
        init.send_message(text)

        def job_update_status():
            print(time_now())
            update_status()

        def job_get_gettoken():
            print(time_now())
            global accessToken
            accessToken = nso_auth.nso.get_gettoken(
                accessToken, session_token, birthday
            )

        ## Update BFF online status every specified minutes
        schedule.every(init.refresh_mins).minutes.do(job_update_status)

        ## Get a new accessToken before it expired(7200 seconds)
        schedule.every(115).minutes.do(job_get_gettoken)

        print(f"BFF online status will be updated every {init.refresh_mins} minutes.")

        while True:
            schedule.run_pending()
            time.sleep(1)

    def clean_last_run(self):
        """
        Abandon last run status.
        """
        if os.path.exists(init.frds_status_file):
            os.remove(init.frds_status_file)

        with open(init.frds_status_file, "w") as file:
            json.dump({}, file)

    def get_last_status(self):
        """
        Get BFF last online status from a json file.
        """
        with open(init.frds_status_file, "r") as file:
            bff_last_status = json.load(file)
        return bff_last_status

    def parse_frd_list(self, data):
        """
        Parse data and send update to Telegram.
        """
        frds_status_json = {}

        for frd in data:
            if list(frd.values())[5]:
                if list(frd.values())[4]:
                    frd_name = html.escape(frd["name"])
                    frd_status = frd["presence"]["state"]

                    if frd_status == "ONLINE":
                        frd_status_int = 1
                        game_name = html.escape(frd["presence"]["game"]["name"])

                        if init.show_image:
                            image = (
                                f'<a href="{frd["presence"]["game"]["imageUri"]}">🟢</a>'
                            )
                        else:
                            image = "🟢"

                        text = f"<b>{frd_name}</b>  {image}  <b>{game_name}</b>"
                    else:
                        frd_status_int = 0
                        game_name = ""

                        text = f"<b>{frd_name}</b>  ⚪"

                    frds_status_json.update(
                        {frd["nsaId"]: {"status": frd_status_int, "game": game_name}}
                    )

                    msg_text = f"{text}"

                    bff_last_status = self.get_last_status()
                    if frd["nsaId"] in bff_last_status:
                        last_online_status = bff_last_status[frd["nsaId"]]["status"]
                        last_game = bff_last_status[frd["nsaId"]]["game"]
                        if (
                            frd_status_int != last_online_status
                            or game_name != last_game
                        ):
                            init.send_message(msg_text)

        with open(init.frds_status_file, "w") as file:
            json.dump(frds_status_json, file)

        print("Step(8/8): Update BFF online status: Done.")


if __name__ == "__main__":
    NSO_BFF().main()
