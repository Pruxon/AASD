import requests

if __name__ == "__main__":
    url = "http://localhost:5443/api/register"
    data = {
        "user": "testuser2",
        "host": "localhost",
        "password": "password"
    }

    res = requests.post(url, json=data, auth=("admin@localhost", "passw0rd"))

    print(res.text)
