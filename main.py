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
    service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
    events = []
    pageToken = None
    while True:
        res = service.events().list(calendarId=config["calendarId"], pageToken=pageToken).execute()
        for event in res.get("items", []):
            events.append(event)
        pageToken = res.get("nextPageToken")
        if not pageToken:
            break

    def task(date):
        s = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
        print(f"\r\033[K\033[34;1m[{date}]\033[m Clearing...", end="")
        for event in events:
            if date in event["start"]["dateTime"]:
                while True:
                    try:
                        s.events().delete(calendarId=config["calendarId"], eventId=event["id"]).execute()
                    except Exception:
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
                while True:
                    try:
                        s.events().insert(calendarId=config["calendarId"], body=event).execute()
                    except Exception:
                        time.sleep(1)
                    else:
                        break
        print(f"\r\033[K\033[32;1m[{date}]\033[m Completed.", end="")

    with ThreadPoolExecutor() as executor:
        res = [x for x in executor.map(task, config["dates"])]

    print(f"\r\033[K{len(res)} dates written.")


if __name__ == "__main__":
    main()
