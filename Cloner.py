import os
import requests
import shutil
from bs4 import BeautifulSoup
#import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("C:/Users/MicroMediA  o5/Desktop/clone/clone/GUI.ui")

def save(bs, element, check):
    global site_name
    global project_path
    global project_name
    global folder_name
    global visited_links
    global error_links
    links = bs.find_all(element)

    for l in links:
        href = l.get("href")
        if href is not None and href not in visited_links:
            if check in href:
                href = l.get("href")
                print("Working with : {}".format(href))
                if "//" in href:
                    path_s = href.split("/")
                    file_name = ""
                    for i in range(3, len(path_s)):
                        file_name = file_name + "/" + path_s[i]
                else:
                    file_name = href

                l = site_name + file_name

                try:
                    r = requests.get(l)
                except requests.exceptions.ConnectionError:
                    error_links.append(l)
                    continue

                if r.status_code != 200:
                    error_links.append(l)
                    continue

                os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]), exist_ok=True)
                with open(project_path + file_name.split("?")[0], "wb") as f:
                    f.write(r.text.encode('utf-8'))
                    f.close()

                visited_links.append(l)


def save_assets(html_text):
    global site_name
    global project_path
    global folder_name
    global visited_links
    global error_links
    global project_name
    bs = BeautifulSoup(html_text, "html.parser")
    save(bs=bs, element="link", check=".css")
    save(bs=bs, element="script", check=".js")

    links = bs.find_all("img")
    for l in links:
        href = l.get("src")
        if href is not None and href not in visited_links:
            print("Working with : {}".format(href))
            if "//" in href:
                path_s = href.split("/")
                file_name = ""
                for i in range(3, len(path_s)):
                    file_name = file_name + "/" + path_s[i]
            else:
                file_name = href

            l = site_name + file_name

            try:
                r = requests.get(l, stream=True)
            except requests.exceptions.ConnectionError:
                error_links.append(l)
                continue

            if r.status_code != 200:
                error_links.append(l)
                continue

            os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]), exist_ok=True)
            with open(project_path + file_name.split("?")[0], "wb") as f:
                shutil.copyfileobj(r.raw, f)

            visited_links.append(l)


def crawl(link):
    global site_name
    global folder_name
    global visited_links
    global error_links
    global project_path
    global project_name
    if "http://" not in link and "https://" not in link:
        link = site_name + link

    if site_name in link and link not in visited_links:
        print("Working with : {}".format(link))

        path_s = link.split("/")
        file_name = ""
        for i in range(3, len(path_s)):
            file_name = file_name + "/" + path_s[i]

        if file_name[len(file_name) - 1] != "/":
            file_name = file_name + "/"

        try:
            r = requests.get(link)
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            sys.exit(1)

        if r.status_code != 200:
            print("Invalid Response")
            sys.exit(1)
        print(project_path + file_name + "index.html")
        os.makedirs(os.path.dirname(project_path + file_name.split("?")[0]), exist_ok=True)
        with open(project_path + file_name.split("?")[0] + "index.html", "wb") as f:
            text = r.text.replace(site_name, project_name)
            f.write(text.encode('utf-8'))
            f.close()

        visited_links.append(link)

        save_assets(r.text)

        soup = BeautifulSoup(r.text, "html.parser")

        for link in soup.find_all('a'):
            try:
                crawl(link.get("href"))
            except:
                error_links.append(link.get("href"))



def startCrawl(url,folder="Default"):
    global site_name
    global folder_name
    global visited_links
    global error_links
    global project_path
    global project_name
    base_dir = os.getcwd()
    try:
        site_name=url
        project_name=folder
    except IndexError:
        print("Usage:\npython app.py www.example.com folder_name")
        sys.exit(1)
    project_path = "../" + project_name +"/"
    os.makedirs(project_path, exist_ok=True)

    visited_links = []
    error_links = []
    crawl(site_name + "/")
    print("Link crawled\n")
    for link in visited_links:
        print("---- {}\n".format(link))

    print("\n\n\nLink error\n")
    for link in error_links:
        print("---- {}\n".format(link))


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.submit.clicked.connect(self.passValues)

    def passValues(self):
        startCrawl(self.ui.url.text(),self.ui.folder.text())
 

if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
    # sys.exit(app.exec_())

