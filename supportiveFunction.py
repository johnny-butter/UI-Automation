import re
import os
import sys
import unittest
import cv2
import numpy as np
import threading
from PIL import ImageGrab
from functools import wraps
from time import sleep, time
from appium.webdriver.common.mobileby import MobileBy as By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from unittest.loader import TestLoader
from HtmlTestRunner.result import _HtmlTestResult as htmlResult
from globalvar import dependency, ui, info, desireCap
from appium import webdriver
getTestCase = TestLoader().getTestCaseNames


class fetchyaml(object):

    def locate_method(self, method):
        if method == 'ID':
            return By.ID
        elif method == 'XPATH':
            return By.XPATH
        elif method == 'CLASSNAME':
            return By.CLASS_NAME
        elif method == 'ANDROID_UI':
            return By.ANDROID_UIAUTOMATOR
        elif method == 'IOS_PREDICATE':
            return By.IOS_PREDICATE
        elif method == 'ACCESS_ID':
            return By.ACCESSIBILITY_ID
        elif method == 'IMAGE':
            return By.IMAGE
        elif method == 'CSS':
            return By.CSS_SELECTOR
        elif method == 'LINK_TEXT':
            return By.LINK_TEXT

    def testorder(self, plan, case):
        testList = []
        contain = getTestCase(plan)
        for i in case:
            if i in contain:
                testList.append(contain[contain.index(i)])
            else:
                # Make sure ddt cases will be loaded
                for j in contain:
                    if bool(re.search('^' + i + '_', j)):
                        testList.append(contain[contain.index(j)])
        testList = list(map(plan, testList))
        return testList


class simplify:

    def __init__(self, driver, testdata=None):
        self.driver = driver

    def testName(self, source, sub=False, cls=None):
        if sub:
            return source._subtest.id().split('.')[-1]
        if cls:
            return '%s (%s.%s)' % (cls.__name__, cls.__module__, source.__name__)
        return source.__str__()

    def Item(self, item, key=None):
        component = getattr(ui, item, None)
        if isinstance(component, list):
            locateMethod = fetchyaml().locate_method(component[0])

            if key:
                componentLocate = ui.replaceKeyWord(
                    component, changeToThis=key)
            else:
                componentLocate = component[1]

            return locateMethod, componentLocate
        else:
            return component

    def findItem(self, item, key=None):
        x, y = self.Item(item, key=key)
        return self.driver.find_element(x, y)

    def findItems(self, item, key=None):
        x, y = self.Item(item, key=key)
        return self.driver.find_elements(x, y)

    def getText(self, item):
        if info.platform == 'Android':
            return self.findItem(item).get_attribute('text')
        if info.platform == 'iOS':
            return self.findItem(item).get_attribute('value')

    def get_screenshot(self):
        return self.driver.get_screenshot_as_base64()

    def waitItem(self, item, ec_method='presence_of_element_located', time=30):
        x, y = self.Item(item)
        if ec_method == 'presence_of_element_located':
            WebDriverWait(self.driver, time, 1).until(
                ec.presence_of_element_located((x, y)))
        return self

    def click(self, item, key=None, delay=1):
        self.findItem(item, key=key).click()
        sleep(delay)
        return self

    def tap(self, item, key=None, distance=0, delay=1, width_percentage=0.67):
        L = self.findItem(item, key=key).location
        S = self.findItem(item, key=key).size
        self.driver.tap([(L['x'] + (S['width'] * width_percentage),
                          L['y'] + (S['height'] * 0.5 + distance))], 100)
        sleep(delay)
        return self

    def scrollPage(self, startItem, endItem=None, distance=300, shift=0):
        Ssize = self.findItem(startItem).size
        S = self.findItem(startItem).location
        if distance >= 0 and endItem:
            E = self.findItem(endItem).location
            self.driver.swipe(S['x'], S['y'] + Ssize['height'] + shift,
                              E['x'], E['y'], 300)
        elif distance < 0 and endItem:
            Esize = self.findItem(endItem).size
            E = self.findItem(endItem).location
            self.driver.swipe(S['x'], S['y'] - shift,
                              E['x'], E['y'] + Esize['height'], 300)
        else:
            if distance >= 0:
                self.driver.swipe(S['x'], S['y'] + Ssize['height'],
                                  S['x'], S['y'] + distance, 300)
            else:
                self.driver.swipe(S['x'], S['y'],
                                  S['x'], S['y'] + distance, 300)
        return self

    def display(self, item, key=None):
        try:
            result = self.findItem(item, key=key).is_displayed()
        except:
            result = False
        return result

    def appBackground(self, time=3):
        self.driver.background_app(time)
        return self

    def skip_case(self, condition):
        if isinstance(condition, dict):
            conditionList = list(condition.keys())
            for i in conditionList:
                if getattr(dependency, i) or getattr(dependency, i) is None:
                    raise unittest.SkipTest(condition[i])

    def fail_case(self, condition):
        if isinstance(condition, dict):
            conditionList = list(condition.keys())
            for i in conditionList:
                if getattr(dependency, i) or getattr(dependency, i) is None:
                    raise AssertionError(condition[i])

    def exeCondintion(self, skipCondition=None, failCondition=None):
        try:
            self.skip_case(skipCondition)
        except:
            raise
        else:
            isSkip = False
        self.fail_case(failCondition)
        return isSkip

    def storeErrorImg(self, instance, func, sub=False):
        if type(instance).__name__ == 'type':
            htmlResult.imgrecord[self.testName(
                instance, cls=func)] = self.get_screenshot()
        else:
            htmlResult.imgrecord[self.testName(
                instance, sub=sub)] = self.get_screenshot()

    @staticmethod
    def flowCtl(sub=False, skipCondition=None, failCondition=None, depend=None, end=False):

        def decorator(func):

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                isSkip = True
                if depend:
                    setattr(dependency, depend, False)

                if info.recordstate:
                    caseName = '{} ({})'.format(func.__name__, func.__module__)
                    screenRecord.addSubtitle(
                        self, info.recordstate, caseName)

                try:
                    # setUpClass not support skip/fail condition
                    # cause pageDriver is not init yet
                    if skipCondition or failCondition:
                        if hasattr(self, 'pageDriver'):
                            isSkip = self.pageDriver.exeCondintion(
                                skipCondition=skipCondition, failCondition=failCondition)
                        else:
                            sys.stderr.write('Must init pageDriver first')
                    else:
                        isSkip = False

                    func(self, *args, **kwargs)
                except:
                    info.successCounter -= 1
                    if depend:
                        setattr(dependency, depend, True)

                    if func.__module__ not in info.retryList and not isSkip:
                        info.retryList.append(func.__module__)

                    self.pageDriver.storeErrorImg(self, func, sub=sub)

                    raise
                finally:
                    if isinstance(end, list) and not isSkip:
                        for endFunc in end:
                            exec(endFunc)
                            sleep(1)
                    info.successCounter += 1

            return wrapper

        return decorator

    @staticmethod
    def endTestFast():
        timeDelta = time() - info.testsStartTime
        if info.successCounter < int(timeDelta / 600):
            raise AssertionError('Time out')


