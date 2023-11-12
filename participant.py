import re
from constants import ColumnNames


class Status:
    QUEUED = 'Queued'
    ACCEPTED = 'Accepted'
    ERROR = 'Error'


class Verdict:
    ACCEPTED = 'Accepted'
    PENDING = 'Pending'
    WRONG_ANSWER = 'Wrong answer'
    ERROR = 'Error'


class Error:
    INVALID_URL = 'invalid url'
    MISMATCHED_PROBLEM = 'mismatched problem'
    RUNTIME_ERROR = 'runtime error'


class Submission:
    def __init__(self, url, verdict, points, problem, status):
        self.url = url
        self.verdict = verdict
        self.points = points
        self.problem = problem
        self.status = status

    def __str__(self):
        return f'url: {self.url}\nproblem: {self.problem}\nstatus: {self.status}\nverdict: {self.verdict}\npoints: {self.points}\n'

    def accept(self):
        self.verdict = Verdict.ACCEPTED

    def verify_problem_name(self, problem):
        if self.problem != problem:
            self.status = Status.ERROR
            self.error = Error.MISMATCHED_PROBLEM
            return False
        return True


class Participant:
    def __init__(self, handle, email, points, submissions):
        self.handle = handle
        self.email = email
        self.submissions = submissions
        self.points = points
        self.batch_year = self.extract_year()

    def extract_year(self):
        year_pattern = re.compile(
            r'bs(?:cs|ai|eds|se|mt|ce|ee)(\d{2})\d{3}@itu\.edu\.pk')
        if year_pattern.search(self.email):
            extracted_years = year_pattern.search(self.email).group(1)
            return int(extracted_years)
        return 20

    def update_points(self):
        for submission in self.submissions:
            if submission.verdict == Verdict.ACCEPTED:
                self.points += submission.points * self.batch_year/20

    def verify_handle(self, handle):
        return self.handle == handle

    def __str__(self):
        return f'handle: {self.handle}\npoints: {self.points}\nemail: {self.email}\nyear: {self.batch_year}\nsubmissions: {self.submissions}\n'

    # @param headers: list of strings
    # @param values: list of lists of strings
    # @return: list of Participant
    @staticmethod
    def serialize_all(headers, values):
        participants = []

        handle_index = headers.index(ColumnNames.CODEFORCES_HANDLE)
        email_index = headers.index(ColumnNames.EMAIL)
        points_index = headers.index(ColumnNames.POINTS)

        for i, row in enumerate(values):
            handle = row[handle_index]
            email = row[email_index]

            points = 0.0
            if len(row) > points_index:
                points = float(row[points_index]
                               ) if row[points_index] != '' else 0.0

            if handle is None or handle == '':
                continue
            participants.append(Participant(handle, email, points, []))

            for col_name in ColumnNames.SUBMISSION_URLS:
                url_index = headers.index(col_name)
                if len(row) > url_index and row[url_index] != '':

                    problem = Participant.construct_problem_name(col_name)
                    if problem is None:
                        print("invalid submission column header:", col_name)
                        continue

                    s = Submission(
                        row[url_index], Verdict.PENDING, 10.0, problem, Status.QUEUED)
                    participants[i].submissions.append(s)
        return participants

    @staticmethod
    def construct_problem_name(header):
        url_pattern = re.compile(r'https://[^\s]+')
        match = url_pattern.search(header)

        if match:
            url = match.group()
            path_elements = url.split('/')

            if len(path_elements) >= 2:
                return ''.join(path_elements[-2:])
            else:
                return None
        else:
            return None
