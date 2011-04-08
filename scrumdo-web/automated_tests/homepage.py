from selenium import selenium
import unittest, time, re


class HomepageTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()

    def test_homepage(self):
        sel = self.selenium
        sel.open("/")
        try: self.failUnless(sel.is_text_present("Get Scrum Done with ScrumDo"))
        except AssertionError, e: self.verificationErrors.append(str(e))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
