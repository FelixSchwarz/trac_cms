# -*- coding: utf-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

from trac.web import HTTPNotFound
from trac_dev_platform.test import EnvironmentStub, TracTest
from trac_dev_platform.test.lib.pythonic_testcase import *

from trac_cms.web_ui import TracCMSModule


class PathTraversalTest(TracTest):

    def setUp(self):
        self.env = EnvironmentStub(default_data=True, enable=('trac_cms.*', 'trac.*'))
        self.env.upgrade()

        self.env.use_temp_directory()
        self._create_trac_ini()
        
    def tearDown(self):
        self.env.destroy_temp_directory()
    
    def _create_trac_ini(self):
        os.mkdir(os.path.join(self.env.path, 'conf'))
        config = self.env.config
        config.filename = os.path.join(self.env.path, 'conf', 'trac.ini')
        config.save()
    
    # --------------------------------------------------------------------------
    
    def test_prevents_path_traversal(self):
        req = self.get_request('/../../conf/trac.ini')
        self.assert_raises(HTTPNotFound, lambda: self.simulate_request(req))


