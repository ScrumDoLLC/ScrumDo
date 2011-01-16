import unittest

import homepage
import account_tests

suite = unittest.TestSuite()
suite.addTest(homepage.HomepageTest("test_homepage"))
suite.addTest(account_tests.AccountTests("test_sign_up"))
suite.addTest(account_tests.AccountTests("test_login"))


unittest.TextTestRunner(verbosity=2).run(suite)
