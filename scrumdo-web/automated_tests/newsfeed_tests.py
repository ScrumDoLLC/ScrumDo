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

    def test_newsfeed_activity_create(self):
        sel = self.selenium
        sel.open("/")
        sel.click("link=Sign Up")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "selenium_user2")
        sel.type("id_password1", "selenium_password")
        sel.type("id_password2", "selenium_password")
        sel.type("id_email", "test@dbp.mm.st")
        sel.click(u"//input[@value='Sign Up »']")
        sel.wait_for_page_to_load("30000")
        sel.click("//div[@id='body']/div[2]/a[1]/h2")
        sel.wait_for_page_to_load("30000")
        sel.type("id_slug", "selenium_test_projec")
        sel.type("id_name", "Selenium Test Project")
        sel.type("id_description", "Selenium Test Project Description.")
        sel.click("//button[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.type("id_recipient", "selenium_user")
        sel.click("//button[@type='submit']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("selenium_user"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_summary", "Test story to see if newsfeed is working.")
        sel.click("add_button")
        sel.click("link=selenium_user2")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("created Test story to see if newsfeed is working"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Login")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "selenium_user")
        sel.type("id_password", "selenium_password")
        sel.click(u"//input[@value='Log in »']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("created Test story to see if newsfeed is working"))
        except AssertionError, e: self.verificationErrors.append(str(e))


    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
