from googleapiclient.errors import HttpError

from participant import Participant
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

        for participant in participants:
            for submission in participant.submissions:
                verdict, problem_name = submission.scrape_verdict()
                if not submission.verify_problem_name(problem_name):
                    print("invalid submission: ", submission)
                    continue
                submission.accept()
                print("submission accepted", participant.handle, problem_name)
            participant.update_points()

        sheets.update_participants_points(
            headers, values, sheet, participants)

    except HttpError as e:
        print(e)


if __name__ == "__main__":
    main()
