import unittest
from ddt import ddt, data, unpack
from .pageObject import landingPage, loginPage
from globalvar import info
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
           .enter_login_page()
        cls.pageDriver.click('login_with_email_button')

        cls.pageDriver = loginPage(info.driver)

    @loginPage.flowCtl()
    def setUp(self):
        self.pageDriver \
            .waitItem('userid_field') \
            .check_username_password_field()

    @loginPage.flowCtl()
    @data(info.login_username_password[0],
          info.login_username_password[1])
    @unpack
    def test_login_fail(self, user, password):
        self.pageDriver \
            .enter_username(user) \
            .enter_password(password) \
            .click_login_button()

        self.assertTrue(self.pageDriver.display('dismiss_button'))

    @classmethod
    @serverConnect('off')
    @loginPage.flowCtl()
    def tearDownClass(cls):
        pass
