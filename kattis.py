from bs4 import BeautifulSoup
import requests

class Course:
    def __init__(self, url: str):
        self.url = url
        self.assignments = []
        self.map = {}
        bsrequest = get_soup(url)
        for li in bsrequest.find_all('li'):
            ol = li.next_sibling.next_sibling
            if li.a != None and li.a.text != None and li.a['href'] != None and ol != None and ol.name == "ol" and li.parent.name == 'ul':
                problem_names = []
                is_open = li.text.find("(Remaining:") != -1
                for li2 in ol.find_all('li'):
                    problem_names.append(li2.text)
                shorturl = ""
                for urlpart in self.url.split('/'):
                    if urlpart == 'courses':
                        break
                    else:
                        shorturl += urlpart + '/'
                assignmenturl = shorturl[:-1] + li.a['href'].replace('problems', 'standings')
                self.assignments.append(Assignment(li.a.text, assignmenturl, problem_names, is_open)) 
                self.map[li.a.text] = len(self.assignments) - 1

    
class Assignment:
    def __init__(self, name: str, url: str, problem_names: list, is_open: bool):
        self.name = name
        self.url = url
        self.problem_names = problem_names
        self.is_open = is_open

    def get_users(self):
        users = {}
        standings = get_soup(self.url)
        for tr in standings.find_all('tr', {'class': ''}):
            if tr.find('td', {'class': 'standings-cell-score'}) == None:
                continue
            username, screenname = Assignment.parse_name(tr)
            solved = Assignment.parse_solved(tr)
            problems = Assignment.parse_problems(tr, self.problem_names)
            users[screenname] = User(username, screenname, solved, problems)
        return users

    def parse_name(soup: BeautifulSoup):
        name_td = soup.find('td', {'class': 'standings-cell--expand'})
        if name_td != None:
            if name_td.a != None:
                return name_td.a.get_text(strip=True), name_td.a['href'].replace('/users/', '')
            else:
                return "Hidden User", ""
        else:
            print("Error: Can\'t parse name from html")
            exit(1)

    def parse_solved(soup: BeautifulSoup) -> int:
        solved_td = soup.find('td', {'class': 'standings-cell-score'})
        if solved_td != None:
            return int(solved_td.get_text(strip=True))
        else:
            print("Error: Can\'t parse solved from html")
            exit(1)

    def parse_problems(soup: BeautifulSoup, problem_names: list) -> list:
        problems = []
        i = 0
        for td in soup.find_all('td'):
            attempts_span = td.find('span', {'class': 'standings-table-result-cell'})
            if attempts_span != None:
                attempts = int(attempts_span.get_text(strip=True).split('+')[0])
            else:
                attempts = 0
            if 'class' not in td.attrs:
                status = 'never'
            elif td['class'][0] in ['solved', 'attempted', 'first']:
                status = td['class'][0]
            else:
                continue
            problems.append(Problem(i, problem_names[i], status, attempts))
            i = i + 1
        if len(problems) == 0:
            print("Error: Can\'t parse problems from html or Not started yet")
            exit(1)
        return problems

class User:
    def __init__(self, username: str, screenname: str, solved: int, problems: list):
        self.username = username
        self.screenname = screenname
        self.solved = solved
        self.problems = problems

class Problem:
    def __init__(self, number: int, name: str, status: str, attempts: int):
        self.number = number
        self.alphabet = chr(ord('A') + number)
        self.name = name
        self.status = status
        self.attempts = attempts

def get_soup(url: str) -> BeautifulSoup:
    request = requests.get(url)
    if request.status_code != 200:
        print("Error: Can\'t get html from url")
        exit(1)
    return BeautifulSoup(request.text, 'html.parser')