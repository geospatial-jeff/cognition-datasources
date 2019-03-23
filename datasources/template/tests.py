from datasources import tests

from __TEMPLATENAME__ import __TEMPLATENAME__

class __TEMPLATENAME__TestCases(tests.BaseTestCases):

    def _setUp(self):

        self.datasource = __TEMPLATENAME__
        self.spatial = # geojson geometry here
        self.temporal = # (start_date, end_date) here