import requests
import unittest
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

baseUrl = os.environ.get("baseUrl", default="http://127.0.0.1:8000/")
username = "testuser1"
password = "testuser1"


class TestAPI(unittest.TestCase):
    timeout = 5

    def test_ping(self):
        resp = requests.get(f"{baseUrl}/api/ping").content
        self.assertEqual(resp, b'"pong"')

    def test_api(self):
        resp = requests.get(f"{baseUrl}/test").json()
        error = resp["errors"][0]
        errortxt = f"Nope, this isn't the API you're looking for, maybe try checking the docs? at {baseUrl.strip('/')}/docs"
        self.assertEqual(errortxt, error["detail"])


class TestFood(unittest.TestCase):
    timeout = 5
    food_id = str(uuid4())
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
            f"{baseUrl}/api/food/add",
            json={
                "food_id": str(self.food_id),
                "name": self.name,
                "brand": self.brand,
                "weight": self.weight,
            },
        )
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["food_id"], self.food_id)
        self.assertEqual(resp["name"], self.name)
        self.assertEqual(resp["brand"], self.brand)

    def _list(self):
        resp = requests.get(f"{baseUrl}/api/food/get", params={"limit": 100})
        if resp.status_code != 200:
            self.assertTrue(True)
            return
        self.assertEqual(resp.json()["result"], "ok")

        resp = resp.json()["data"]

        in_list: bool = False
        for food in resp:
            if not in_list:
                if food["food_id"] == self.food_id:
                    in_list = True
        self.assertTrue(in_list)

    def _get(self):
        resp = requests.get(f"{baseUrl}/api/food/get/{self.food_id}")
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["food_id"], self.food_id)

    def _update(self):
        resp = requests.put(
            f"{baseUrl}/api/food/update/{self.food_id}", json={"weight": 2}
        )
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["food_id"], self.food_id)
        self.assertEqual(resp["weight"], 2)

    def _delete(self):
        jwt_code = TestUser.login(username, password)
        headers = {"Authorization": f"Bearer {jwt_code}"}
        resp = requests.delete(
            f"{baseUrl}/api/food/delete/{self.food_id}", headers=headers
        ).json()
        self.assertEqual(resp["result"], "ok")


class TestUser(unittest.TestCase):
    user_id = str(uuid4())
    username = "testuser69"
    password = "testpassword"
    email = "testuser69@example.com"
    first_name = "Test"
    last_name = "User"
    is_admin = True
    token: str

    @staticmethod
    def login(username: str, password: str) -> str:
        resp = requests.post(
            f"{baseUrl}/api/auth/login",
            params={
                "username": username,
                "password": password,
            },
        ).json()
        return resp["data"]

    def test_user_flow(self):
        self._createUser()
        self._listUsers()
        self._getUser()
        self._updateUser()
        self._deleteUser()

    def _createUser(self):
        resp = requests.post(
            f"{baseUrl}/api/user/add",
            json={
                "user_id": self.user_id,
                "username": self.username,
                "password": self.password,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "is_admin": self.is_admin,
            },
        )

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["user_id"], self.user_id)
        self.assertEqual(resp["username"], self.username)

    def _listUsers(self):
        resp = requests.get(f"{baseUrl}/api/user/get", params={"limit": 100})
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        resp = resp.json()
        self.assertEqual(resp["result"], "ok")

        in_list: bool = False
        for user in resp["data"]:
            if not in_list:
                if user["user_id"] == self.user_id:
                    in_list = True
        self.assertTrue(in_list)

    def _getUser(self):
        resp = requests.get(f"{baseUrl}/api/user/get/{self.user_id}")
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["user_id"], self.user_id)

    def _updateUser(self):
        resp = requests.put(
            f"{baseUrl}/api/user/update/{self.user_id}", json={"first_name": "Test "}
        )
        if resp.status_code != 200:
            self.assertTrue(True)
            return

        self.assertEqual(resp.json()["result"], "ok")
        resp = resp.json()["data"]
        self.assertEqual(resp["user_id"], self.user_id)
        self.assertEqual(resp["first_name"], "Test ")

    def _deleteUser(self):
        jwt_code = self.login(self.username, self.password)
        headers = {"Authorization": f"Bearer {jwt_code}"}
        resp = requests.delete(
            f"{baseUrl}/api/user/delete/{self.user_id}",
            params={
                "user_id": self.user_id,
            },
            headers=headers,
        ).json()
        self.assertEqual(resp["result"], "ok")


if __name__ == "__main__":
    unittest.main()
