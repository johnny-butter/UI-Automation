import unittest
from ddt import ddt, data, unpack
from ..pageObject import landingPage, loginPage
from globalvar import ui, info
from supportiveFunction import serverConnect


def setUpModule():
    loginPage.endTestFast()


@ddt
class loginTestCase(unittest.TestCase):

    @classmethod
    @serverConnect('on', forceRestart=True)
    @loginPage.flowCtl()
    def setUpClass(cls):
        cls.pageDriver = landingPage(info.driver)
        cls.pageDriver\
           .add_quota_to_student(info.userid) \
           .enter_login_page()

        cls.pageDriver = loginPage(info.driver)

    @loginPage.flowCtl()
    def setUp(self):
        self.pageDriver \
            .waitItem('userid_field') \
            .check_username_password_field()

    @loginPage.flowCtl(end=['self.pageDriver.swipe_to_email_login()'])
    def test_phone_login_page(self):
        self.pageDriver \
            .swipe_to_phone_login()

        self.assertTrue(self.pageDriver.display('phone_field'))

    @loginPage.flowCtl(end=['self.pageDriver.click("dismiss_button")'])
    @data(ui.login_username_password[0],
          ui.login_username_password[1])
    @unpack
    def test_login_fail(self, user, password):
        self.pageDriver \
            .enter_username(user) \
            .enter_password(password) \
            .click_login_button()

        self.assertTrue(self.pageDriver.display('dismiss_button'))

    @loginPage.flowCtl(depend='LOGIN_FAIL')
    def test_login(self):
        self.pageDriver \
            .enter_username(ui.login_username_password[2]['user']) \
            .enter_password(ui.login_username_password[2]['password']) \
            .click_login_button(isCorrectUser=True)

        self.assertTrue(self.pageDriver.display('ask_button_top'))

    @classmethod
    @serverConnect('off')
    @loginPage.flowCtl()
    def tearDownClass(cls):
        pass
