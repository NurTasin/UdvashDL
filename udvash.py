import requests as req
from bs4 import BeautifulSoup
import re
import json
from http.cookiejar import MozillaCookieJar
from os import path
from pprint import pprint
from urllib.parse import quote_plus

 
class UdvashLoginError(Exception):
    """Raised when any error occurs login in to Udvash"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Udvash:
    def __init__(self, regnum=None, password=None, cookiepath=None) -> None:
        self.session = req.session()
        if not cookiepath:
            cookiepath = "./cookie.txt"
        self.cookie_jar = MozillaCookieJar()
        self.cookiepath = cookiepath       
        self.regnum = regnum
        self.password = password
        if not path.exists(cookiepath):
            if (not regnum) or (not password):
                print("No cookie was found and credentials were not provided. Prompting for Credentials.")
                self.regnum = input("Registration Number:  ")
                self.password = input ("Password:  ")
                self._loginWithCreds(regnum,password)
            else:
                print("No Cookie Found! Loging in with provided credentials")
                self._loginWithCreds(regnum,password)
        else:
            print(f"Cookie file `{self.cookiepath}` found! Using it to login.")
            self._loginWithCookie(cookiepath)
    
    def _loginWithCreds(self,regnum,password):
        login_data = self.session.post("https://online.udvash-unmesh.com/Account/Login",data={
            "RememberMe":True,
            "RegistrationNumber": str(regnum),
            "Password": str(password)
        })
        # print(login_data.text)
        if ("Invalid Password" in login_data.text) or ("Invalid registration number" in login_data.text):
            raise UdvashLoginError("Wrong Registration Number or Password Provided")
        else:
            # print(login_data.text)
            # print(self.session.cookies.get_dict())
            print("Login Successsful!!")
            for cookie in self.session.cookies:
                self.cookie_jar.set_cookie(cookie)

            self.cookie_jar.save(self.cookiepath, ignore_discard=True)
    
    def _loginWithCookie(self,cookiepath):
        self.cookie_jar = MozillaCookieJar(cookiepath)
        self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        self.session.cookies = self.cookie_jar

        #checking if the cookies are still valid
        res = self.session.get("https://online.udvash-unmesh.com/Routine",allow_redirects=False)
        if "Object moved to" in res.text:
            if (not self.regnum) or (not self.password):
                print("Cookie expired! Prompting for credentials")
                self.regnum = input("Registration Number:  ")
                self.password = input ("Password:  ")
                self._loginWithCreds(self.regnum,self.password)
            else:
                print("Logging in with provided credentials instead")
                self._loginWithCreds(self.regnum,self.password)
        elif "My Routine - Udvash Unmesh Online" in res.text:
            print("Login Successful!")
        else:
            raise UdvashLoginError("Unknown Error Occured while loging in using cookie")
    
    def getRoutine(self):
        lecture = self.session.post("https://online.udvash-unmesh.com/Routine/LoadRoutineAjax",data={
            "type": "lecture",
            "courseId": 0,
            "subjectId": "",
            "filterType": 1,
            "lectureType": 0,
            "examPlatform": 0,
        })

        exam = self.session.post("https://online.udvash-unmesh.com/Routine/LoadRoutineAjax",data={
            "type": "exam",
            "courseId": 0,
            "subjectId": "",
            "filterType": 1,
            "lectureType": 0,
            "examPlatform": 0,
        })

        lecture_soup = BeautifulSoup(lecture.text,"html.parser")
        exam_soup = BeautifulSoup(exam.text,"html.parser")

        result = {
            "lectures":[],
            "exams":[]
        }
        
        lecture_divs = lecture_soup.find_all("div",attrs={"class":"displayClass"})
        for lecture_div in lecture_divs:
            title = lecture_div.find("h2",attrs={"class":"uu-routine-title"}).get_text()
            body=lecture_div.find("div", attrs={"class":"uu-routine-item-body"}).get_text().split("\n")
            lecture_body = []
            for _ in body:
                if not _.strip()=="":
                    lecture_body.append(_.strip())
            result["lectures"].append({
                "title":title,
                "description": lecture_body[0],
                "time":lecture_body[2],
                "course": lecture_body[-1]
            })

        exam_divs = exam_soup.find_all("div",attrs={"class":"displayClass"})
        for exam_div in exam_divs:
            title = "".join(exam_div.find("h2",attrs={"class":"uu-routine-title"}).get_text()).strip()
            body = exam_div.find("div", attrs={"class":"uu-routine-item-body"}).get_text().split("\n")
            exam_body = []
            for _ in body:
                if not _.strip()=="":
                    exam_body.append(_.strip())
            # print(exam_body)
            ExamLink=None
            if exam_body[-1]=="You haven't taken the exam yet":
                ExamLink = exam_div.find("a",attrs={"class":"uu-button-style-4"}).get("href")
            result["exams"].append({
                "title":title,
                "time": " ".join([exam_body[1],exam_body[2]]),
                "duration": exam_body[4],
                "course": exam_body[-2],
                "status": exam_body[-1],
                "link": ExamLink
            })
        
        return result
    

    def getClassContent(self,classLink):
        res = self.session.get(classLink)
        # print(res.text)
        result={
            "video":"",
            "title":"",
            "notes":""
        }
        if "initYoutubePlayer(containerId, videoId, thumbnailSrc, topOverlayText)" in res.text:
            #Youtube link is detected
            soup = BeautifulSoup(res.text,"html.parser")
            jscode = soup.find("div",attrs={"id":"video-tabContent"}).find("script").contents
            jscode = "".join([i.strip() for i in jscode])
            video_id = re.findall("let videoId = '((.)*)';",jscode)[0][0]
            video_title = re.findall("let topOverlayText = '((.)*)';",jscode)[0][0]

            result["video"]= "https://youtube.com/watch?v="+video_id
            result["title"]= video_title
        else:
            # Using Udvash's own CDN
            soup = BeautifulSoup(res.text,"html.parser")
            link = soup.find("video",attrs={"id":"video_1"}).find("source").get("src")
            title = re.findall('<h4 class="mb-lg-0 mb-2">((.)*)<\/h4>',res.text)[0][0]

            result["video"] = link
            result["title"] = title
        
        #fetching notes
        url_parts = classLink.split("/")[:-1]
        url_args = classLink.split("?")[-1]
        notes_base_url = "/".join(url_parts)+"/ViewClassNote?"+url_args
        res = self.session.get(notes_base_url)
        soup = BeautifulSoup(res.text,"html.parser")
        note_raw_link = soup.find("a", attrs={"class":"btn btn-success btn-sm"}).get("href")
        result ["notes"] = note_raw_link
        return result

    def _parseSingleQuestionSource(self,link):
        res = self.session.get(link)
        soup = BeautifulSoup(res.text,"html.parser")
        return soup.find("input",attrs={"id":"mcqAnalysisPdf"}).get("value").replace(" ","%20")


    def getExamContent(self,examLink):
        # Only designed to extract In-Branch Exam's Question and Solves
        result = {
            "courseName":"",
            "examName":"",
            "links":[]
        }
        res = self.session.get(examLink)
        soup = BeautifulSoup(res.text,"html.parser")
        papers = soup.find_all("div",attrs={"class":"TakeExamHeader"})
        details_section = papers[0]
        result["courseName"] = details_section.find("h2").get_text()
        result["examName"] = details_section.find_all("h3")[-1].get_text()
        for paper in papers[1::]:
            paper_title = paper.find("div",attrs={"class":"col text-left"}).find("h2").get_text().replace(":","")
            paper_types = paper.find("div",attrs={"class":"col text-right"}).find_all("a")
            for paper_type in paper_types:
                paper_cat = paper_type.find("span",attrs={"class":"linkspan"}).get_text()
                result["links"].append({
                    "title":f"{paper_title} - {paper_cat}.pdf",
                    "link":self._parseSingleQuestionSource(f"https://online.udvash-unmesh.com{paper_type.get('href')}")
                })

        return result
    
