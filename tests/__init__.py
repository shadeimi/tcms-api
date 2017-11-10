import random

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import tcms_api

from tcms.tests.factories import UserFactory
from tcms.core.contrib.auth.backends import initiate_user_with_default_setups


class BaseAPIClient_TestCase(StaticLiveServerTestCase):
    """
        Bring up a local Django instance and
        prepare test data - create Test Cases, Test Plans and Test Runs
    """

    # how many test objects to create
    num_cases = 1
    num_plans = 1
    num_runs = 1

    @classmethod
    def setUpClass(cls):
        super(StaticLiveServerTestCase, cls).setUpClass()

        # NB: for now these need to be the same as in ~/.tcms.conf
        cls.api_user = UserFactory(username='api-tester')
        cls.api_user.set_password('testing')
        initiate_user_with_default_setups(cls.api_user)

        cls.product = tcms_api.Product(name="Kiwi TCMS")
        cls.version = tcms_api.Version(product=cls.product, version="unspecified")
        cls.plantype = tcms_api.PlanType(name="Function")
        cls.category = tcms_api.Category(category="Regression", product=cls.product)
        cls.component = tcms_api.Component(name='tcms_api', product=cls.product)
        cls.CASESTATUS = tcms_api.CaseStatus("CONFIRMED")
        cls.build = tcms_api.Build(product=cls.product, build="unspecified")

        cls.tags = [tcms_api.Tag(id) for id in range(3000, 3200)]
        cls.TESTERS = [tcms_api.User(id) for id in range(1000, 1050)]

        # Create test cases
        cls.cases = []
        for case_count in range(cls.num_cases):
            testcase = tcms_api.TestCase(
                name="Test Case {0}".format(case_count + 1),
                category=cls.category,
                product=cls.product,
                summary="Test Case {0}".format(case_count + 1),
                status=cls.CASESTATUS)
            # Add a couple of random tags and the default tester
            testcase.tags.add([random.choice(cls.tags) for counter in range(10)])
            testcase.tester = random.choice(cls.TESTERS)
            testcase.update()
            cls.cases.append(testcase)

        # Create master test plan (parent of all)
        cls.master = tcms_api.TestPlan(
            name="API client Test Plan",
            product=cls.product,
            version=cls.version,
            type=cls.plantype)
        tcms_api.info("* {0}".format(cls.master))
        cls.master.testcases.add(cls.cases)
        cls.master.update()

        # Create child test plans
        cls.testruns = []
        for plan_count in range(cls.num_plans):
            testplan = tcms_api.TestPlan(
                name="Test Plan {0}".format(plan_count + 1),
                product=cls.product,
                version=cls.version,
                parent=cls.master,
                type=cls.plantype)
            # Link all test cases to the test plan
            testplan.testcases.add(cls.cases)
            testplan.update()
            tcms_api.info("  * {0}".format(testplan))

            # Create test runs
            for run_count in range(cls.num_runs):
                testrun = tcms_api.TestRun(
                    testplan=testplan,
                    build=cls.build,
                    product=cls.product,
                    summary="Test Run {0}".format(run_count + 1),
                    version=cls.version)
                tcms_api.info("    * {0}".format(testrun))
                cls.testruns.append(testrun)
