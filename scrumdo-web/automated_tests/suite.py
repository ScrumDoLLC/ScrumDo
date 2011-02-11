import unittest

import homepage
import account_tests
import newsfeed_tests

suite = unittest.TestSuite()
suite.addTest(homepage.HomepageTest("test_homepage"))
suite.addTest(account_tests.AccountTests("test_sign_up"))
suite.addTest(account_tests.AccountTests("test_login"))
suite.addTest(account_tests.AccountTests("test_organization_create"))
suite.addTest(newsfeed_tests.NewsfeedTests("test_create_story"))
suite.addTest(newsfeed_tests.NewsfeedTests("test_newsfeed_activity_create"))

unittest.TextTestRunner(verbosity=2).run(suite)
