#!/usr/bin/env python
# encoding: utf-8
"""
test_reader.py

Created by David Peckham on 2009-09-20.
Copyright (c) 2009 David Peckham. All rights reserved.

Enhanced by Sanjay Sharma (indoos@gmail.com) 2025-10-17.
"""

import datetime
import os
import sys
import unittest

# Add the local pyunv directory to the path so tests use the enhanced version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyunv.universe import Universe
from pyunv.reader import Reader
from pyunv.manifest import Manifest


class ReaderTests(unittest.TestCase):
    
    def setUp(self):
        super(ReaderTests, self).setUp()
    
    def tearDown(self):
        super(ReaderTests, self).tearDown()
            
    def test_date_from_dateindex1(self):
        date = datetime.date(1976, 7, 4)
        self.assertEqual(Reader.date_from_dateindex(2442964), date)
        
    def test_date_from_dateindex2(self):
        date = datetime.date(1976, 7, 5)
        self.assertEqual(Reader.date_from_dateindex(2442965), date)
        
    def test_date_from_dateindex3(self):
        date = datetime.date(2009, 9, 15)
        self.assertEqual(Reader.date_from_dateindex(2455090), date)
        

class SampleUniverseXIR2(unittest.TestCase):
    
    def setUp(self):
        super(SampleUniverseXIR2, self).setUp()
        self.filename = 'tests/universes/universe_xir2.unv'
        self.reader = Reader(open(self.filename, 'rb'))
        self.universe = self.reader.universe
    
    def tearDown(self):
        super(SampleUniverseXIR2, self).tearDown()
        del self.reader

    # tests for universe parameters
    
    def test_universe_name(self):
        self.assertEqual(self.universe.parameters.universe_name, 
            'universe_xir2')
        
    def test_universe_filename(self):
        self.assertEqual(self.universe.parameters.universe_filename, 
            'universe_xir2')
        
    def test_revision(self):
        self.assertEqual(self.universe.parameters.revision, 0)
        
    def test_description(self):
        self.assertEqual(self.universe.parameters.description, 
            'This is the first sample universe for PyUnv tests.'
            ' It uses the pyunv_a database.')
        
    def test_created_by(self):
        self.assertEqual(self.universe.parameters.created_by, 'peckhda')
        
    def test_modified_by(self):
        self.assertEqual(self.universe.parameters.modified_by, 'peckhda')
        
    def test_created_date(self):
        self.assertEqual(self.universe.parameters.created_date, 
            datetime.date(2009, 9, 26))

    def test_modified_date(self):
        self.assertEqual(self.universe.parameters.modified_date, 
            datetime.date(2009, 9, 27))
        
    def test_query_time_limit(self):
        self.assertEqual(self.universe.parameters.query_time_limit, 37)
        
    def test_query_row_limit(self):
        self.assertEqual(self.universe.parameters.query_row_limit, 54321)
        
    def test_cost_estimate_warning_limit(self):
        self.assertEqual(
            self.universe.parameters.cost_estimate_warning_limit, 5)
        
    def test_object_strategy(self):
        self.assertEqual(self.universe.parameters.object_strategy, 
            '(Built-in) Standard Renaming')
        
    def test_long_text_limit(self):
        self.assertEqual(self.universe.parameters.long_text_limit, 1234)
        
    def test_cost_estimate_warning_limit(self):
        self.assertEqual(
            self.universe.parameters.cost_estimate_warning_limit, 5)
        
    def test_comments(self):
        self.assertEqual(self.universe.parameters.comments, 
            'These are comments for the universe_xir2 universe.')
        
    def test_domain(self):
        self.assertEqual(self.universe.parameters.domain, None)

    def test_dbms_engine(self):
        self.assertEqual(self.universe.parameters.dbms_engine, 
            'Generic ODBC3 datasource')

    def test_network_layer(self):
        self.assertEqual(self.universe.parameters.network_layer, 'ODBC')

    # tests for reading universe objects
    
    def test_class_count(self):
        self.assertEqual(self.universe.statistics['classes'], 7)
            
    def test_object_count(self):
        self.assertEqual(self.universe.statistics['objects'], 33)
            
    def test_table_count(self):
        self.assertEqual(self.universe.statistics['tables'], 8)
            
    def test_alias_count(self):
        self.assertEqual(self.universe.statistics['aliases'], 3)
            
    def test_join_count(self):
        self.assertEqual(self.universe.statistics['joins'], 7)
            
    def test_context_count(self):
        self.assertEqual(self.universe.statistics['contexts'], 2)
            
    def test_condition_count(self):
        self.assertEqual(self.universe.statistics['conditions'], 6)

    def test_custom_parameters(self):
        self.assertEqual(self.universe.custom_parameters['SAMPLE_PARAMETER1'], '999333')
        self.assertEqual(self.universe.custom_parameters['OLAP_UNIVERSE'], 'No')
        self.assertEqual(self.universe.custom_parameters['ANSI92'], 'YES')
        self.assertEqual(self.universe.custom_parameters['SAMPLE_PARAMETER2'], '999222')
            
    def test_manifest(self):
        Manifest(self.universe).save(open(self.filename+'.txt', 'w'))
        

