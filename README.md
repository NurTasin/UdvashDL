# Udvash Class Documentation

The `Udvash` class is a Python class designed to facilitate interaction with the Udvash Unmesh Online platform. This class provides methods for logging in, retrieving class routines, accessing class content, and fetching exam-related information. This documentation provides comprehensive details and examples for each method and its usage.

## Table of Contents

1. [Class Initialization](#class-initialization)
2. [Logging In](#logging-in)
3. [Getting Class Routine](#getting-class-routine)
4. [Getting Class Content](#getting-class-content)
5. [Getting Exam Content](#getting-exam-content)
6. [Internal Methods](#internal-methods)
7. [CLI Usage](#cli-usage)

---

### 1. Class Initialization <a name="class-initialization"></a>

The `Udvash` class constructor initializes the object and sets up the session with the Udvash Unmesh Online platform. You can create an instance of the class with the following parameters:

- `regnum` (str, optional): Registration number for Udvash Unmesh Online. If not provided, it will be prompted for during login.
- `password` (str, optional): Password for Udvash Unmesh Online. If not provided, it will be prompted for during login.
- `cookiepath` (str, optional): Path to a file where cookies will be stored. If not provided, it defaults to "./cookie.txt".

```python
from udvash import Udvash

# Example Usage
udvash = Udvash(regnum="your_registration_number", password="your_password")
```

### 2. Logging In <a name="logging-in"></a>

The `Udvash` class handles login internally without exposing the specific login function. The `__init__` method takes care of the login process. Here's what happens during initialization:

- If a cookie file exists, it will be used for authentication.
- If a cookie file is not found, and no credentials are provided during initialization, it will prompt for credentials.
- If a cookie file is not found but credentials are provided during initialization, it will use the provided credentials to log in.

```python
from udvash import Udvash

# Example Usage with Provided Credentials
udvash = Udvash(regnum="your_registration_number", password="your_password")

# Example Usage without Credentials (Prompts for Credentials)
udvash = Udvash()
```

### 3. Getting Class Routine <a name="getting-class-routine"></a>

#### `getRoutine()`

This method retrieves the class routine, including both lectures and exams, and returns the data as a dictionary.

**Example:**

```python
routine = udvash.getRoutine()
print(routine)
```

The returned dictionary has the following structure:

```python
{
    "lectures": [
        {
            "title": "Lecture Title",
            "description": "Lecture Description",
            "time": "Lecture Time",
            "course": "Course Name"
        },
        # ...
    ],
    "exams": [
        {
            "title": "Exam Title",
            "time": "Exam Time",
            "duration": "Exam Duration",
            "course": "Course Name",
            "status": "Exam Status",
            "link": "Exam Link (if available)"
        },
        # ...
    ]
}
```

### 4. Getting Class Content <a name="getting-class-content"></a>

#### `getClassContent(classLink)`

This method retrieves class content, including video links and notes, for a given class link.

- `classLink` (str): URL of the class.

**Example:**

```python
class_link = "https://online.udvash-unmesh.com/your_class_link"
class_content = udvash.getClassContent(class_link)
print(class_content)
```

The returned dictionary has the following structure:

```python
{
    "video": "Video Link (YouTube or Udvash CDN)",
    "title": "Class Title",
    "notes": "Link to Class Notes (if available)"
}
```

### 5. Getting Exam Content <a name="getting-exam-content"></a>

#### `getExamContent(examLink)`

This method retrieves exam-related content, specifically for in-branch exams. It provides details about the course, exam name, and links to download question papers.

- `examLink` (str): URL of the exam.

**Example:**

```python
exam_link = "https://online.udvash-unmesh.com/your_exam_link"
exam_content = udvash.getExamContent(exam_link)
print(exam_content)
```

The returned dictionary has the following structure:

```python
{
    "courseName": "Course Name",
    "examName": "Exam Name",
    "links": [
        {
            "title": "Paper Title",
            "link": "Link to Download Paper (PDF)"
        },
        # ...
    ]
}
```

### 6. Internal Methods <a name="internal-methods"></a>

These methods are used internally within the class and are not intended for external use:

- `_loginWithCreds(regnum,password)`: Logs in using provided registration number and password and saves the cookie to `./cookie.txt`.
- `_loginWithCookie(cookiepath)`: Logs in using stored cookies from the specified `cookiepath`.
- `_parseSingleQuestionSource(link)`: Parses a single question source link from the exam page.

---

This documentation provides comprehensive details and examples for each method of the `Udvash` class. You can use this class to interact with the Udvash Unmesh Online platform, retrieve class routines, access class content, and fetch exam-related information.


## Command-Line Interface (CLI) Usage <a name="cli-usage"></a>

The `udvashdl` script is a command-line tool designed to extract various contents (class, notes, exam questions) from the Udvash Unmesh Online platform. This section explains how to use the `udvashdl` script and its available command-line options.

### Installation

Before using the `udvashdl` script, ensure that you have the required dependencies installed:

- Python (3.x)
- `yt-dlp` (for downloading videos)
- `wget` (for downloading files)

You can install `yt-dlp` and `wget` using the following commands:

```bash
pip install yt-dlp
```

### Usage

To use the `udvashdl` script, open a terminal and run the following command:

```bash
python udvashdl.py [OPTIONS] CONTENT_LINK
```

Replace `CONTENT_LINK` with the URL of the content you want to extract from the Udvash Unmesh Online platform.

#### Available Options

- `--login`: Logs you in interactively and saves the cookie, then exits.
- `-R`, `--reg-num`: Udvash Registration Number.
- `-P`, `--password`: Password for Udvash's web app.
- `--cookie`: Path to the cookie file or where to save the cookie for fast login.
- `-N`, `--only-note`: Skips downloading the video lecture and only downloads the note.
- `-V`, `--only-video`: Skips downloading the note lecture and only downloads the video.
- `CONTENT_LINK`: URL of the content you want to extract.

#### Examples

1. Interactive login and save the cookie:

```bash
python udvashdl.py --login
```

2. Login with provided registration number and password:

```bash
python udvashdl.py -R your_registration_number -P your_password CONTENT_LINK
```

3. Login with a provided cookie file:

```bash
python udvashdl.py --cookie your_cookie_file_path CONTENT_LINK
```

4. Download class content (video and notes):

```bash
python udvashdl.py CONTENT_LINK
```

5. Download class notes only:

```bash
python udvashdl.py -N CONTENT_LINK
```

6. Download class video only:

```bash
python udvashdl.py -V CONTENT_LINK
```

7. Download exam question papers:

```bash
python udvashdl.py QUESTION_HUB_LINK
```

### Output Directory

The script will create the following directory structure to organize downloaded content:

- `UdvashDL`
  - `Lectures` (for class content)
    - `Lecture Title`
      - `Lecture Title.pdf` (notes)
      - `Lecture Title.mp4` (video)
  - `Questions` (for exam question papers)
    - `Course Name`
      - `Exam Name`
        - `Paper Title`

### Note

- Ensure that you have the necessary permissions to create directories and download files in the current working directory.
- Some content extraction options may require the installation of additional tools (e.g., `yt-dlp` and `wget`) to download videos and files.

### Disclaimer

This application, `udvashdl`, is created and provided solely for educational purposes. It is designed to facilitate the extraction of educational content from the Udvash Unmesh Online platform. The author of this application does not condone or endorse any form of piracy, copyright infringement, or any other illegal activity.

**Usage of this application for any purpose other than educational and personal use may infringe on the terms of service and policies of the Udvash Unmesh Online platform and local copyright laws. Users are responsible for complying with all applicable laws and regulations.**

The author of this application shall not be held responsible for any misuse, harm, legal consequences, or piracy that may arise from the use of this application. Users are strongly encouraged to use this tool responsibly and in accordance with applicable laws.

By using this application, you acknowledge and agree to the above disclaimer and the intended educational purpose of this tool.

> This documentation was generated using ChatGPT