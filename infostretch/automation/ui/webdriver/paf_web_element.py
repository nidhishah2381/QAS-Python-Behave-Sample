from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement
from selenium.webdriver.support.wait import WebDriverWait
import json
from infostretch.automation.core.message_type import MessageType
from infostretch.automation.ui.webdriver import base_driver
from infostretch.automation.ui.webdriver.paf_find_by import get_find_by
from infostretch.automation.core.configurations_manager import ConfigurationsManager
from infostretch.automation.core.load_class import load_class
from infostretch.automation.core.reporter import Reporter
from infostretch.automation.keys.application_properties import ApplicationProperties
from infostretch.automation.ui.util.paf_wd_expected_conditions import *
from infostretch.automation.ui.webdriver.command_tracker import Stage, CommandTracker


class PAFWebElement(RemoteWebElement):
    def __init__(self, key, cacheable=False):

        self.locator = None
        self.by = None
        self.description = None
        self._parent_element = None
        self._listeners = []
        self.cacheable = cacheable

        if isinstance(key, str) and len(key) > 0:
            value = ConfigurationsManager().get_str_for_key(key, default_value=key)
            #print("30"+value+" loading")
            try:
                locator = json.loads(value)['locator']
                # self.description = json.loads(value)['description']
            except ValueError:
                locator = value
                # self.description = value
            parent = base_driver.BaseDriver().get_driver()
            self.by, self.locator = get_find_by(locator)
            if parent.w3c and parent._is_remote is False:
                if self.by == By.ID:
                    self.by = By.CSS_SELECTOR
                    self.locator = '[id="%s"]' % self.locator
                elif self.by == By.TAG_NAME:
                        self.by = By.CSS_SELECTOR
                elif self.by == By.CLASS_NAME:
                        self.by = By.CSS_SELECTOR
                        self.locator = ".%s" % self.locator
                elif self.by == By.NAME:
                        self.by = By.CSS_SELECTOR
                        self.locator = '[name="%s"]' % self.locator
            self.description = self.locator
            self.cacheable = cacheable
            self._id = -1
            RemoteWebElement.__init__(self, parent=parent, id_=self.id, w3c=parent.w3c)

        if ConfigurationsManager().contains_key(ApplicationProperties.WEBELEMENT_COMMAND_LISTENERS):
            class_name = ConfigurationsManager().get_str_for_key(ApplicationProperties.WEBELEMENT_COMMAND_LISTENERS)
            self._listeners.append(load_class(class_name)())

    @classmethod
    def create_instance_using_webelement(cls, remote_webelement, cacheable=False):
        cls.locator = None
        cls.by = None
        cls.description = None
        cls._parent_element = None
        cls._listeners = []
        cls.cacheable = cacheable

        cls._id = remote_webelement.id
        cls._w3c = remote_webelement._w3c
        return cls(key='')

    def get_description(self, msg):
        return msg if (msg is not None and len(msg) > 0) else self.locator

    def find_element(self, by=By.ID, value=None):
        web_element = super(PAFWebElement, self).find_element(by=by, value=value)
        paf_web_element = PAFWebElement.create_instance_using_webelement(web_element)
        paf_web_element._parent_element = self
        paf_web_element._parent = self._parent_element.parent
        paf_web_element.by = by
        paf_web_element.locator = value
        paf_web_element.description = value
        return paf_web_element

    def find_elements(self, by=By.ID, value=None):
        web_elements = super(PAFWebElement, self).find_elements(by=by, value=value)
        paf_web_elements = []
        for web_element in web_elements:
            paf_web_element = PAFWebElement.create_instance_using_webelement(web_element)
            paf_web_element._parent_element = self
            paf_web_element._parent = self._parent_element.parent
            paf_web_element.by = by
            paf_web_element.locator = value
            paf_web_element.description = value
            paf_web_elements.append(paf_web_element)
        return paf_web_elements

    def wait_for_visible(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = 'Wait time out for ' + self.description + ' to be visible'
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForVisible((self.by, self.locator)), message
        )

    def wait_for_not_visible(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotVisible((self.by, self.locator))
        )

    def wait_for_disabled(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be disabled"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForDisabled((self.by, self.locator)), message
        )

    def wait_for_enabled(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be enabled"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForEnabled((self.by, self.locator)), message
        )

    def wait_for_present(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be present"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForPresent((self.by, self.locator)), message
        )

    def wait_for_not_present(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to not be present"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotPresent((self.by, self.locator)), message
        )

    def wait_for_text(self, text_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " text " + text_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForText((self.by, self.locator), text_), message
        )

    def wait_for_containing_text(self, text_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " containing text " + text_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForContainingText((self.by, self.locator), text_), message
        )

    def wait_for_not_text(self, text_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " text not " + text_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotText((self.by, self.locator), text_), message
        )

    def wait_for_not_containing_text(self, text_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " containing text not " + text_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotContainingText((self.by, self.locator), text_), message
        )

    def wait_for_value(self, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " value " + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForValue((self.by, self.locator), value_), message
        )

    def wait_for_not_value(self, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " value not " + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotValue((self.by, self.locator), value_), message
        )

    def wait_for_selected(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be selected"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForSelected((self.by, self.locator)), message
        )

    def wait_for_not_selected(self, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " not to be selected"
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotSelected((self.by, self.locator)), message
        )

    def wait_for_attribute(self, attr_, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " " + attr_ + " = " + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForAttribute((self.by, self.locator), attr_, value_), message
        )

    def wait_for_not_attribute(self, attr_, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " " + attr_ + " != " + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotAttribute((self.by, self.locator), attr_, value_), message
        )

    def wait_for_css_class(self, class_name_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have css class " + class_name_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForCssClass((self.by, self.locator), class_name_), message
        )

    def wait_for_not_css_class(self, class_name_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have not css class " + class_name_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotCssClass((self.by, self.locator), class_name_), message
        )

    def wait_for_css_style(self, style_name_, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have css style " + style_name_ + "=" + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForCssStyle((self.by, self.locator), style_name_, value_), message
        )

    def wait_for_not_css_style(self, style_name_, value_, wait_time=0):
        wait_time_out = ConfigurationsManager().get_int_for_key(ApplicationProperties.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have not css style " + style_name_ + "=" + value_
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForNotCssStyle((self.by, self.locator), style_name_, value_), message
        )

    def __ensure_present(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_present()
        except TimeoutException:
            outcome = False
            self.report("present", outcome, msg)
        return outcome

    def verify_present(self, msg=''):
        outcome = self.__ensure_present(msg)
        if outcome:
            msg = self.get_description(msg)
            self.report("present", outcome, msg)
        return outcome

    def verify_not_present(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_present()
            outcome = False
        except TimeoutException:
            outcome = True
        self.report("notpresent", outcome, msg)
        return outcome

    def verify_visible(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_visible()
        except TimeoutException:
            outcome = False
        self.report("visible", outcome, msg)
        return outcome

    def verify_not_visible(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_not_visible()
        except TimeoutException:
            outcome = False
        self.report("notvisible", outcome, msg)
        return outcome

    def verify_enabled(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_enabled()
        except TimeoutException:
            outcome = False
        self.report("enabled", outcome, msg)
        return outcome

    def verify_disabled(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_disabled()
        except TimeoutException:
            outcome = False
        self.report("disabled", outcome, msg)
        return outcome

    def verify_text(self, text_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("text", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_text_contain(self, text_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_containing_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("text", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_not_text(self, text_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("nottext", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_not_text_contains(self, text_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_containing_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("nottext", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_value(self, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_value(value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("value", outcome, msg, expected=value_, actual=actaul_)
        return outcome

    def verify_not_value(self, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_value(value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notvalue", outcome, msg, expected=value_, actual=actaul_)
        return outcome

    def verify_selected(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_selected()
        except TimeoutException:
            outcome = False
        self.report("selected", outcome, msg)
        return outcome

    def verify_not_selected(self, msg=''):
        outcome = True
        msg = self.get_description(msg)
        try:
            self.verify_not_selected()
        except TimeoutException:
            outcome = False
        self.report("notselected", outcome, msg)
        return outcome

    def verify_attribute(self, attr_, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_attribute(attr_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("attribute", outcome, msg, op=attr_, expected=value_, actual=actaul_)
        return outcome

    def verify_not_attribute(self, attr_, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_attribute(attr_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notattribute", outcome, msg, op=attr_, expected=value_, actual=actaul_)
        return outcome

    def verify_css_class(self, class_name_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_css_class(class_name_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("cssclass", outcome, msg, expected=class_name_, actual=actaul_)
        return outcome

    def verify_not_css_class(self, class_name_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_css_class(class_name_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notcssclass", outcome, msg, expected=class_name_, actual=actaul_)
        return outcome

    def verify_css_style(self, style_name_, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_css_style(style_name_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("cssstyle", outcome, msg, op=style_name_, expected=value_, actual=actaul_)
        return outcome

    def verify_not_css_style(self, style_name_, value_, msg=''):
        if not self.__ensure_present(msg):
            return False

        outcome = True
        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_css_style(style_name_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notcssstyle", outcome, msg, op=style_name_, expected=value_, actual=actaul_)
        return outcome

    def assert_present(self, msg=''):
        if not self.verify_present(msg):
            raise AssertionError

    def assert_not_present(self, msg=''):
        if not self.verify_not_present(msg):
            raise AssertionError

    def assert_visible(self, msg=''):
        if not self.verify_visible(msg):
            raise AssertionError

    def assert_not_visible(self, msg=''):
        if not self.verify_not_visible(msg):
            raise AssertionError

    def assert_enabled(self, msg=''):
        if not self.verify_enabled(msg):
            raise AssertionError

    def assert_disabled(self, msg=''):
        if not self.verify_disabled(msg):
            raise AssertionError

    def assert_text(self, text_, msg=''):
        if not self.verify_text(text_, msg):
            raise AssertionError

    def assert_text_contain(self, text_, msg=''):
        if not self.verify_text_contain(text_, msg):
            raise AssertionError

    def assert_not_text(self, text_, msg=''):
        if not self.verify_not_text(text_, msg):
            raise AssertionError

    def assert_not_text_contains(self, text_, msg=''):
        if not self.verify_not_text_contains(text_, msg):
            raise AssertionError

    def assert_value(self, value_, msg=''):
        if not self.verify_value(value_, msg):
            raise AssertionError

    def assert_not_value(self, value_, msg=''):
        if not self.verify_not_value(value_, msg):
            raise AssertionError

    def assert_selected(self, msg=''):
        if not self.verify_selected(msg):
            raise AssertionError

    def assert_not_selected(self, msg=''):
        if not self.verify_not_selected(msg):
            raise AssertionError

    def assert_attribute(self, attr_, value_, msg=''):
        if not self.verify_attribute(attr_, value_, msg):
            raise AssertionError

    def assert_not_attribute(self, attr_, value_, msg=''):
        if not self.verify_not_attribute(attr_, value_, msg):
            raise AssertionError

    def assert_css_class(self, class_name_, msg=''):
        if not self.verify_css_class(class_name_, msg):
            raise AssertionError

    def assert_not_css_class(self, class_name_, msg=''):
        if not self.verify_not_css_class(class_name_, msg):
            raise AssertionError

    def assert_css_style(self, style_name_, value_, msg=''):
        if not self.verify_css_style(style_name_, value_, msg):
            raise AssertionError

    def assert_not_css_style(self, style_name_, value_, msg=''):
        if not self.verify_not_css_style(style_name_, value_, msg):
            raise AssertionError

    def is_present(self):
        try:
            if self._id != -1 and self.cacheable:
                return True

            if self._parent_element is not None:
                if not self._parent_element.is_present():
                    return False
                else:
                    elements = self._parent_element.find_elements(by=self.by, value=self.locator)
            else:
                elements = self._parent.find_elements(by=self.by, value=self.locator)

            if elements is not None and len(elements) > 0:
                if self._id == -1:
                    self._id = elements[0].id
                return True
            else:
                return False
        except:
            return False

    def _execute(self, command, params=None):
        command_tracker = CommandTracker(command, params)

        if params is None:
            params = {}

        if self.id != -1:
            params['id'] = self.id
        else:
            driver_command = Command.FIND_ELEMENT
            parameters = {"using": self.by, "value": self.locator, "id": -1}
            element = self.parent.execute(driver_command, parameters)['value']
            self._id = element._id
            params['id'] = self.id

        command_tracker.parameters = params
        self.before_command(command_tracker)
        try:
            if command_tracker.response is None:
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response

            self.after_command(command_tracker)
        except Exception as e:
            command_tracker.exception = e
            self.on_exception(command_tracker)

        if command_tracker.has_exception():
            if command_tracker.retry:
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response
            else:
                raise command_tracker.exception

        return command_tracker.response

    @staticmethod
    def report(operation, outcome, msg, **kwargs):
        key = "element." + operation + "." + ("pass" if outcome else "fail")
        message_format = ConfigurationsManager().get_str_for_key(key)

        not_op_pass_format = "Expected {expected} not {operation} : " \
                             "Actual {actual} not {operation}"
        not_op_fail_format = "Expected {expected} not {operation} : " \
                             "Actual {actual} {operation}"
        op_pass_format = "Expected {expected} {operation} : " \
                         "Actual {actual} {operation}"
        op_fail_format = "Expected {expected} {operation} : " \
                         "Actual {actual} not {operation}"

        not_op_val_format = "Expected %(op)s {operation} should not be {expected} : " \
                            "Actual %(op)s {operation} is {actual}"
        op_val_format = "Expected %(op)s {operation} should be {expected} : " \
                        "Actual %(op)s {operation} is {actual}"

        if message_format is None:
            condition_1 = not_op_val_format if (kwargs is not None and len(
                kwargs) > 2) else (not_op_pass_format if outcome else not_op_fail_format)

            condition_2 = op_val_format if (kwargs is not None and len(kwargs) > 2) else (
                op_pass_format if outcome else op_fail_format)

            message_format = condition_1 if operation.startswith('not') else condition_2
            message_format = message_format.replace('{operation}', operation.replace('not', ''))

        message = message_format.format(expected=msg, actual=msg)

        if kwargs is not None and len(kwargs.keys()) > 0:
            message = message % kwargs
        else:
            message = message % {"expected":msg, "actual":msg}

        if outcome:
            Reporter.log(message, MessageType.Pass)
        else:
            Reporter.log(message, MessageType.Fail)

    def before_command(self, command_tracker):
        command_tracker.stage = Stage.executing_before_method
        if self._listeners is not None:
            for listener in self._listeners:
                listener.before_command(self, command_tracker)

    def after_command(self, command_tracker):
        command_tracker.stage = Stage.executing_after_method
        if self._listeners is not None:
            for listener in self._listeners:
                listener.after_command(self, command_tracker)

    def on_exception(self, command_tracker):
        command_tracker.stage = Stage.executing_on_failure

        if isinstance(command_tracker.get_exception_type(), StaleElementReferenceException):
            self._id = -1
            parameters = command_tracker.get_parameters()
            parameters['id'] = self.id
            command_tracker.set_exception(None)
            command_tracker.set_stage(Stage.executing_method)
            self._execute(command_tracker.get_command(), parameters)

        if self._listeners is not None:
            if command_tracker.has_exception():
                for listener in self._listeners:
                    listener.on_exception(self, command_tracker)

    def on_wait_new(self, command_tracker):
         return WebDriverWait(base_driver.BaseDriver().get_driver(), 30)