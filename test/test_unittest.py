import requests
import unittest
from uuid import UUID

baseURL = "http://127.0.0.1:8000"


class TestAPI(unittest.TestCase):
    timeout = 5

    def test_ping(self):
        resp = requests.get(f"{baseURL}/api/ping").content
        self.assertEqual(resp, b'"pong"')

    def test_api(self):
        resp = requests.get(f"{baseURL}/test").json()
        error = resp["errors"][0]
        errortxt = f"Nope, this isn't the API you're looking for, maybe try checking the docs? at {baseURL.strip('/')}/docs"
        self.assertEqual(errortxt, error["detail"])


class TestFood(unittest.TestCase):
    timeout = 5
    uuid = "0b410292-1ff8-4640-a174-a90261ea4b6a"
    name = "Asado"
    brand = "Meow-meow"
    weight = 1

    def test_food_flow(self):
        self._create()
        self._list()
        self._get()
        self._update()
        self._delete()

    def _create(self):
        resp = requests.post(
            f"{baseURL}/api/food/add",
            json={
                "uuid": str(self.uuid),
                "name": self.name,
                "brand": self.brand,
                "weight": self.weight,
            },
        )
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        resp = resp.json()
        self.assertEqual(resp["result"], "ok")
        resp = resp["data"]
        self.assertEqual(resp["uuid"], self.uuid)
        self.assertEqual(resp["name"], self.name)
        self.assertEqual(resp["brand"], self.brand)

    def _list(self):
        resp = requests.get(f"{baseURL}/api/food/get", params={"limit": 100}).json()
        in_list: bool = False
        for food in resp["data"]:
            if not in_list:
                if food["uuid"] == self.uuid:
                    in_list = True
        self.assertTrue(in_list)

    def _get(self):
        resp = requests.get(f"{baseURL}/api/food/get/{self.uuid}").json()
        self.assertEqual(resp["uuid"], self.uuid)

    def _update(self):
        resp = requests.put(
            f"{baseURL}/api/food/update/{self.uuid}", json={"weight": 2}
        ).json()
        self.assertEqual(resp["uuid"], self.uuid)
        self.assertEqual(resp["weight"], 2)

    def _delete(self):
        resp = requests.delete(f"{baseURL}/api/food/delete/{self.uuid}").json()
        self.assertEqual(resp["result"], "ok")


class TestUser(unittest.TestCase):
    uuid = UUID("7bfebeab-44d6-4192-8b5f-b09bc9737203")
    username = "testuser"
    password = "testpassword"
    email = "testuser@example.com"
    first_name = "Test"
    last_name = "User"
    is_admin = True
    token: str

    @staticmethod
    def login(username, password):
        resp = requests.post(
            f"{baseURL}/api/auth/login",
            params={
                "username": username,
                "password": password,
            },
        ).json()
        return resp

    def test_user_flow(self):
        self._createUser()
        self._login()
        self._listUsers()
        self._getUser()
        self._updateUser()
        self._deleteUser()

    def _createUser(self):
        resp = requests.post(
            f"{baseURL}/api/user/add",
            params={
                "uuid": str(self.uuid),
                "username": self.username,
                "password": self.password,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "is_admin": self.is_admin,
            },
        ).json()
        self.assertEqual(resp["data"].get("uuid"), str(self.uuid))
        self.assertEqual(resp["data"]["username"], self.username)

    def _login(self):
        resp = self.login(
            username=self.username,
            password=self.password,
        )
        self.assertEqual(resp["result"], "ok")
        self.assertIn("access_token", resp)
        self.token = resp["access_token"]
        self.assertIn("token_type", resp)
        self.assertEqual(resp["token_type"], "bearer")

    def _listUsers(self):
        resp = requests.get(f"{baseURL}/api/user/get", params={"limit": 100}).json()
        in_list: bool = False
        for user in resp["data"]:
            if not in_list:
                if user["uuid"] == self.uuid:
                    in_list = True
        self.assertTrue(in_list)

    def _getUser(self):
        resp = requests.get(f"{baseURL}/api/user/get/{self.uuid}").json()
        self.assertEqual(resp["uuid"], self.uuid)

    def _update_user(self):
        resp = requests.put(
            f"{baseURL}/api/user/update/{self.uuid}", json={"first_name": "Test "}
        ).json()
        self.assertEqual(resp["uuid"], self.uuid)
        self.assertEqual(resp["first_name"], "Test ")

    def _deleteUser(self):
        key = self.login(
            username=self.username,
            password=self.password,
        )
        headers = {
            "Authorization": f"Bearer {key['access_token']}",
        }
        resp = requests.delete(
            f"{baseURL}/api/user/delete",
            params={
                "uuid": str(self.uuid),
            },
            headers=headers,
        ).json()
        self.assertEqual(resp["result"], "ok")
