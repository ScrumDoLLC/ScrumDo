#!/usr/bin/python
# -*- coding: latin-1 -*-


from selenium import selenium
import unittest, time, re
import time

class NewsfeedTests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()

    def test_create_story(self):
        sel = self.selenium
        sel.open("/")
        sel.click("link=Login")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "selenium_user")
        sel.type("id_password", "selenium_password")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Test project from automated tests")
        sel.wait_for_page_to_load("30000")
        sel.type("id_summary", "Test story from automated tests")
        sel.click(u"//*[@id='add_button']")
        sel.do_command('waitForElementPresent', ("//*[@id='createdStories']/li", ))
        sel.click(u"link=selenium_user")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Test story from automated tests"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")        
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()

