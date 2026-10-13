import urllib.request
import urllib.parse


url = "http://127.0.0.1:5000/login"


for i in range(2):

    data = {
        "username": "admin",
        "password": "wrong123"
    }

    data = urllib.parse.urlencode(data).encode()

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    try:

        response = urllib.request.urlopen(request)

        print("Login attempt:", i + 1)
        print("Response:", response.status)

    except Exception as error:

        print("Login attempt:", i + 1)
        print("Response:", error)