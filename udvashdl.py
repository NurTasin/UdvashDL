import argparse
from udvash import Udvash, UdvashLoginError
from os import path,system, mkdir
from sys import exit
DEFAULT_COOKIE_PATH = "./cookie.txt"

argparser = argparse.ArgumentParser(prog="udvashdl.py",
                                    usage="python udvashdl.py [-R <registration number> -P <password> | --cookie <cookie_file>] CONTENT_LINK",
                                    description="Helps to extract various contents (class, notes, exam questions) from Udvash's website")

argparser.add_argument("--login",action="store_true",help="Logs you in interactively and saves the cookie and exits")
argparser.add_argument("-R","--reg-num",action="store",help="Udvash Registration Number")
argparser.add_argument("-P","--password",action="store",help="Password for Udvash's webapp")
argparser.add_argument("--cookie",action="store",help="Path to the cookie path or where to save the cookie for fast login")
argparser.add_argument("-N","--only-note",action="store_true",help="Skips the video lecture and only downloads the note")
argparser.add_argument("-V","--only-video",action="store_true", help="Skips the note lecture and only downloads the video")
argparser.add_argument("content_url",help="Url of the content you want to extract.")

args = argparser.parse_args()
print(args)

#---------------------- Login Management -------------------------#

#Checking if interactive login flag was set
if args.login:
    UdvashClient = Udvash(input("Registration Number: "),input("Password: "))
    exit(0)

#Login method priority
# Provided Creds -> Provided Cookie -> Default Cookies

UdvashClient = None

if (not args.reg_num) or (not args.password):
    if (not args.cookie):
        if not path.exists(DEFAULT_COOKIE_PATH):
            print("[Error] No Credentials or Cookies were provided")
            argparser.print_usage()
            exit(1)
        else:
            UdvashClient = Udvash(cookiepath=args.cookie)
    else:
        UdvashClient = UdvashClient()
else:
    UdvashClient = Udvash(regnum=args.reg_num,password=args.password)


#--------------------- Content Extraction Management ----------------------
if not path.exists("./UdvashDL"):
    mkdir("./UdvashDL")

if not path.exists("./UdvashDL/Lectures"):
    mkdir("./UdvashDL/Lectures")

if not path.exists("./UdvashDL/Questions"):
    mkdir("./UdvashDL/Questions")

if "https://online.udvash-unmesh.com/Routine/RoutineDetails" in args.content_url:
    #Download Class
    classData = UdvashClient.getClassContent(args.content_url)
    print(f"Lecture Title: {classData['title']}")
    title = classData['title']
    if args.only_note or args.only_video:
        if args.only_note:
            if not path.exists(f"./UdvashDL/Lectures/{title}"):
                mkdir(f"./UdvashDL/Lectures/{title}")
            system(f"wget -x -nv -q --no-check-certificate -c -O \"./UdvashDL/Lectures/{title}/{title}.pdf\" \"{classData['notes']}\"")
        
        if args.only_video:
            system(f"yt-dlp {'-f 22' if 'youtube.com' in classData['video'] else ''} \"{classData['video']}\" -o \"./UdvashDL/Lectures/{title}/{title}.mp4\"")
    else:
        if not path.exists(f"./UdvashDL/Lectures/{title}"):
            mkdir(f"./UdvashDL/Lectures/{title}")
        system(f"wget -x -nv -c -q --no-check-certificate -O \"./UdvashDL/Lectures/{title}/{title}.pdf\" \"{classData['notes']}\"")
        system(f"yt-dlp {'-f 22' if 'youtube.com' in classData['video'] else ''} \"{classData['video']}\" -o \"./UdvashDL/Lectures/{title}/{title}.mp4\"")
    
elif "https://online.udvash-unmesh.com/Exam/Question" in args.content_url:
    examData = UdvashClient.getExamContent(args.content_url)
    print(f"Exam Name: {examData['examName']}\nCourse Name: {examData['courseName']}")
    examName=examData['examName']
    courseName = examData["courseName"]
    for _ in examData['links']:
        if not path.exists(f"./UdvashDL/Questions/{courseName}"):
            mkdir(f"./UdvashDL/Questions/{courseName}")

        if not path.exists(f"./UdvashDL/Questions/{courseName}/{examName}"):
            mkdir(f"./UdvashDL/Questions/{courseName}/{examName}")
        
        print(f"Downloading ./UdvashDL/Questions/{courseName}/{examName}/{_['title']}")
        system(f"wget -x -q -nv -c -O \"./UdvashDL/Questions/{courseName}/{examName}/{_['title']}\" \"{_['link']}\"")

else:
    print("Extractor for this page is not available yet!")