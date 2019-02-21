import sys
import time
import smtplib
import mechanicalsoup
from getpass import getpass
from datetime import datetime


class LibraryReissuer:

    def __init__(self, username, password, mail_username, mail_password):
        self.start_time = time.time()
        self.login_url = "http://14.139.108.229/W27/login.aspx?ReturnUrl=%2fW27%2fMyInfo%2fw27MyInfo.aspx"
        self.browser = mechanicalsoup.StatefulBrowser()
        self.username = username
        self.password = password
        self.user_data = {}
        self.index = 0
        self.my_info_page = None
        self.table = None
        self.response = None
        self.mailer = smtplib.SMTP('smtp.gmail.com', 587)
        self.mailer.starttls()
        try:
            self.mailer.login(mail_username, mail_password)
        except SMTPAuthenticationError:
            print("Wrong GMail Password.")
            sys.exit()
        print("Logged in. SMTP.")
        self.mail_username = mail_username
        self.mail_password = mail_password

    def login(self):
        self.browser.open(self.login_url)
        self.browser.select_form()
        self.browser['txtUserName'] = self.username
        self.browser['Password1'] = self.password
        self.browser.submit_selected()
        if self.browser.get_url() == 'http://14.139.108.229/W27/SlimError.aspx?aspxerrorpath=/W27/SlimError.aspx':
            print("Login Error")
            return
        elif self.browser.get_url() == "http://14.139.108.229/W27/login.aspx?ReturnUrl=%2fW27%2fMyInfo%2fw27MyInfo.aspx":
            print("Wrong Password")
            self.browser.close()
            sys.exit()
        else:
            print("Logged In!\n")
            self.my_info_page = self.browser.get_current_page()

    def check(self):
        self.table = self.my_info_page.find('table', id='ctl00_ContentPlaceHolder1_CtlMyLoans1_grdLoans')
        self.index = 0
        try:
            for book in self.table.find_all("tr"):
                if self.index == 0:
                    self.index += 1
                    continue
                self.user_data[self.index] = {}
                self.user_data[self.index]['book_no'] = book.find_all("td")[0].text.strip()
                self.user_data[self.index]['author'] = book.find_all("td")[2].text.strip()
                self.user_data[self.index]['name'] = book.find_all("td")[1].text.strip()
                self.user_data[self.index]['iss_date'] = datetime.strptime(book.find_all("td")[3].text.strip(), '%d-%b-%Y')
                self.user_data[self.index]['due_date'] = datetime.strptime(book.find_all("td")[4].text.strip(), '%d-%b-%Y')
                self.user_data[self.index]['status'] = book.find_all("td")[5].text.strip()
                self.user_data[self.index]['recalled'] = book.find_all("td")[6].text.strip()
                self.user_data[self.index]['fine_due'] = book.find_all("td")[7].text.strip()
                self.user_data[self.index]['time_remaining'] = (self.user_data[self.index]['due_date'] - datetime.
                                                                now()).days
                self.user_data[self.index]['reissue_button'] = book.find("input", type='submit')
                self.user_data[self.index]['reissue_button']['name'] = self.user_data[self.index]['reissue_button']['id'].replace("_", "$")

                self.index += 1
            for key, value in self.user_data.items():
                print(value['name'] + " :: " + str(value['time_remaining']))
                if value['time_remaining'] <= 0:
                    print("Time to reissue.")
                    if "disabled" in str(value['reissue_button']):
                        self.mail_type = "Manual Reissue :: "
                        self.current_book_data = value
                        self.send_mail()
                        print("REISSUE LIMIT OVER :: ", value['name'])
                        continue
                    print("Reissuing Book :: ", value['name'])
                    isDone = self.reissue(value)
                    if isDone:
                        print("Reissued.")
                        self.mail_type = "Reissued :: "
                        self.current_book_data = value
                        self.send_mail()
                        pass
                    else:
                        print("Error Reissuing.")
                        self.mail_type = "Error :: "
                        self.current_book_data = value
                        self.send_mail()
                        # return "Error Occured"
                elif value['time_remaining'] == 1:
                    self.mail_type = "One Day left :: "
                    self.current_book_data = value
                    self.send_mail()
                    # todo send notification via mail or message
                else:
                    pass
                    # todo nothing
        except AttributeError:
            print("No books issued.")

    def reissue(self, value):
        self.browser.open("http://14.139.108.229/W27/MyInfo/w27MyInfo.aspx")
        form = self.browser.select_form()
        form.choose_submit(value['reissue_button'])
        self.response = self.browser.submit_selected()

        if self.browser.get_current_page().find('span', id="ctl00_ContentPlaceHolder1_CtlMyLoans1_lblMsg").text == \
                "Can Not Re-Issue. The ReIssue limit Is Over!":
            print("Re-Issue limit is over!")
            return False
        if self.response.status_code != 200:
            print("Not able to reissue. Sorry :(")
            return False
        print("Book {} Reissued :)".format(value['name']))
        return True

    def flow(self):
        self.login()
        self.check()
        print("Closing StatefulBrowser.")
        self.browser.close()
        self.mailer.quit()
        print("Time Taken :: ", (time.time() - self.start_time))

    def send_mail(self):

        option_dict = {
            'Manual Reissue :: ': 'The reissue limit for the book {} is over. Please reissue it manually.',
            'Reissued :: ': 'Book {} reissued.',
            'Error :: ': 'Some error occured in reissueing the book {}.',
            'One Day left :: ': 'One day remaining from due date for book {}. If it is to be returned please do it immediately.'
        }
        SUBJECT = self.mail_type + " " + self.current_book_data['name']
        TEXT = option_dict[self.mail_type].format(self.current_book_data['name'])
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        self.mailer.sendmail(self.mail_username, self.mail_username, message)

    def __del__(self):

        # self.mailer.quit()
        self.browser.close()


if __name__ == "__main__":
    username = input("Username : ")
    password = getpass("Password : ")
    mail_username = input("Mail Username : ")
    mail_password = getpass("Mail Passsword : ")

    obj = LibraryReissuer(username, password, mail_username, mail_password)
    obj.flow()
