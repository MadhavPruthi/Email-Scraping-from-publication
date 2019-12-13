import requests


def send_simple_message(email):
    return requests.post(
        "https://api.mailgun.net/v3/blog.openreuse.org/messages",
        auth=("api", "d27c88c4de0fe3ba106e75f4ee170ab1-c1fe131e-e6cd927d"),
        data={"from": "New User <mailgun@blog.openreuse.org>",
              "to": [email],
              "subject": "Hello",
              "text": "Testing some Mailgun awesomness!"})

