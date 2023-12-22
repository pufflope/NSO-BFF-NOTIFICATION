import re
import init
import uuid
import base64
import string
import secrets
import hashlib
import requests
import webbrowser


class nso:
    def api():
        "Nintendo:"
        # 1
        "https://accounts.nintendo.com/connect/1.0.0/authorize"
        # 2
        "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
        # 3
        "https://accounts.nintendo.com/connect/1.0.0/api/token"
        # 4
        "https://api.accounts.nintendo.com/2.0.0/users/me"
        # 5
        "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"
        # 6
        "https://api-lp1.znc.srv.nintendo.net/v3/Friend/List"
        # 7
        "https://api-lp1.znc.srv.nintendo.net/v3/Account/GetToken"

        "3rd-party:"
        # 8
        "https://api.imink.app/f"

        """
        Login step: 1-4, 8, 5
        Stay login: 3, 8, 7
        """

    def login():
        """
        Request a Nintendo authorization webpage to get user's session_token_code(use for "/1.0.0/api/session_token")
        """
        url = "https://accounts.nintendo.com/connect/1.0.0/authorize"

        session_token_code_verifier = "".join(
            secrets.choice(string.ascii_letters) for i in range(50)
        )

        redirect_uri = f"npf{init.client_id}://auth"

        hash = hashlib.sha256(session_token_code_verifier.encode()).digest()
        encoded_hash = base64.urlsafe_b64encode(hash)
        session_token_code_challenge = encoded_hash.decode()[:-1]

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Host": "accounts.nintendo.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Accept-Language": "en-us",
        }
        body = {
            "state": session_token_code_verifier,
            "redirect_uri": redirect_uri,
            "client_id": init.client_id,
            "scope": "openid user user.birthday user.mii user.screenName",
            "response_type": "session_token_code",
            "session_token_code_challenge": session_token_code_challenge,
            "session_token_code_challenge_method": "S256",
            "theme": "login_form",
        }

        res = requests.get(url, headers=headers, params=body)

        print_text = 'Step(1/8): Get session_token_code from "/1.0.0/authorize":'

        if res.status_code == 200:
            print("Open this link:\n", res.url)

            webbrowser.open(res.url)

            link = input(
                "Step(1/8): Login, right click the select this account button, copy link address then right click here to paste:\nPress Enter when you pasted.\n"
            )

            session_token_code = "".join(re.findall("session_token_code=(.*)&", link))

            print(print_text, "Succeed.")

            return nso.get_session_token(
                session_token_code, session_token_code_verifier
            )
        else:
            print(print_text, "Error:", res, res.text)

    def get_session_token(session_token_code, session_token_code_verifier):
        """
        Post session_token_code(from "/1.0.0/authorize") to get session_token(use for "/1.0.0/api/token" and "/v3/Account/GetToken")
        """
        url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"

        headers = init.request_headers_com()
        body = {
            "client_id": {init.client_id},
            "session_token_code": {session_token_code},
            "session_token_code_verifier": {session_token_code_verifier},
        }
        res = requests.post(url, headers=headers, data=body)

        print_text = 'Step(2/8): Get session_token from "/1.0.0/api/session_token":'

        if res.status_code == 200:
            session_token = res.json()["session_token"]
            code = res.json()["code"]
            print(print_text, "Succeed.")
            step = "initlogin"
            return nso.get_token(session_token, step), session_token
        else:
            print(print_text, "Error:", res.json())

    def get_token(session_token, step):
        """
        Post sesion_token(from "/1.0.0/api/session_token") to get cookie, id_token and access_token(expire in 900 seconds)
        cookie use for "/2.0.0/users/me"
        accesss_token use for "/2.0.0/users/me", "/v3/Account/Login" and "https://api.imink.app/f"
        id_token use for "/v3/Account/GetToken"
        """
        url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

        headers = init.request_headers_com()
        headers["Content-Type"] = "application/json"
        body = {
            "client_id": init.client_id,
            "session_token": session_token,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
        }
        res = requests.post(url, headers=headers, json=body)

        print_text = 'Step(3/8): Get cookie, access_token from "/1.0.0/api/token":'

        if res.status_code == 200:
            id_token = res.json()["id_token"]
            access_token = res.json()["access_token"]

            cookieA = "".join(re.findall("_abck=\S*;", res.headers["Set-Cookie"]))
            cookieB = "".join(re.findall(" bm_sz=\S*", res.headers["Set-Cookie"]))
            cookie = cookieA + cookieB

            print(print_text, "Succeed.")

            if step == "initlogin":
                accessToken = nso.get_user_me(cookie, access_token)
                return accessToken
            elif step == "staylogin":
                return id_token

        else:
            print(print_text, "Error:", res.json())

    def get_user_me(cookie, access_token):
        """
        Post cookie, access_token(from "/1.0.0/api/token") to get user's birthday and country(use for "/v3/Account/Login" and "/v3/Account/GetToken")
        """
        url = "https://api.accounts.nintendo.com/2.0.0/users/me"

        headers = init.request_headers_com()
        headers["Host"] = "api.accounts.nintendo.com"
        headers["Content-Type"] = "application/json"
        headers["Cookie"] = cookie
        headers["Authorization"] = "Bearer " + access_token

        res = requests.get(url, headers=headers)

        print_text = 'Step(4/8): Get user_me from "/2.0.0/users/me":'

        if res.status_code == 200:
            print(print_text, "Succeed.")
            birthday = res.json()["birthday"]
            country = res.json()["country"]
            accessToken = nso.get_login(access_token, birthday, country)
            return accessToken, birthday
        else:
            print(print_text, "Error:", res, res.text)

    def get_login(access_token, birthday, country):
        """
        Get access_token(use for "/v3/Friend/List") (expire in 7200 seconds)
        """
        url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"

        request_id = str(uuid.uuid4())

        imink = nso.get_f(access_token)
        imink_timestamp = imink["timestamp"]
        imink_f = imink["f"]
        imink_request_id = imink["request_id"]

        headers = init.request_headers_net()
        headers["Authorization"] = "Bearer " + access_token
        body = {
            "requestId": request_id,
            "parameter": {
                "f": imink_f,
                "naBirthday": birthday,
                "naCountry": country,
                "naIdToken": access_token,
                "requestId": imink_request_id,
                "language": "en-US",
                "timestamp": imink_timestamp,
            },
        }
        res = requests.post(url, headers=headers, json=body)

        print_text = 'Step(6/8): Get accessToken from "/v3/Account/Login":'

        if res.status_code == 200:
            accessToken = res.json()["result"]["webApiServerCredential"]["accessToken"]
            print(print_text, "Succeed.")
            return accessToken
        else:
            print(print_text, "Error:", res.json())

    def get_friend_list(accessToken):
        """
        Post accessToken(from "/v3/Account/Login") to get NSO friend list.
        """
        url = "https://api-lp1.znc.srv.nintendo.net/v3/Friend/List"

        headers = init.request_headers_net()
        headers["Authorization"] = "Bearer " + str(accessToken)

        request_id = str(uuid.uuid4()).upper()
        body = {
            "requestId": request_id,
            "parameter": {},
        }
        res = requests.post(url, headers=headers, json=body)

        print_text = 'Step(7/8): Get friends from "/v3/Friend/List":'

        if res.status_code == 200:
            print(print_text, "Succeed.")
            return res.json()["result"]["friends"]
        else:
            print(print_text, "Error:", res.json())

    def get_f(access_token):
        """
        Post access_token(from "/1.0.0/api/token") to get f, request_id, timestamp(use for "/v3/Account/Login" and "/v3/Account/GetToken")
        """
        url = "https://api.imink.app/f"

        headers = {
            "User-Agent": f"{init.program_name}/{init.program_version}",
        }
        body = {
            "Content-Type": "application/json; charset=utf-8",
            "token": access_token,
            "hash_method": "1",
        }
        res = requests.post(url, headers=headers, json=body)

        print_text = 'Step(5/8): Get f from "api.imink.app/f":'

        if res.status_code == 200:
            print(print_text, "Succeed.")
            return res.json()
        else:
            print(print_text, "Error:", res.text, res)
            msg_text = f'Seems "api.imink.app/f" API is down, go https://status.imink.app/ and check the status.\nError: {res}'
            init.send_message(msg_text)

    def get_gettoken(accessToken, session_token, birthday):
        """
        Request a new accessToken to stay login.
        """
        step = "staylogin"
        id_token = nso.get_token(session_token, step)
        url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/GetToken"

        request_id = str(uuid.uuid4())

        imink = nso.get_f(id_token)
        imink_timestamp = imink["timestamp"]
        imink_f = imink["f"]
        imink_request_id = imink["request_id"]

        headers = init.request_headers_net()
        headers["Authorization"] = "Bearer " + accessToken
        body = {
            "requestId": request_id,
            "parameter": {
                "naBirthday": birthday,
                "f": imink_f,
                "timestamp": imink_timestamp,
                "requestId": imink_request_id,
                "naIdToken": id_token,
            },
        }
        res = requests.post(url, headers=headers, json=body)

        print_text = 'Step(10/8): Get accessToken from "/v3/Account/GetToken":'

        if res.status_code == 200:
            accessToken = res.json()["result"]["webApiServerCredential"]["accessToken"]
            print(print_text, "Succeed.")
            return accessToken
        else:
            print(print_text, "Error:", res.json())