class serverConnect:

    def __init__(self, switch, waitTime=10, noReset=False, wipe=False,
                 caps_Android=None, caps_iOS=None, caps_Chrome=None, forceRestart=False):
        self.switch = switch
        self.waitTime = waitTime
        self.forceRestart = forceRestart
        self.caps = eval('caps_' + info.platform)

        if noReset:
            self.common_caps = {'noReset': 'true'}
        else:
            self.common_caps = {'noReset': 'false'}

        # Make Android restart emulator and wipe data
        if wipe and info.platform == 'Android':
            self.common_caps.update(
                {'avdArgs': '-gpu host -wipe-data -no-boot-anim -no-snapshot'})

    def on(self, func):
        if info.driver:
            return 'Server already connected'

        desireCap.all.update(self.common_caps)

        if self.caps and isinstance(self.caps, dict):
            desireCap.all.update(self.caps)

        driver = webdriver.Remote(info.url, desireCap.all)
        driver.implicitly_wait(self.waitTime)
        info.driver = driver

    def off(self):
        if not info.driver:
            return 'Not connect to server yet'

        info.driver.quit()
        info.driver = None

        if info.platform == 'Android':
            # Remove wipe data args to prevent re-start emulator
            desireCap.all.update(
                {'avdArgs': '-gpu host -no-boot-anim -no-snapshot'})

    def __call__(self, func):

        @wraps(func)
        def decorator(*args, **kwargs):
            if func.__name__ in ['setUpClass', 'tearDownClass']:
                if self.switch == 'on':
                    if self.forceRestart:
                        self.off()
                        sleep(5)
                    self.on(func)
                try:
                    func(*args, **kwargs)
                except:
                    # If error occur in setUpClass, make sure driver will close
                    if func.__name__ == 'setUpClass':
                        self.off()
                    raise
                finally:
                    if (self.switch == 'off' and len(info.retryList) > info.retryNum) \
                            or (info.lastTestCase in func.__module__ and func.__name__ == 'tearDownClass'):
                        info.retryNum = len(info.retryList)
                        self.off()
        return decorator


class screenRecord:

    def __init__(self, path='', outsuffix=''):
        self.path = path
        self.outsuffix = outsuffix
        self.videoName = 'Report_{}_{}.mp4'.format(info.platform, outsuffix)
        screen = ImageGrab.grab()
        self.width, self.height = screen.size

    def start(self, recordState):
        status, subtitle = None, 'Test Start'
        spacing = len(subtitle) * 32 + 50

        def getStatus(rState):
            nonlocal status, spacing, subtitle
            while True:
                try:
                    status = rState.get(block=False)
                    if status == 'close':
                        break
                    else:
                        subtitle = status
                        spacing = len(subtitle) * 20 + 20
                except:
                    status = None
            sleep(1)

        # four character code object for video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4a')
        # video writer object
        self.output = cv2.VideoWriter(os.path.join(
            self.path, info.platform, self.videoName), fourcc, 3, (self.width, self.height))
        threading.Thread(target=getStatus, args=(
            recordState,), daemon=True).start()
        while True:
            # capture computer screen
            img = ImageGrab.grab()
            # convert image to numpy array
            img_np = np.array(img)
            # add subtitle parameters: image, string, string location, font type,
            # font size(*10 pt about *26 px), font color, font thickness
            cv2.putText(img_np, subtitle, (self.width - spacing,
                                           int(self.height / 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # convert color space from BGR to RGB
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            # show image on OpenCV frame
            cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Screen', 50, 50)
            cv2.moveWindow('Screen', self.width, self.height)
            cv2.imshow('Screen', frame)
            # write frame to video writer
            self.output.write(frame)
            # wait = X ms; 27 == "esc"
            if cv2.waitKey(1) == 27 or status == 'close':
                break

        self.output.release()
        cv2.destroyAllWindows()

    def stop(self, recordState):
        recordState.put('close')

    def addSubtitle(self, recordState, subtitle):
        recordState.put(str(subtitle))
