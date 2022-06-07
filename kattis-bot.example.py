#!/usr/bin/env python3

from kattis import Course, User
import requests
from time import sleep

class View:
    def __init__(self, user: User, newuser: bool = False):
        self.screenname = user.screenname
        self.solved = user.solved
        if newuser:
            self.stateproblems = ["never" for _ in user.problems]
            self.attemptsproblems = [0 for _ in user.problems]
        else:
            self.stateproblems = [i.status for i in user.problems]
            self.attemptsproblems = [i.attempts for i in user.problems]

def send_discord(msg: str):
    if msg == None:
        return
    sleep(0.5)
    requests.post(None, json={"content": msg})
    print("send to discord: {}".format(msg), flush=True)

def get_current_assignment(course: Course):
    for assignment in course.assignments:
        if assignment.is_open and assignment.name.find("(Late)") == -1:
            return assignment
    return None

def init_views(users: list):
    views = {}   
    for screenname in users:
        view = View(users[screenname])
        views[screenname] = view
    return views

def add_user_views(views: dict, user: User):
    if user.screenname in views:
        return views
    else:
        views[user.screenname] = View(user, True)
        return views

def main():
    courseurl = "https://***.kattis.com/courses/***/***" # /courses/GB20602/2022_Spring みたいな？
    otakus = []
    
    course = Course(courseurl)
    assignment = get_current_assignment(course)
    users = assignment.get_users()
    full = len(assignment.problem_names)
    views = init_views(users)
    old_assignment = assignment
    print("init", flush=True)
    
    while True:
        course = Course(courseurl)
        assignment = get_current_assignment(course)
        if assignment == None:
            exit(0)
        
        users = assignment.get_users()
        print("fetch", flush=True)

        if old_assignment.url != assignment.url:
            full = len(assignment.problem_names)
            views = init_views(users)
            move = "移動したよ\n{}: {}\n↓\n{}: {}".format(old_assignment.name, old_assignment.url, assignment.name, assignment.url)
            send_discord(move)
            print("move", flush=True)

        for user in users.values():
            i = 0
            if user.screenname == "":
                continue
            views = add_user_views(views, user)
            for problem in user.problems:
                if problem.attempts > views[user.screenname].attemptsproblems[i] and views[user.screenname].stateproblems[i] != "solved":
                    send = None
                    if problem.status == "first":
                        send = "{}({})さんが{}回目で初めて{}問題を通しました ({}/{})".format(user.username, user.screenname, problem.attempts, problem.alphabet)
                        views[user.screenname].stateproblems[i] = "solved"
                    elif problem.status == "solved":
                        send = "{}({})さんが{}回目で{}問題を通しました ({}/{})".format(user.username, user.screenname, problem.attempts, problem.alphabet, user.solved, full)
                        views[user.screenname].stateproblems[i] = "solved"
                    elif problem.status == "attempted" and user.screenname in otakus:
                        send = "{}({})さんが{}問題に苦戦しています {}->{}".format(user.username, user.screenname, problem.alphabet, views[user.screenname].attemptsproblems[i], problem.attempts)
                    send_discord(send)
                    views[user.screenname].attemptsproblems[i] = problem.attempts
                i = i + 1
            if user.solved > views[user.screenname].solved:
                if user.solved == full:
                    send = "{}({})さんが全完しました\nおめでとうございます:tada::tada::tada: ({}/{})".format(user.username, user.screenname, full - user.solved, user.solved, full)
                    send_discord(send)
                views[user.screenname].solved = user.solved
        print("wait", flush=True)
        sleep(300)
        old_assignment = assignment

if __name__ == '__main__':
    main()