class SampleUniverseEFashion(unittest.TestCase):
    
    def setUp(self):
        super(SampleUniverseEFashion, self).setUp()
        self.filename = 'tests/universes/eFashion.unv'
        self.reader = Reader(open(self.filename, 'rb'))
        self.universe = self.reader.universe
    
    def tearDown(self):
        super(SampleUniverseEFashion, self).tearDown()
        del self.reader

    # tests for universe parameters
    
    def test_universe_name(self):
        self.assertEqual(self.universe.parameters.universe_name, 'eFashion')
        
    def test_universe_filename(self):
        self.assertEqual(self.universe.parameters.universe_filename, 'eFashion')
        
    def test_class_count(self):
        self.assertEqual(self.universe.statistics['classes'], 6)
            
    def test_object_count(self):
        self.assertEqual(self.universe.statistics['objects'], 41)
            
    def test_table_count(self):
        self.assertEqual(self.universe.statistics['tables'], 4)
            
    def test_validation_errors_count(self):
        self.assertEqual(len(self.universe.validation_errors), 40)
            
    def test_cross_references_count(self):
        self.assertEqual(len(self.universe.cross_references), 29)
            
    def test_manifest(self):
        Manifest(self.universe).save(open(self.filename+'.txt', 'w'))


class SampleUniverseUnivers5(unittest.TestCase):
    
    def setUp(self):
        super(SampleUniverseUnivers5, self).setUp()
        self.filename = 'tests/universes/Univers5.unv'
        self.reader = Reader(open(self.filename, 'rb'))
        self.universe = self.reader.universe
    
    def tearDown(self):
        super(SampleUniverseUnivers5, self).tearDown()
        del self.reader

    # tests for universe parameters
    
    def test_universe_name(self):
        self.assertEqual(self.universe.parameters.universe_name, 'Univers5')
        
    def test_universe_filename(self):
        self.assertEqual(self.universe.parameters.universe_filename, 'Univers5')
        
    def test_class_count(self):
        self.assertEqual(self.universe.statistics['classes'], 1)
            
    def test_object_count(self):
        self.assertEqual(self.universe.statistics['objects'], 5)
            
    def test_table_count(self):
        self.assertEqual(self.universe.statistics['tables'], 1)
            
    def test_validation_errors_count(self):
        self.assertEqual(len(self.universe.validation_errors), 0)
            
    def test_cross_references_count(self):
        self.assertEqual(len(self.universe.cross_references), 5)
            
    def test_manifest(self):
        Manifest(self.universe).save(open(self.filename+'.txt', 'w'))
        

if __name__ == '__main__':
    unittest.main()


