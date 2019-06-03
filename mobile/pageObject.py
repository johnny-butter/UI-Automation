import threading
from supportiveFunction import simplify
from globalvar import info
from time import sleep


class landingPage(simplify):

    def enter_login_page(self):
        if info.platform == 'iOS':
            try:
                self.waitItem('allow_button', time=90) \
                    .click('allow_button')
            except:
                pass
        self.click('login_button')

    def add_quota_to_student(self, studentId):

        def adding():
            info.addquotaStatus[0] = QuotaModify(
                studentId).addFreeQuota()

        threading.Thread(target=adding, daemon=True).start()
        return self


class loginPage(simplify):

    def __init__(self, driver):
        super(loginPage, self).__init__(driver)
        self.username = self.findItem('login_page_email')
        self.password = self.findItem('login_page_pass')

        self.height = int(self.username.location['y'])
        self.width = int(self.driver.get_window_size()['width'])

    def check_username_password_field(self):
        if self.getText('login_page_email') != '':
            self.username.clear()
            sleep(1)
            if info.platform == 'Android':
                self.driver.press_keycode('66')
            elif info.platform == 'iOS':
                self.driver.hide_keyboard(key_name='return')
            sleep(1)
            self.password.clear()
            sleep(1)

    def swipe_to_phone_login(self):
        self.waitItem('forgotpass_button')
        self.driver.swipe(0.87 * self.width, self.height,
                          0.09 * self.width, self.height, 500)
        sleep(1)

    def swipe_to_email_login(self):
        self.driver.swipe(0.09 * self.width, self.height,
                          0.87 * self.width, self.height, 500)

    def enter_username(self, username):
        self.username.send_keys(username)
        sleep(1)
        if info.platform == 'Android':
            self.driver.press_keycode('66')
        elif info.platform == 'iOS':
            self.driver.hide_keyboard(key_name='return')
        sleep(1)
        return self

    def enter_password(self, password):
        self.password.send_keys(password)
        sleep(3)
        return self

    def click_login_button(self, isCorrectUser=False):
        times = 0
        isAddQuotaReady = info.addquotaStatus[0]
        while not isAddQuotaReady and times < 3 and isCorrectUser:
            sleep(10)
            isAddQuotaReady = info.addquotaStatus[0]
            times += 1
        self.click('login_enter_button')
        return self
