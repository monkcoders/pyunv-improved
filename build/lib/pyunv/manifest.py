#!/usr/bin/env python
# encoding: utf-8
"""
manifest.py

Created by David Peckham on 2009-09-09.
Copyright (c) 2009 David Peckham. All rights reserved.

Enhanced by Sanjay Sharma (indoos@gmail.com) 2025-10-17.
"""

import sys
import os
import unittest

from mako.template import Template


class Manifest:
    
    def __init__(self, universe, template=None):
        self.universe = universe
        if template:
            self.template = template
        else:
            self.template = 'manifest.mako'

    def save(self, f):
        """docstring for write_manifest"""
        template = Template(filename=self.template, 
            encoding_errors='replace')
        f.write(template.render(universe=self.universe))


class ManifestTests(unittest.TestCase):
    
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