# Additional test class for enhanced analysis features
class EnhancedAnalysisTests(unittest.TestCase):
    """Test enhanced analysis features with Univers5"""
    
    def setUp(self):
        super(EnhancedAnalysisTests, self).setUp()
        self.filename = 'tests/universes/Univers5.unv'
        self.reader = Reader(open(self.filename, 'rb'))
        self.universe = self.reader.universe
    
    def tearDown(self):
        super(EnhancedAnalysisTests, self).tearDown()
        del self.reader

    # Database Tables Tests
    
    def test_database_tables_extraction(self):
        """Test that database tables are extracted during enhanced analysis"""
        self.assertGreater(len(self.universe.database_tables), 0, 
                          "Database tables should be extracted")
    
    def test_database_tables_have_required_fields(self):
        """Test that database tables contain required metadata"""
        if self.universe.database_tables:
            for table_id, table_info in self.universe.database_tables.items():
                self.assertIn('id', table_info)
                self.assertIn('name', table_info)
                self.assertIn('column_count', table_info)
                self.assertIn('used_in_objects', table_info)
                self.assertIn('used_in_joins', table_info)
    
    # Table Columns Tests
    
    def test_table_columns_extraction(self):
        """Test that table columns are extracted"""
        if self.universe.database_tables:
            self.assertGreater(len(self.universe.table_columns), 0,
                             "Table columns should be extracted if tables exist")
    
    def test_table_columns_have_required_fields(self):
        """Test that table columns contain required metadata"""
        if self.universe.table_columns:
            for table_id, columns in self.universe.table_columns.items():
                self.assertIsInstance(columns, list)
                for column in columns:
                    self.assertIn('id', column)
                    self.assertIn('name', column)
                    self.assertIn('table_id', column)
                    self.assertIn('fullname', column)
    
    # Join Details Tests
    
    def test_join_details_structure(self):
        """Test that join details structure exists"""
        self.assertIsNotNone(self.universe.join_details)
        self.assertIsInstance(self.universe.join_details, dict)
    
    def test_join_details_have_required_fields(self):
        """Test that join details contain required fields"""
        if self.universe.join_details:
            for join_id, join_info in self.universe.join_details.items():
                self.assertIn('id', join_info)
                self.assertIn('statement', join_info)
                self.assertIn('expression', join_info)
                self.assertIn('tables_involved', join_info)
    
    # Context Details Tests
    
    def test_context_details_structure(self):
        """Test that context details structure exists"""
        self.assertIsNotNone(self.universe.context_details)
        self.assertIsInstance(self.universe.context_details, dict)
    
    def test_context_details_have_required_fields(self):
        """Test that context details contain required fields"""
        if self.universe.context_details:
            for ctx_id, ctx_info in self.universe.context_details.items():
                self.assertIn('id', ctx_info)
                self.assertIn('name', ctx_info)
                self.assertIn('joins', ctx_info)
                self.assertIn('tables_involved', ctx_info)
    
    # Context Incompatibilities Tests
    
    def test_context_incompatibilities_structure(self):
        """Test that context incompatibilities structure exists"""
        self.assertIsNotNone(self.universe.context_incompatibilities)
        self.assertIsInstance(self.universe.context_incompatibilities, list)
    
    # LOV Definitions Tests
    
    def test_lov_definitions_structure(self):
        """Test that LOV definitions structure exists"""
        self.assertIsNotNone(self.universe.lov_definitions)
        self.assertIsInstance(self.universe.lov_definitions, dict)
    
    # Stored Procedure Parameters Tests
    
    def test_stored_procedure_parameters_structure(self):
        """Test that stored procedure parameters structure exists"""
        self.assertIsNotNone(self.universe.stored_procedure_parameters)
        self.assertIsInstance(self.universe.stored_procedure_parameters, dict)
    
    def test_stored_procedure_parameters_correct_format(self):
        """Test stored procedure parameters have correct format"""
        if self.universe.stored_procedure_parameters:
            for proc_name, parameters in self.universe.stored_procedure_parameters.items():
                self.assertIsInstance(proc_name, str, "Procedure name should be string")
                self.assertIsInstance(parameters, list, "Parameters should be list")
                for param in parameters:
                    self.assertIn('name', param, "Parameter should have 'name'")
                    self.assertIn('type', param, "Parameter should have 'type'")
                    self.assertIn('value', param, "Parameter should have 'value'")
    
    def test_stored_procedure_parameters_found(self):
        """Test that stored procedure parameters are found in Univers5"""
        # Univers5 should have the GetEmployeesByDeptAndSalary stored procedure
        self.assertGreater(len(self.universe.stored_procedure_parameters), 0,
                         "Univers5 should have stored procedure parameters")
    
    # General Enhanced Analysis Tests
    
    def test_all_enhanced_analysis_structures_exist(self):
        """Test that all enhanced analysis data structures exist"""
        self.assertTrue(hasattr(self.universe, 'database_tables'))
        self.assertTrue(hasattr(self.universe, 'table_columns'))
        self.assertTrue(hasattr(self.universe, 'join_details'))
        self.assertTrue(hasattr(self.universe, 'context_details'))
        self.assertTrue(hasattr(self.universe, 'context_incompatibilities'))
        self.assertTrue(hasattr(self.universe, 'lov_definitions'))
        self.assertTrue(hasattr(self.universe, 'stored_procedure_parameters'))

