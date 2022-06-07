from kattis import Course
import argparse

def index_input(help_text: str, len: int) -> int:
    indexstr = input(help_text + " (q to quit): ")
    try:
        index = int(indexstr)
    except:
        if indexstr == "q":
            exit(0)
        else:
            print("Invalid input")
            return index_input(help_text, len)
    if len <= index:
        print("Invalid assignment number")
        return index_input(help_text, len)
    print("----------------------------------------------------")
    return index

def main():
    parser = argparse.ArgumentParser(description='Get kattis course\'s information')
    parser.add_argument('-c', '--course-url', dest='url', type=str,
                        default="https://tsukuba.kattis.com/courses/GB20602/2022_Spring",
                        help='Url to course')
    parser.add_argument('-n', '--assignment', dest='assignmentnum', 
                        type=int, default=None, required=False,
                        help='Assignment number')
    parser.add_argument('-u', '--username', dest='username', 
                        type=str, default=None, required=False,
                        help='filter username')
    parser.add_argument('-s', '--screenname', dest='screenname', 
                        type=str, default=None, required=False,
                        help='filter screenname')
    parser.add_argument('-p', '--problem', dest='problem', 
                        type=int, default=None, required=False,
                        help='filter problem')
    parser.add_argument('-f', '--format', dest='format', 
                        type=str, default="{0}({1}) {2}/{3}\n|   {1} {2:15}: {3:6}({4})\n|", required=False,
                        help='{0: username, 1: screenname, 2: solved_problem, 3: all_problem}|{0: problemnum, 1: alphabet, 2: problemname, 3: status, 4: attempts}|end')
    args = parser.parse_args()

    course = Course(args.url)

    if args.assignmentnum == None:
        i = 0
        for assignment in course.assignments:
            print(str(i) + ": " + assignment.name)
            print(assignment.is_open)
            i = i + 1
        assignmentnum = index_input("Which assignment?", len(course.assignments))
    else:
        if (args.assignmentnum >= len(course.assignments)):
            print("Invalid assignment number")
            exit(1)
        assignmentnum = args.assignmentnum

    users = course.assignments[assignmentnum].get_users()
    for user in users.values():
        if args.username != None and user.username != args.username:
            continue
        if args.screenname != None and user.screenname != args.screenname:
            continue
        tmp = args.format.replace("\\n","\n").replace("\\t","\t").split("|")
        print(tmp[0].format(user.username, user.screenname, user.solved, len(course.assignments[0].problem_names)), end="")
        for problem in user.problems:
            if args.problem != None and problem.number != args.problem:
                continue
            print(tmp[1].format(problem.number, problem.alphabet, problem.name, problem.status, problem.attempts), end="")
        print(tmp[2], end="")

if __name__ == '__main__':
    main()