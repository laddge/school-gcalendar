import toml
import googleapiclient.discovery
import google.auth


def main():
    with open("./config.toml") as f:
        config = toml.loads(f.read())
    creds = google.auth.load_credentials_from_file(
        "./credentials.json",
        ["https://www.googleapis.com/auth/calendar"],
    )[0]
    service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)
    print(service.events().list(calendarId=config["settings"]["calendarId"]).execute())


if __name__ == "__main__":
    main()
