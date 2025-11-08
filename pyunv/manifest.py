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
        self.template = None
        
        if template:
            self.template = template
        else:
            # Try to find manifest.mako in the package directory
            try:
                # Get the directory of the current module
                module_path = os.path.dirname(__file__)
                template_path = os.path.join(module_path, 'manifest.mako')
                if os.path.exists(template_path):
                    self.template = template_path
                else:
                    # Fallback: assume manifest.mako is in current directory
                    self.template = 'manifest.mako'
            except Exception:
                # Fallback: assume manifest.mako is in current directory
                self.template = 'manifest.mako'

    def save(self, f):
        """docstring for write_manifest"""
        if self.template:
            try:
                template = Template(filename=self.template, 
                    encoding_errors='replace')
                f.write(template.render(universe=self.universe))
            except FileNotFoundError:
                raise RuntimeError("No template found at: " + self.template + 
                    ". Ensure manifest.mako is installed with the pyunv package.")
        else:
            raise RuntimeError("No template found for Manifest. " + 
                "Ensure manifest.mako is installed with the pyunv package.")


class ManifestTests(unittest.TestCase):
    
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
