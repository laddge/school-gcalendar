import time
from concurrent.futures import ThreadPoolExecutor
import toml
import googleapiclient.discovery
import google.auth


def main():
    with open("./config.toml") as f:
        config = toml.load(f)
    creds = google.auth.load_credentials_from_file(
        "./credentials.json",
        ["https://www.googleapis.com/auth/calendar"],
    )[0]

    def task(date):
        service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
        for t in range(10):
            try:
                events = service.events().list(calendarId=config["calendarId"], maxResults=9999).execute().get("items", [])
            except Exception:
                print(f"\r\033[K\033[31;1m[{date}]\033[m Rate limit exceeded, retrying... ({t + 1} / 10)", end="")
                time.sleep(1)
            else:
                break
        print(f"\r\033[K\033[34;1m[{date}]\033[m Clearing...", end="")
        for event in events:
            if date in event["start"]["dateTime"]:
                for t in range(10):
                    try:
                        service.events().delete(calendarId=config["calendarId"], eventId=event["id"]).execute()
                    except Exception:
                        print(f"\r\033[K\033[31;1m[{date}]\033[m Rate limit exceeded, retrying... ({t + 1} / 10)", end="")
                        time.sleep(1)
                    else:
                        break
        table = config["dates"][date]
        if type(table) == str:
            table = config["presets"][table]
        print(f"\r\033[K\033[34;1m[{date}]\033[m Writing...", end="")
        for i, event in enumerate(table):
            if "summary" in event:
                event["start"] = {"dateTime": "{}T{}:00".format(date, config["periods"][i][0]), "timeZone": config["tz"]}
                event["end"] = {"dateTime": "{}T{}:00".format(date, config["periods"][i][1]), "timeZone": config["tz"]}
                for t in range(10):
                    try:
                        service.events().insert(calendarId=config["calendarId"], body=event).execute()
                    except Exception:
                        print(f"\r\033[K\033[31;1m[{date}]\033[m Rate limit exceeded, retrying... ({t + 1} / 10)", end="")
                        time.sleep(1)
                    else:
                        break
        print(f"\r\033[K\033[32;1m[{date}]\033[m Completed.", end="")

    with ThreadPoolExecutor() as executor:
        res = [x for x in executor.map(task, config["dates"])]

    print(f"\r\033[K{len(res)} dates written.")


if __name__ == "__main__":
    main()
