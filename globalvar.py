import os
import sys
import yaml
import base64
from datetime import datetime

ROOTPATH = os.path.abspath('.')
DEVICE_DICT = {'Android': 'mobile', 'iOS': 'mobile', 'Chrome': 'web'}
DEVICE_TYPE = sys.argv[1] if len(
    sys.argv) > 1 and sys.argv[1] in DEVICE_DICT else 'Android'


class information:
    url = 'http://127.0.0.1:4723/wd/hub'
    driver = None
    platform = None
    recordstate = None
    testsStartTime = None
    successCounter = 0
    retryList = []
    retryNum = 0
    lastTestCase = None
    timenow = '-{}'.format(datetime.strftime(
        datetime.now(), '%m%d%I%M'))


class testData(information):
    with open(os.path.join(ROOTPATH, DEVICE_DICT[DEVICE_TYPE], 'config',
                           DEVICE_TYPE + '_config.yaml'), encoding='utf-8') as c:
        testConfig = yaml.load(c)

    keySymbol = '___'

    def __init__(self, configType):
        self.configType = configType

    def __setattr__(self, name, value):
        if name == 'configType':
            self.__dict__[name] = value
            return

        if self.configType == 'desired_caps' and name in self.testConfig['desired_caps']:
            self.testConfig['desired_caps'][name] = value
        else:
            self.__dict__[name] = value

    def __getattribute__(self, item):
        if item == '__dict__':
            return super(testData, self).__getattribute__(item)

        if hasattr(information, item):
            if super(testData, self).__getattribute__('configType') == 'default':
                return super(testData, self).__getattribute__(item)
            else:
                raise AttributeError('There is no value')

        return super(testData, self).__getattribute__(item)

    def __getattr__(self, item):
        if item == 'all':
            return self.testConfig[self.configType]

        if self.configType == 'uicomponent':
            self.replaceKeyWord(self.testConfig[self.configType][item])

        return self.testConfig[self.configType][item]

    def replaceKeyWord(self, component, changeToThis='default'):
        '''
        Replace particular key word to default value
        (e.g. ___username___(must same as key in default))
        '''
        if self.keySymbol in component[1] and isinstance(component, list):
            resolveComponent = component[1].split(self.keySymbol)
            relplaceKey = resolveComponent[1]

            if changeToThis == 'default':
                if relplaceKey in self.testConfig['default']:
                    resolveComponent[1] = self.testConfig['default'][relplaceKey]
                    component[1] = ''.join(resolveComponent)
            else:
                resolveComponent[1] = changeToThis
                return ''.join(resolveComponent)


ui = testData('uicomponent')
info = testData('default')
desireCap = testData('desired_caps')
