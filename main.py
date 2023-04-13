import toml
import googleapiclient.discovery
import google.auth
import tqdm


def main():
    with open("./config.toml") as f:
        config = toml.load(f)
    creds = google.auth.load_credentials_from_file(
        "./credentials.json",
        ["https://www.googleapis.com/auth/calendar"],
    )[0]
    service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
    events = service.events().list(calendarId=config["calendarId"], maxResults=9999).execute().get("items", [])
    for date, table in config["dates"].items():
        print(f"\n\033[32;1m[{date}]\033[m")
        print(f"Clearing...")
        for event in tqdm.tqdm(events):
            if date in event["start"]["dateTime"]:
                service.events().delete(calendarId=config["calendarId"], eventId=event["id"]).execute()
        if type(table) == str:
            table = config["presets"][table]
        print(f"Writing...")
        for i, event in enumerate(tqdm.tqdm(table)):
            if "summary" in event:
                event["start"] = {"dateTime": "{}T{}:00".format(date, config["periods"][i][0]), "timeZone": config["tz"]}
                event["end"] = {"dateTime": "{}T{}:00".format(date, config["periods"][i][1]), "timeZone": config["tz"]}
                service.events().insert(calendarId=config["calendarId"], body=event).execute()


if __name__ == "__main__":
    main()
