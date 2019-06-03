import yaml
import unittest
import multiprocessing
import atexit
import os
import sys
import time
from importlib import import_module
from globalvar import desireCap, info
from supportiveFunction import fetchyaml, screenRecord
from HtmlTestRunner import HTMLTestRunner
OUTSUFFIX = time.strftime("%Y-%m-%d_%H-%M-%S")
ROOTPATH = os.path.abspath('.')
DEBUG_DEVICE = 0
REMOTE_URL = (0, 'http://domain.com')
RECORD = 1
# Load argument from shell
device_dict = {'Android': 'mobile', 'iOS': 'mobile', 'Chrome': 'web'}
if len(sys.argv) > 1:
    if str(sys.argv[1]) in device_dict.keys():
        device_type = str(sys.argv[1])
    else:
        device_type = 'Android'
else:
    device_type = 'Android'

info.platform = device_type

if len(sys.argv) > 2:
    if str(sys.argv[2]) == 'DEBUG':
        DEBUG_DEVICE = 1

with open(os.path.join(ROOTPATH, device_dict[device_type], 'config/test_order.yaml')) as order:
    usecase = yaml.load(order)
    info.lastTestCase = usecase['file'][-1]

if DEBUG_DEVICE:
    try:
        with open(os.path.join(ROOTPATH, device_dict[device_type], 'config/devConfig.yaml')) as conf:
            devConfig = yaml.load(conf)

        desireCap.all.update(devConfig['DEBUG_DEVICE'][device_type])

    except:
        print('Need devConfig file')

if REMOTE_URL[0]:
    info.url = REMOTE_URL[1] + '/wd/hub'

recording = screenRecord(path=os.path.join(
    ROOTPATH, device_dict[device_type], 'video'), outsuffix=OUTSUFFIX)

if device_dict[device_type] == 'web':
    info.url = 'http://127.0.0.1:9515'
    desireCap.all.update({'goog:chromeOptions': {'args': [
        'start-maximized', '--google-base-url https://domain.com/']}})


def stopRecord(recordState, process):
    if RECORD:
        recording.stop(recordState)
        # Make sure main process be closed at last
        process.join(timeout=60)


def main():
    if RECORD:
        recordState = multiprocessing.Queue()
        # For add subtitle
        info.recordstate = recordState
        videoP = multiprocessing.Process(target=recording.start,
                                         args=(recordState,),
                                         daemon=True)
        videoP.start()
        # Make video will not broken
        atexit.register(stopRecord, recordState, videoP)

    runner = HTMLTestRunner(
        output=os.path.join(device_dict[device_type], 'reports', device_type),
        mobileType=device_type,
        outsuffix=OUTSUFFIX)
    # Import test module && Load test case && Execute test
    suite = unittest.TestSuite()
    for testFile in usecase['file']:
        case_list = usecase[usecase[testFile]]
        globals().update(
            {testFile: import_module('{}.testcase.{}'.format(device_dict[device_type], testFile))})
        if case_list:
            suite.addTests(fetchyaml().testorder(
                getattr(eval(testFile), usecase[testFile]), case_list))

    info.testsStartTime = time.time()
    result, testReportName, testCaseResult = runner.run(suite)


if __name__ == '__main__':
    main()
