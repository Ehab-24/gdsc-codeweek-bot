import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.verdict_selector = '.verdict-accepted'
        self.problem_selector = '#pageContent > div.datatable > div:nth-child(6) > table > tr:nth-child(2) > td:nth-child(3) > a'
        self.handle_selector = '#pageContent > div.datatable > div:nth-child(6) > table > tbody > tr:nth-child(2) > td:nth-child(2) > a'

    def scrape_verdict(self, participant, submission):
        response = requests.get(submission.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            verdict = soup.select(self.verdict_selector)
            problem_a = soup.select(self.problem_selector)
            # handle_a = soup.select(self.handle_selector)

            problem = problem_a[0].text if problem_a and len(
                problem_a) == 1 else ''
            # handle = handle_a[0].text if handle_a and len(
            #     handle_a) == 1 else ''

            if not submission.verify_problem_name(problem):
                print("error: {}".format(submission.error), submission)
                return False
            # if not participant.verify_handle(handle):
            #     print("error: mismatched user handle: ", submission)
            #     return False

            return verdict and len(verdict) == 1 and verdict[0].text == 'Accepted'
        else:
            print('Error', response.status_code, response.text)
            return False
