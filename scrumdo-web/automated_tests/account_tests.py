#!/usr/bin/python
# -*- coding: latin-1 -*-


from selenium import selenium
import unittest, time, re
import time

class AccountTests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()

    def test_sign_up(self):
        sel = self.selenium
        sel.open("/")
        sel.click("link=Sign Up")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "selenium_user")
        sel.type("id_password1", "selenium_password")
        sel.type("id_password2", "selenium_password")
        sel.type("id_email", "selenium@scrumdo.com")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Successfully logged in as selenium_user"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Get Scrum Done with ScrumDo"))
        except AssertionError, e: self.verificationErrors.append(str(e))    
        
    def test_login(self):
        sel = self.selenium
        sel.open("/")
        sel.click("link=Login")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "selenium_user")
        sel.type("id_password", "selenium_password")
        sel.click("id_remember")
        sel.click(u"//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Successfully logged in"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
