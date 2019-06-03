from supportiveFunction import simplify
from time import sleep


class landingPage(simplify):

    def enter_login_page(self):
        self.click('login_button')


class loginPage(simplify):

    def __init__(self, driver, testdata):
        super(loginPage, self).__init__(driver, testdata)
        self.username = self.findItem('login_page_email')
        self.password = self.findItem('login_page_pass')

    def check_username_password_field(self):
        if self.getText('login_page_email') != '':
            self.username.clear()
            sleep(1)
            self.password.clear()
            sleep(1)

    def enter_username(self, username):
        self.username.send_keys(username)
        sleep(1)
        return self

    def enter_password(self, password):
        self.password.send_keys(password)
        sleep(3)
        return self

    def click_login_button(self):
        self.click('login_enter_button')
        return self
