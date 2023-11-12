from googleapiclient.errors import HttpError

from participant import Participant
from scraper import Scraper
import sheets


def main():
    try:
        sheet = sheets.get_sheet()
        result = sheet.values().get(
            spreadsheetId=sheets.SPREADSHEET_ID,
            range='Sheet1'
        ).execute()

        # get sheet headers and data values
        values = result.get('values', [])
        headers = values[0]
        values = values[1:]

        participants = Participant.serialize_all(headers, values)
        scraper = Scraper()

        for participant in participants:
            for submission in participant.submissions:
                accepted = scraper.scrape_verdict(participant, submission)
                if not accepted:
                    continue

                submission.accept()
                print("submission accepted",
                      participant.handle, submission.problem)
            participant.update_points()

        sheets.update_participants_points(
            headers, values, sheet, participants)

    except HttpError as e:
        print(e)


if __name__ == "__main__":
    main()
