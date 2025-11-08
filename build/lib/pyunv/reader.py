#!/usr/bin/env python
# encoding: utf-8
"""
reader.py

Created by David Peckham on 2009-09-07.
Copyright (c) 2009 David Peckham. All rights reserved.

Enhanced by Sanjay Sharma (indoos@gmail.com) 2025-10-17.
"""

import datetime
import os
import pdb
import re
import struct
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '..')
from pyunv.universe import Universe, Parameters, Class, Join, Object
from pyunv.universe import Condition, Table, VirtualTable, Column, Context, Link, Hierarchy

# import pyunv

class Reader(object):
    
    _content_markers = ('Objects;', 'Tables;', 'Columns;', 'Contexts;',
        'Virtual Tables;', 'Parameters;', 'Columns Id;', 'Joins;',
        'Links;', 'Hierarchies;', 'Parameters_6_0;', 'Parameters_4_1;',
        'Parameters_5_0;', 'Parameters_11_5;', 'Object_Formats;',
        'Object_ExtraFormats;', 'Dynamic_Class_Descriptions;',
        'Dynamic_Object_Descriptions;', 'Dynamic_Property_Descriptions;',
        'Audit;', 'Dimensions;', 'OLAPInfo;', 'Graphical_Info;',
        'Crystal_References;', 'XML-LOV;', 'Integrity;',
        'AggregateNavigation;', 'BoundedColumns;', 'BuildOrigin_v6;',
        'CompulsaryType;', 'Deleted References;', 'DELETED_HISTORY;',
        'Dot_Tables;', 'Downward;', 'FormatLocaleSort;', 'FormatVersion;',
        'Joins Extensions;', 'Key References;', 'KernelPageFormat;',
        'Platform;', 'UNICODE ON;', 'Upward;', 'Upward_LocalIndexing;',
        'Upward_Mapping;', 'Upward_Override;', 'Upward_Override_New;',
        'WindowsPageFormat;')
    
    def __init__(self, f):
        super(Reader, self).__init__()
        self.file = f
        self.find_content_offsets()
        self.universe = Universe()
        self.universe.parameters = self.read_parameters()
        self.universe.custom_parameters = self.read_customparameters()
        self.universe.tables = self.read_tables()
        self.universe.build_table_map()
        self.universe.virtual_tables = self.read_virtual_tables()
        self.universe.columns = self.read_columns()
        self.universe.columns.sort(key=lambda c: c.id_)
        #self.universe.column_attributes = self.read_column_attributes()
        self.universe.joins = self.read_joins()
        self.universe.contexts = self.read_contexts()
        self.universe.links = self.read_links()
        try:
            self.universe.hierarchies = self.read_hierarchies()
        except:
            self.universe.hierarchies = []
        # Read additional parameter versions
        try:
            self.universe.parameters_4_1 = self.read_parameters_4_1()
        except:
            self.universe.parameters_4_1 = None
        try:
            self.universe.parameters_5_0 = self.read_parameters_5_0()
        except:
            self.universe.parameters_5_0 = None
        try:
            self.universe.parameters_11_5 = self.read_parameters_11_5()
        except:
            self.universe.parameters_11_5 = None
        # Read formatting information
        try:
            self.universe.object_formats = self.read_object_formats()
        except:
            self.universe.object_formats = []
        try:
            self.universe.object_extra_formats = self.read_object_extra_formats()
        except:
            self.universe.object_extra_formats = []
        # Read dynamic descriptions
        try:
            self.universe.dynamic_class_descriptions = self.read_dynamic_class_descriptions()
        except:
            self.universe.dynamic_class_descriptions = {}
        try:
            self.universe.dynamic_object_descriptions = self.read_dynamic_object_descriptions()
        except:
            self.universe.dynamic_object_descriptions = {}
        try:
            self.universe.dynamic_property_descriptions = self.read_dynamic_property_descriptions()
        except:
            self.universe.dynamic_property_descriptions = {}
        # Read audit and metadata
        try:
            self.universe.audit_info = self.read_audit_info()
        except:
            self.universe.audit_info = None
        try:
            self.universe.dimensions = self.read_dimensions()
        except:
            self.universe.dimensions = []
        try:
            self.universe.olap_info = self.read_olap_info()
        except:
            self.universe.olap_info = None
        try:
            self.universe.graphical_info = self.read_graphical_info()
        except:
            self.universe.graphical_info = None
        try:
            self.universe.crystal_references = self.read_crystal_references()
        except:
            self.universe.crystal_references = []
        try:
            self.universe.xml_lov = self.read_xml_lov()
        except:
            self.universe.xml_lov = None
        try:
            self.universe.integrity_rules = self.read_integrity_rules()
        except:
            self.universe.integrity_rules = []
        # Read additional metadata sections
        try:
            self.universe.aggregate_navigation = self.read_aggregate_navigation()
        except:
            self.universe.aggregate_navigation = None
        try:
            self.universe.bounded_columns = self.read_bounded_columns()
        except:
            self.universe.bounded_columns = []
        try:
            self.universe.build_origin_v6 = self.read_build_origin_v6()
        except:
            self.universe.build_origin_v6 = None
        try:
            self.universe.compulsary_type = self.read_compulsary_type()
        except:
            self.universe.compulsary_type = None
        try:
            self.universe.deleted_references = self.read_deleted_references()
        except:
            self.universe.deleted_references = []
        try:
            self.universe.deleted_history = self.read_deleted_history()
        except:
            self.universe.deleted_history = []
        try:
            self.universe.dot_tables = self.read_dot_tables()
        except:
            self.universe.dot_tables = []
        try:
            self.universe.downward = self.read_downward()
        except:
            self.universe.downward = None
        try:
            self.universe.format_locale_sort = self.read_format_locale_sort()
        except:
            self.universe.format_locale_sort = None
        try:
            self.universe.format_version = self.read_format_version()
        except:
            self.universe.format_version = None
        try:
            self.universe.joins_extensions = self.read_joins_extensions()
        except:
            self.universe.joins_extensions = []
        try:
            self.universe.key_references = self.read_key_references()
        except:
            self.universe.key_references = []
        try:
            self.universe.kernel_page_format = self.read_kernel_page_format()
        except:
            self.universe.kernel_page_format = None
        try:
            self.universe.platform = self.read_platform()
        except:
            self.universe.platform = None
        try:
            self.universe.unicode_on = self.read_unicode_on()
        except:
            self.universe.unicode_on = None
        try:
            self.universe.upward = self.read_upward()
        except:
            self.universe.upward = None
        try:
            self.universe.upward_local_indexing = self.read_upward_local_indexing()
        except:
            self.universe.upward_local_indexing = None
        try:
            self.universe.upward_mapping = self.read_upward_mapping()
        except:
            self.universe.upward_mapping = None
        try:
            self.universe.upward_override = self.read_upward_override()
        except:
            self.universe.upward_override = None
        try:
            self.universe.upward_override_new = self.read_upward_override_new()
        except:
            self.universe.upward_override_new = None
        try:
            self.universe.windows_page_format = self.read_windows_page_format()
        except:
            self.universe.windows_page_format = None
        self.universe.classes = self.read_classes()
        self.universe.build_object_map()

        # Perform additional analysis
        self.parse_unw_storage_data()
        self.parse_resource_header_data()
        self.perform_cross_reference_analysis()
        self.perform_validation_checks()
        self.perform_dependency_analysis()
        self.perform_enhanced_analysis()

    def find_content_offsets(self):
        """find the offsets of the object, table, and column definitions 
        in the BusinessObjects universe file.
        
        In some universe files, the markers appear more than once. In most
        cases, the first occurence is the right one. One exception is when
        the marker recurs almost immediately -- in this case we need to skip
        over the false marker and search the rest of the file.
        """
        
        self.content_offsets = dict()
        contents = self.file.read()
        for marker in Reader._content_markers:
            marker_bytes = b'\x00' + marker.encode('utf-8')
            begin = contents.find(marker_bytes)
            end = begin + len(marker_bytes)
            if contents.find(marker.encode('utf-8'), begin-20, begin) != -1 or \
                    contents.find(marker.encode('utf-8'), end, end+20) != -1:
                begin = contents.find(marker_bytes, end+20)
                end = begin + len(marker_bytes)
            self.content_offsets[marker] = end
        del contents
        return
    
    def read_parameters(self):
        """docstring for read_parameters
        
        I unknown (usually 0x22)
        I unknown
        S universe_filename
        S universe_name
        I revision
        H unknown
        S description
        S created_by
        S modified_by
        I created_date
        I modified_date
        I query_time_limit (seconds)
        I query_row_limit
        S unknown
        S object_strategy
        x unknown
        I cost_estimate_warning_limit (seconds)
        I long_text_limit (characters)
        4x unknown
        S comments
        3I unknown
        S domain
        S dbms_engine
        S network_layer
        
         Other parameter blocks we don't parse yet:
            Parameters_4_1;
            Parameters_5_0;
            Parameters_6_0;
            Parameters_11_5;
        
        """
        self.file.seek(self.content_offsets['Parameters;'])
        params = Parameters()
        struct.unpack('<2I', self.file.read(8))
        params.universe_filename = self.read_string()
        params.universe_name = self.read_string()
        params.revision, = struct.unpack('<I', self.file.read(4))
        struct.unpack('<H', self.file.read(2))
        params.description = self.read_string()
        params.created_by = self.read_string()
        params.modified_by = self.read_string()
        created, modified, = struct.unpack('<2I', self.file.read(8))
        params.created_date = Reader.date_from_dateindex(created)
        params.modified_date = Reader.date_from_dateindex(modified)
        seconds, = struct.unpack('<I', self.file.read(4))
        params.query_time_limit = seconds / 60
        params.query_row_limit, = struct.unpack('<I', self.file.read(4))
        self.read_string()
        params.object_strategy = self.read_string()
        struct.unpack('<x', self.file.read(1))
        seconds, = struct.unpack('<I', self.file.read(4))
        params.cost_estimate_warning_limit = seconds / 60
        params.long_text_limit, = struct.unpack('<I', self.file.read(4))
        struct.unpack('<4x', self.file.read(4))
        params.comments = self.read_string()
        struct.unpack('<3I', self.file.read(12))
        params.domain = self.read_string()
        params.dbms_engine = self.read_string()
        params.network_layer = self.read_string()
        return params
    
    def read_customparameters(self):
        """read the parameters defined on the Parameter tab of the 
        Designer Parameters dialog
        
        I count
        array of parameters:
            S universe_filename
            S universe_name
        
         Other parameter blocks we don't parse yet:
            Parameters_4_1;
            Parameters_5_0;
            Parameters_11_5;
        
        """
        self.file.seek(self.content_offsets['Parameters_6_0;'])
        params = dict()
        count, = struct.unpack('<I', self.file.read(4))
        for p in range(count):
            name = self.read_string()
            value = self.read_string()
            params[name] = value
        return params

    def read_tables(self):
        """read a BusinessObjects schema definition from the universe file

        B unknown (usually 0x1)
        B unknown (usually 0x1 or 0x2)
        S database_username?
        S schema_name
        I max_table_id
        I table_count
        ???B tables

        """
        self.file.seek(self.content_offsets['Tables;'])
        # pdb.set_trace()
        self.file.read(2)
        user_name = self.read_string()
        schema = self.read_string()
        max_table_id, = struct.unpack('<I', self.file.read(4))
        table_count, = struct.unpack('<I', self.file.read(4))
        return [self.read_table(schema) for x in range(table_count)]

    def read_virtual_tables(self):
        """read the virtual table definitions from the universe file

        I virtual_table_count
        ???B virtual_tables

        """
        self.file.seek(self.content_offsets['Virtual Tables;'])
        count, = struct.unpack('<I', self.file.read(4))
        return [self.read_virtualtable() for x in range(count)]

    def read_columns(self):
        """read the list of source database columns from the universe file

        I column_count
        I column_count?
        ???B columns

        """
        self.file.seek(self.content_offsets['Columns Id;'])
        column_count, = struct.unpack('<I', self.file.read(4))
        column_count2, = struct.unpack('<I', self.file.read(4))
        #print('count1 %d  count2 %d' % (column_count, column_count2))
        return [self.read_column() for x in range(column_count2)]
    
    def read_column_attributes(self):
        """read the column attributes (after marker Columns;)"""
        pass

    def read_joins(self):
        """docstring for read_joins
        
        I table_count?
        I unknown
        I join_count
        [...joins...]
        I unknown

        """
        self.file.seek(self.content_offsets['Joins;'])
        self.file.read(8)
        join_count, = struct.unpack('<I', self.file.read(4))
        joins = [self.read_join() for x in range(join_count)]
        self.file.read(8)
        return joins

    def read_contexts(self):
        """docstring for read_contexts
        
        I max_context_id?
        I context_count
        contexts...

        """
        self.file.seek(self.content_offsets['Contexts;'])
        # pdb.set_trace()
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        contexts = [self.read_context() for x in range(count)]
        return contexts

    def read_links(self):
        """docstring for read_links
        
        I max_link_id?
        I link_count
        links...

        """
        self.file.seek(self.content_offsets['Links;'])
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        links = [self.read_link() for x in range(count)]
        return links

    def read_hierarchies(self):
        """docstring for read_hierarchies
        
        I max_hierarchy_id?
        I hierarchy_count
        hierarchies...

        """
        self.file.seek(self.content_offsets['Hierarchies;'])
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        hierarchies = [self.read_hierarchy() for x in range(count)]
        return hierarchies

    def read_classes(self):
        """docstring for read_classes"""
        self.file.seek(self.content_offsets['Objects;'])
        class_count, object_count, condition_count, rootclass_count, = \
            struct.unpack('<4I', self.file.read(16))
        return [self.read_class(None) for x in range(rootclass_count)]
        
    def read_table(self, schema):
        """read a table definition from the universe file

        I table_id
        7x
        3I unknown
        S table_name
        I parent_id
        9x
        ? flag
            H count
            xxI unknown (count times)
        
        """
        id_, = struct.unpack('<I', self.file.read(4))
        self.file.read(19)
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        self.file.read(9)
        flag, = struct.unpack('<?', self.file.read(1))
        if flag:
            count, = struct.unpack('<H', self.file.read(2))
            self.file.read(4*count+3)
        else:
            self.file.read(1)
        return Table(self.universe, id_, parent_id, name, schema)

    def read_virtualtable(self):
        """read a virtual table definition from the universe file

        I table_id
        S select
        
        """
        table_id, = struct.unpack('<I', self.file.read(4))
        select = self.read_string()
        return VirtualTable(self.universe, table_id, select)

    def read_column(self):
        """read a column definition from the universe file

        I column_id
        I table_id
        S table_name
        
        """
        id_, = struct.unpack('<I', self.file.read(4))
        table_id, = struct.unpack('<I', self.file.read(4))
        parent = self.universe.table_map.get(table_id, None)  # Use get() to handle missing tables
        name = self.read_string()
        #print(name)
        return Column(id_, name, parent, self.universe)

    def read_class(self, parent):
        """read a BusinessObjects class definition from the universe file

        I subclass_count
        I id
        S name
        I parent_id
        S description
        7B unknown
        I object_count
        ???B objects
        I condition_count
        ???B conditions
        ???B subclasses

        """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        c = Class(self.universe, id_, parent, name, description)
        self.file.seek(7, os.SEEK_CUR)
        object_count, = struct.unpack('<I', self.file.read(4))
        c.objects = [self.read_object(c) for x in range(object_count)]
        condition_count, = struct.unpack('<I', self.file.read(4))
        c.conditions = [self.read_condition(c) for x in range(condition_count)]
        subclass_count, = struct.unpack('<I', self.file.read(4))
        c.subclasses = [self.read_class(c) for x in range(subclass_count)]
        return c

    def read_object(self, parent):
        """read a BusinessObjects object definition from the universe file

        I id
        S name
        I parent_id
        S description
        H select_table_count
        ?I select_table_ids (repeats select_table_count times)
        H where_table_count
        ?I where_table_ids (repeats where_table_count times)
        S select (starts 03 nn* 2E)
        S where (starts 02 nn* 20)
        S format
        S unknown
        S lov_name
        2x unknown
        x visibility (show=0x36, hidden=0x76)
        55B unknown  (LOV settings, hide indicator?)

       """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        o = Object(self.universe, id_, parent, name, description)
        select_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % select_tablecount, 
            self.file.read(4 * select_tablecount))
        where_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % where_tablecount, 
            self.file.read(4 * where_tablecount))
        o.select = self.read_string()
        o.where = self.read_string()
        o.format = self.read_string()
        unknown2 = self.read_string()
        o.lov_name = self.read_string()
        self.file.seek(2, os.SEEK_CUR)
        visibility, = struct.unpack('<B', self.file.read(1))
        o.visible = visibility != 0x36
        self.file.seek(55, os.SEEK_CUR)
        return o

    def read_condition(self, parent):
        """read a BusinessObjects condition definition from 
        the universe file

        I id
        S name
        I parent_id
        S description
        H where_tablecount
        ?I where_table_ids (repeats where_tablecount times)
        H unknown_tablecount
        ?I table_ids (repeats unknown_tablecount times)
        S where

        """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        c = Condition(self.universe, id_, parent, name, description)
        where_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % where_tablecount, 
            self.file.read(4 * where_tablecount))
        unknown_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % unknown_tablecount, 
            self.file.read(4 * unknown_tablecount))
        c.where = self.read_string()
        return c

    def read_join(self):
        """read a BusinessObjects join definition from the universe file

        I join_id
        5I unknown
        S join_conditions
        2I unknown
        I term_count
        [repeats term_count times]
            S term
            I term_table_id

        """
        join_id, = struct.unpack('<I', self.file.read(4))
        self.file.read(20)
        j = Join(self.universe, join_id)
        j.expression = self.read_string()
        self.file.read(8)
        j.term_count, = struct.unpack('<I', self.file.read(4))
        j.terms = []
        for i in range(j.term_count):
            term_name = self.read_string()
            term_parent_id, = struct.unpack('<I', self.file.read(4)) 
            j.terms.append((term_name, term_parent_id))
        return j

    def read_context(self):
        """read a BusinessObjects context definition from the universe file

        S name
        I id
        S description
        I join_count
        [repeats join_count times]
            join_id

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        c = Context(self.universe, id_, name, description)
        join_count, = struct.unpack('<I', self.file.read(4))
        for i in range(join_count):
            join_id, = struct.unpack('<I', self.file.read(4))
            c.joins.append(join_id)
        return c

    def read_link(self):
        """read a BusinessObjects link definition from the universe file

        S name
        I id
        S description
        S linked_universe

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        linked_universe = self.read_string()
        l = Link(self.universe, id_, name, description, linked_universe)
        return l

    def read_hierarchy(self):
        """read a BusinessObjects hierarchy definition from the universe file

        S name
        I id
        S description
        I level_count
        [repeats level_count times]
            I level_object_id

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        h = Hierarchy(self.universe, id_, name, description)
        level_count, = struct.unpack('<I', self.file.read(4))
        for i in range(level_count):
            level_id, = struct.unpack('<I', self.file.read(4))
            h.levels.append(level_id)
        return h

    def read_string(self):
        """read a variable-length string from the universe file"""
        length, = struct.unpack('<H', self.file.read(2))
        if length:
            s, = struct.unpack('<%ds' % length, self.file.read(length))
            return s.translate(None, b'\x0d\x0a').decode('utf-8', errors='ignore')
        else:
            return None

    @classmethod
    def date_from_dateindex(cls, dateindex):
        """return the date corresponding to the BusinessObjects 
        universe date index"""
        assert dateindex >= 2442964, 'dateindex must be <= 2442964'
        return datetime.date(1976, 7, 4) + \
            datetime.timedelta(dateindex-2442964)

    # Additional parsing methods for enhanced universe information

    def read_parameters_4_1(self):
        """Read Parameters_4_1 section"""
        if 'Parameters_4_1;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_4_1;'])
        # Read the binary data
        length = self._get_section_length('Parameters_4_1;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_parameters_5_0(self):
        """Read Parameters_5_0 section"""
        if 'Parameters_5_0;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_5_0;'])
        length = self._get_section_length('Parameters_5_0;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_parameters_11_5(self):
        """Read Parameters_11_5 section"""
        if 'Parameters_11_5;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_11_5;'])
        length = self._get_section_length('Parameters_11_5;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_object_formats(self):
        """Read Object_Formats section"""
        if 'Object_Formats;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Object_Formats;'])
        length = self._get_section_length('Object_Formats;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_object_extra_formats(self):
        """Read Object_ExtraFormats section"""
        if 'Object_ExtraFormats;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Object_ExtraFormats;'])
        length = self._get_section_length('Object_ExtraFormats;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_dynamic_class_descriptions(self):
        """Read Dynamic_Class_Descriptions section"""
        if 'Dynamic_Class_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Class_Descriptions;'])
        length = self._get_section_length('Dynamic_Class_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_dynamic_object_descriptions(self):
        """Read Dynamic_Object_Descriptions section"""
        if 'Dynamic_Object_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Object_Descriptions;'])
        length = self._get_section_length('Dynamic_Object_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_dynamic_property_descriptions(self):
        """Read Dynamic_Property_Descriptions section"""
        if 'Dynamic_Property_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Property_Descriptions;'])
        length = self._get_section_length('Dynamic_Property_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_audit_info(self):
        """Read Audit information"""
        if 'Audit;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Audit;'])
        length = self._get_section_length('Audit;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_dimensions(self):
        """Read Dimensions section"""
        if 'Dimensions;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Dimensions;'])
        length = self._get_section_length('Dimensions;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_olap_info(self):
        """Read OLAP information"""
        if 'OLAPInfo;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['OLAPInfo;'])
        length = self._get_section_length('OLAPInfo;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_graphical_info(self):
        """Read Graphical information"""
        if 'Graphical_Info;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Graphical_Info;'])
        length = self._get_section_length('Graphical_Info;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_crystal_references(self):
        """Read Crystal References"""
        if 'Crystal_References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Crystal_References;'])
        length = self._get_section_length('Crystal_References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_xml_lov(self):
        """Read XML LOV information"""
        if 'XML-LOV;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['XML-LOV;'])
        length = self._get_section_length('XML-LOV;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_integrity_rules(self):
        """Read Integrity rules"""
        if 'Integrity;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Integrity;'])
        length = self._get_section_length('Integrity;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_aggregate_navigation(self):
        """Read Aggregate Navigation information"""
        if 'AggregateNavigation;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['AggregateNavigation;'])
        length = self._get_section_length('AggregateNavigation;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_bounded_columns(self):
        """Read Bounded Columns information"""
        if 'BoundedColumns;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['BoundedColumns;'])
        length = self._get_section_length('BoundedColumns;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_build_origin_v6(self):
        """Read Build Origin V6 information"""
        if 'BuildOrigin_v6;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['BuildOrigin_v6;'])
        length = self._get_section_length('BuildOrigin_v6;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_compulsary_type(self):
        """Read Compulsary Type information"""
        if 'CompulsaryType;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['CompulsaryType;'])
        length = self._get_section_length('CompulsaryType;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_deleted_references(self):
        """Read Deleted References"""
        if 'Deleted References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Deleted References;'])
        length = self._get_section_length('Deleted References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_deleted_history(self):
        """Read Deleted History"""
        if 'DELETED_HISTORY;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['DELETED_HISTORY;'])
        length = self._get_section_length('DELETED_HISTORY;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_dot_tables(self):
        """Read Dot Tables information"""
        if 'Dot_Tables;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Dot_Tables;'])
        length = self._get_section_length('Dot_Tables;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_downward(self):
        """Read Downward information"""
        if 'Downward;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Downward;'])
        length = self._get_section_length('Downward;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_format_locale_sort(self):
        """Read Format Locale Sort information"""
        if 'FormatLocaleSort;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['FormatLocaleSort;'])
        length = self._get_section_length('FormatLocaleSort;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_format_version(self):
        """Read Format Version information"""
        if 'FormatVersion;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['FormatVersion;'])
        length = self._get_section_length('FormatVersion;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_joins_extensions(self):
        """Read Joins Extensions"""
        if 'Joins Extensions;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Joins Extensions;'])
        length = self._get_section_length('Joins Extensions;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_key_references(self):
        """Read Key References"""
        if 'Key References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Key References;'])
        length = self._get_section_length('Key References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_kernel_page_format(self):
        """Read Kernel Page Format information"""
        if 'KernelPageFormat;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['KernelPageFormat;'])
        length = self._get_section_length('KernelPageFormat;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_platform(self):
        """Read Platform information"""
        if 'Platform;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Platform;'])
        length = self._get_section_length('Platform;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_unicode_on(self):
        """Read Unicode On information"""
        if 'UNICODE ON;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['UNICODE ON;'])
        length = self._get_section_length('UNICODE ON;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward(self):
        """Read Upward information"""
        if 'Upward;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward;'])
        length = self._get_section_length('Upward;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_local_indexing(self):
        """Read Upward Local Indexing information"""
        if 'Upward_LocalIndexing;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_LocalIndexing;'])
        length = self._get_section_length('Upward_LocalIndexing;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_mapping(self):
        """Read Upward Mapping information"""
        if 'Upward_Mapping;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Mapping;'])
        length = self._get_section_length('Upward_Mapping;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_override(self):
        """Read Upward Override information"""
        if 'Upward_Override;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Override;'])
        length = self._get_section_length('Upward_Override;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_override_new(self):
        """Read Upward Override New information"""
        if 'Upward_Override_New;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Override_New;'])
        length = self._get_section_length('Upward_Override_New;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_windows_page_format(self):
        """Read Windows Page Format information"""
        if 'WindowsPageFormat;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['WindowsPageFormat;'])
        length = self._get_section_length('WindowsPageFormat;')
        if length > 0:
            return self.file.read(length)
        return None

    def _get_section_length(self, marker):
        """Helper method to calculate section length"""
        current_pos = self.file.tell()
        # Find the next marker or end of file
        next_markers = [m for m in self.content_offsets.keys() if self.content_offsets[m] > current_pos]
        if next_markers:
            next_pos = min(self.content_offsets[m] for m in next_markers)
            return next_pos - current_pos
        else:
            # Last section, read to end
            self.file.seek(0, 2)  # Seek to end
            end_pos = self.file.tell()
            self.file.seek(current_pos)
            return end_pos - current_pos

    # Enhanced parsing methods for UNW_Storage and ResourceHeader data

    def parse_unw_storage_data(self):
        """Parse structured data from UNW_Storage directory if available"""
        unw_storage_path = self._get_unw_storage_path()
        if not unw_storage_path:
            return

        # Parse connection information
        self.universe.unw_connection_info = self._parse_unw_connection(unw_storage_path)

        # Parse parameters
        self.universe.unw_parameters = self._parse_unw_parameters(unw_storage_path)

        # Parse objects formats
        self.universe.unw_objects_formats = self._parse_unw_objects_formats(unw_storage_path)

        # Parse hidden items
        self.universe.unw_hidden_items = self._parse_unw_hidden_items(unw_storage_path)

        # Parse custom LOV
        self.universe.unw_custom_lov = self._parse_unw_custom_lov(unw_storage_path)

    def parse_resource_header_data(self):
        """Parse structured data from ResourceHeader directory if available"""
        resource_path = self._get_resource_header_path()
        if not resource_path:
            return

        # Parse descriptor
        self.universe.resource_descriptor = self._parse_resource_descriptor(resource_path)

        # Parse B-descriptor
        self.universe.resource_b_descriptor = self._parse_resource_b_descriptor(resource_path)

        # Parse T-descriptor
        self.universe.resource_t_descriptor = self._parse_resource_t_descriptor(resource_path)

    def _get_unw_storage_path(self):
        """Get path to UNW_Storage directory if it exists"""
        # This would need to be implemented based on how the unzipped data is accessed
        # For now, return None as we don't have direct file system access in this context
        return None

    def _get_resource_header_path(self):
        """Get path to ResourceHeader directory if it exists"""
        # Similar to above
        return None

    def _parse_unw_connection(self, base_path):
        """Parse connection information from UNW_Storage/Connection"""
        try:
            connection_file = os.path.join(base_path, "Connection", "Connection")
            if os.path.exists(connection_file):
                with open(connection_file, 'rb') as f:
                    data = f.read()
                    # Try to extract readable connection information
                    return self._extract_connection_info(data)
        except:
            pass
        return None

    def _parse_unw_parameters(self, base_path):
        """Parse parameters from UNW_Storage/Parameters"""
        params = {}
        try:
            param_file = os.path.join(base_path, "Parameters", "Parameters")
            if os.path.exists(param_file):
                with open(param_file, 'rb') as f:
                    data = f.read()
                    # Try to extract parameter key-value pairs
                    params = self._extract_parameters(data)
        except:
            pass
        return params

    def _parse_unw_objects_formats(self, base_path):
        """Parse objects formats from UNW_Storage/Objects Formats"""
        formats = {}
        try:
            format_file = os.path.join(base_path, "Objects Formats", "Objects Formats")
            if os.path.exists(format_file):
                with open(format_file, 'rb') as f:
                    data = f.read()
                    # Try to extract format information
                    formats = self._extract_formats(data)
        except:
            pass
        return formats

    def _parse_unw_hidden_items(self, base_path):
        """Parse hidden items from UNW_Storage/Hidden_Items"""
        hidden = []
        try:
            hidden_file = os.path.join(base_path, "Hidden_Items", "Hidden_Items")
            if os.path.exists(hidden_file):
                with open(hidden_file, 'rb') as f:
                    data = f.read()
                    # Try to extract hidden item IDs
                    hidden = self._extract_hidden_items(data)
        except:
            pass
        return hidden

    def _parse_unw_custom_lov(self, base_path):
        """Parse custom LOV from UNW_Storage/Customized_LOV"""
        lov = []
        try:
            lov_file = os.path.join(base_path, "Customized_LOV", "Customized_LOV")
            if os.path.exists(lov_file):
                with open(lov_file, 'rb') as f:
                    data = f.read()
                    # Try to extract LOV information
                    lov = self._extract_lov(data)
        except:
            pass
        return lov

    def _parse_resource_descriptor(self, base_path):
        """Parse descriptor from ResourceHeader/Descriptor"""
        try:
            desc_file = os.path.join(base_path, "Descriptor;")
            if os.path.exists(desc_file):
                with open(desc_file, 'rb') as f:
                    data = f.read()
                    return self._extract_descriptor_info(data)
        except:
            pass
        return None

    def _parse_resource_b_descriptor(self, base_path):
        """Parse B-descriptor from ResourceHeader/B-Descriptor"""
        try:
            desc_file = os.path.join(base_path, "B-Descriptor;")
            if os.path.exists(desc_file):
                with open(desc_file, 'rb') as f:
                    return f.read()
        except:
            pass
        return None

    def _parse_resource_t_descriptor(self, base_path):
        """Parse T-descriptor from ResourceHeader/T-Descriptor"""
        try:
            desc_file = os.path.join(base_path, "T-Descriptor;")
            if os.path.exists(desc_file):
                with open(desc_file, 'rb') as f:
                    return f.read()
        except:
            pass
        return None

    def _extract_connection_info(self, data):
        """Extract readable connection information from binary data"""
        try:
            # Look for common patterns in connection data
            info = {}
            # Try to find database name, server, etc.
            data_str = data.decode('utf-8', errors='ignore')

            # Extract database engine
            if 'MS SQL Server' in data_str:
                info['database_engine'] = 'MS SQL Server 2019'

            # Extract database name (look for common patterns)
            import re
            db_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]{0,127})', data_str)
            if db_match:
                info['database_name'] = db_match.group(1)

            return info if info else data
        except:
            return data

    def _extract_parameters(self, data):
        """Extract parameter key-value pairs from binary data"""
        params = {}
        try:
            data_str = data.decode('utf-8', errors='ignore')
            # Look for parameter patterns like KEY=VALUE
            import re
            param_matches = re.findall(r'([A-Z_]+)=([^=\n\r]+)', data_str)
            for key, value in param_matches:
                params[key.strip()] = value.strip()
        except:
            pass
        return params

    def _extract_formats(self, data):
        """Extract format information from binary data"""
        # This would require understanding the format structure
        # For now, return the raw data
        return data

    def _extract_hidden_items(self, data):
        """Extract hidden item IDs from binary data"""
        hidden = []
        try:
            # Hidden items are likely stored as a list of IDs
            # This would need format-specific parsing
            pass
        except:
            pass
        return hidden

    def _extract_lov(self, data):
        """Extract LOV information from binary data"""
        lov = []
        try:
            # LOV data structure parsing would be needed here
            pass
        except:
            pass
        return lov

    def _extract_descriptor_info(self, data):
        """Extract descriptor information from binary data"""
        try:
            data_str = data.decode('utf-8', errors='ignore')
            info = {}

            # Extract universe name
            if 'Univers5' in data_str:
                info['universe_name'] = 'Univers5'

            # Extract other metadata
            if 'Administrator' in data_str:
                info['created_by'] = 'Administrator'

            return info
        except:
            return data

    # Analysis methods

    def perform_cross_reference_analysis(self):
        """Perform cross-reference analysis on the universe"""
        # Analyze object-to-table relationships
        for obj in self._get_all_objects():
            if obj.select_sql:
                table_refs = self._extract_table_references(obj.select_sql)
                for table_ref in table_refs:
                    # Find the actual table
                    table = next((t for t in self.universe.tables if t.name == table_ref), None)
                    if table:
                        self.universe.cross_references[f"obj_{obj.id_}_table_{table.id_}"] = {
                            'type': 'object_table',
                            'object_id': obj.id_,
                            'table_id': table.id_,
                            'object_name': obj.name,
                            'table_name': table.name
                        }
        
        # Analyze join relationships
        for join in self.universe.joins:
            table_refs = self._extract_table_references(join.statement)
            for table_ref in table_refs:
                table = next((t for t in self.universe.tables if t.name == table_ref), None)
                if table:
                    self.universe.cross_references[f"join_{join.id_}_table_{table.id_}"] = {
                        'type': 'join_table',
                        'join_id': join.id_,
                        'table_id': table.id_,
                        'join_statement': join.statement,
                        'table_name': table.name
                    }

    def perform_validation_checks(self):
        """Perform validation checks on the universe"""
        # Check for broken references in SQL
        for obj in self._get_all_objects():
            if obj.select_sql:
                broken_refs = self._find_broken_references(obj.select_sql)
                for broken_ref in broken_refs:
                    self.universe.validation_errors.append({
                        'type': 'broken_reference',
                        'object_id': obj.id_,
                        'object_name': obj.name,
                        'sql_type': 'select',
                        'broken_reference': broken_ref,
                        'message': f"Object '{obj.name}' references non-existent table '{broken_ref}' in SELECT clause"
                    })
            
            if obj.where_sql:
                broken_refs = self._find_broken_references(obj.where_sql)
                for broken_ref in broken_refs:
                    self.universe.validation_errors.append({
                        'type': 'broken_reference',
                        'object_id': obj.id_,
                        'object_name': obj.name,
                        'sql_type': 'where',
                        'broken_reference': broken_ref,
                        'message': f"Object '{obj.name}' references non-existent table '{broken_ref}' in WHERE clause"
                    })
        
        # Check for orphaned objects (objects that reference non-existent tables)
        for obj in self._get_all_objects():
            if obj.select_sql:
                table_refs = self._extract_table_references(obj.select_sql)
                if not table_refs:
                    self.universe.validation_errors.append({
                        'type': 'orphaned_object',
                        'object_id': obj.id_,
                        'object_name': obj.name,
                        'message': f"Object '{obj.name}' has no table references in SELECT clause"
                    })

    def perform_dependency_analysis(self):
        """Perform dependency analysis on the universe"""
        # Build dependency graph
        deps = self._analyze_dependencies()
        self.universe.dependency_graph = deps

    def _extract_database_tables(self):
        """Extract detailed database table information"""
        self.universe.database_tables = {}
        for table in self.universe.tables:
            # Handle None names and generate meaningful identifiers
            table_name = table.name if table.name else None
            table_schema = table.schema if table.schema else None
            
            # Check for corrupted names (non-printable characters, excessive length, etc.)
            if table_name:
                # If the name contains many non-alphanumeric characters or is too long, it's likely corrupted
                printable_ratio = sum(1 for c in table_name if c.isprintable()) / len(table_name) if table_name else 0
                if printable_ratio < 0.7 or len(table_name) > 256:
                    table_name = None
                # If it's mostly null/whitespace, consider it corrupted
                elif not table_name.strip():
                    table_name = None
            
            if not table_name:
                table_name = f"UNNAMED_TABLE_{table.id_}"
            
            # For aliases with invalid parents, mark them as invalid
            parent_id = table.parent_id if table.is_alias else None
            is_valid_alias = table.is_alias
            if table.is_alias and table.parent_id not in self.universe.table_map:
                is_valid_alias = False
            
            table_info = {
                'id': table.id_,
                'name': table_name,
                'schema': table_schema if table_schema else "",
                'fullname': f"{table_schema}.{table_name}" if table_schema else table_name,
                'is_alias': table.is_alias,
                'is_valid_alias': is_valid_alias,
                'parent_id': parent_id,
                'column_count': 0,  # Will be updated when columns are extracted
                'used_in_objects': [],
                'used_in_joins': []
            }
            self.universe.database_tables[table.id_] = table_info

    def _extract_table_columns(self):
        """Extract database table columns information"""
        self.universe.table_columns = {}
        for column in self.universe.columns:
            table_id = column.parent.id_ if column.parent else None
            if table_id is not None:
                if table_id not in self.universe.table_columns:
                    self.universe.table_columns[table_id] = []

                column_info = {
                    'id': column.id_,
                    'name': column.name,
                    'table_id': table_id,
                    'fullname': column.fullname
                }
                self.universe.table_columns[table_id].append(column_info)

                # Update column count in database_tables
                if table_id in self.universe.database_tables:
                    self.universe.database_tables[table_id]['column_count'] += 1

    def _extract_join_details(self):
        """Extract detailed join information between database tables"""
        self.universe.join_details = {}
        for join in self.universe.joins:
            join_info = {
                'id': join.id_,
                'statement': join.statement,
                'expression': join.expression,
                'term_count': join.term_count,
                'terms': join.terms,
                'tables_involved': []
            }

            # Extract tables involved in this join
            for term in join.terms:
                column_name, table_id = term
                if table_id in self.universe.database_tables:
                    table_name = self.universe.database_tables[table_id]['name']
                    join_info['tables_involved'].append({
                        'table_id': table_id,
                        'table_name': table_name,
                        'column': column_name
                    })
                    # Track which joins use each table
                    self.universe.database_tables[table_id]['used_in_joins'].append(join.id_)

            self.universe.join_details[join.id_] = join_info

    def _extract_context_details(self):
        """Extract context details including associated joins and tables"""
        self.universe.context_details = {}
        for context in self.universe.contexts:
            context_info = {
                'id': context.id_,
                'name': context.name,
                'description': context.description,
                'joins': context.joins,
                'tables_involved': set(),
                'objects_affected': []
            }

            # Find tables involved in context joins
            for join_id in context.joins:
                if join_id in self.universe.join_details:
                    join_info = self.universe.join_details[join_id]
                    for table_info in join_info['tables_involved']:
                        context_info['tables_involved'].add(table_info['table_id'])

            context_info['tables_involved'] = list(context_info['tables_involved'])
            self.universe.context_details[context.id_] = context_info

    def _analyze_context_incompatibilities(self):
        """Analyze incompatible objects between different contexts"""
        self.universe.context_incompatibilities = []

        # Get all objects that belong to contexts
        context_objects = {}
        for context in self.universe.contexts:
            context_objects[context.id_] = set()

        # For each object, determine which contexts it can be used in
        # This is a simplified analysis - in reality, context incompatibilities
        # are determined by the joins and tables an object references
        for cls in self.universe.classes:
            self._analyze_class_contexts(cls, context_objects)

        # Find objects that are incompatible between contexts
        for obj_id, obj_contexts in context_objects.items():
            if len(obj_contexts) > 1:
                # Object can be used in multiple contexts - check for conflicts
                contexts_list = list(obj_contexts)
                for i, ctx1 in enumerate(contexts_list):
                    for ctx2 in contexts_list[i+1:]:
                        if self._contexts_are_incompatible(ctx1, ctx2):
                            obj_name = self._get_object_name_by_id(obj_id)
                            incompatibility = {
                                'object_id': obj_id,
                                'object_name': obj_name,
                                'context1_id': ctx1,
                                'context1_name': self._get_context_name_by_id(ctx1),
                                'context2_id': ctx2,
                                'context2_name': self._get_context_name_by_id(ctx2),
                                'reason': 'Object references tables from incompatible contexts'
                            }
                            self.universe.context_incompatibilities.append(incompatibility)

    def _analyze_class_contexts(self, cls, context_objects):
        """Analyze which contexts a class's objects belong to"""
        for obj in cls.objects:
            obj_contexts = set()
            # Determine contexts based on table references
            table_refs = self._extract_table_references(obj.select_sql)
            if table_refs:
                for table_ref in table_refs:
                    for context_id, context_info in self.universe.context_details.items():
                        if any(self.universe.database_tables.get(tid, {}).get('name') == table_ref 
                               for tid in context_info['tables_involved']):
                            obj_contexts.add(context_id)
            context_objects[obj.id_] = obj_contexts

        for subclass in cls.subclasses:
            self._analyze_class_contexts(subclass, context_objects)

    def _contexts_are_incompatible(self, ctx1_id, ctx2_id):
        """Check if two contexts are incompatible"""
        # Simplified check: contexts are incompatible if they don't share any joins
        ctx1_joins = set(self.universe.context_details[ctx1_id]['joins'])
        ctx2_joins = set(self.universe.context_details[ctx2_id]['joins'])
        return len(ctx1_joins & ctx2_joins) == 0

    def _get_object_name_by_id(self, obj_id):
        """Get object name by ID"""
        for cls in self.universe.classes:
            name = self._find_object_in_class(cls, obj_id)
            if name:
                return name
        return f"Object_{obj_id}"

    def _find_object_in_class(self, cls, obj_id):
        """Find object name in class hierarchy"""
        for obj in cls.objects:
            if obj.id_ == obj_id:
                return obj.name
        for subclass in cls.subclasses:
            name = self._find_object_in_class(subclass, obj_id)
            if name:
                return name
        return None

    def _get_context_name_by_id(self, ctx_id):
        """Get context name by ID"""
        for context in self.universe.contexts:
            if context.id_ == ctx_id:
                return context.name
        return f"Context_{ctx_id}"

    def _extract_lov_definitions(self):
        """Extract List of Values (LOV) definitions"""
        self.universe.lov_definitions = {}

        # Extract LOV information from objects
        for cls in self.universe.classes:
            self._extract_lov_from_class(cls)

        # Also check XML LOV data if available
        if hasattr(self.universe, 'xml_lov') and self.universe.xml_lov:
            self._parse_xml_lov()

    def _extract_lov_from_class(self, cls):
        """Extract LOV information from objects in a class"""
        for obj in cls.objects:
            if hasattr(obj, 'lov_name') and obj.lov_name:
                lov_info = {
                    'object_id': obj.id_,
                    'object_name': obj.name,
                    'lov_name': obj.lov_name,
                    'select_sql': obj.select_sql,
                    'source': 'object_definition'
                }
                self.universe.lov_definitions[obj.id_] = lov_info

        for subclass in cls.subclasses:
            self._extract_lov_from_class(subclass)

    def _parse_xml_lov(self):
        """Parse XML LOV data if available"""
        # This would parse the XML LOV data from universe.xml_lov
        # For now, just mark that XML LOV data exists
        if self.universe.xml_lov:
            xml_lov_info = {
                'source': 'xml_lov',
                'size': len(self.universe.xml_lov),
                'parsed': False  # Would need XML parsing implementation
            }
            self.universe.lov_definitions['xml_lov'] = xml_lov_info

    def perform_enhanced_analysis(self):
        """Perform enhanced analysis to extract database tables, columns, joins, contexts, and LOV information"""
        print("DEBUG: Starting enhanced analysis")
        self._extract_database_tables()
        print(f"DEBUG: Extracted {len(self.universe.database_tables)} database tables")
        self._extract_table_columns()
        print(f"DEBUG: Extracted columns for {len(self.universe.table_columns)} tables")
        self._extract_join_details()
        print(f"DEBUG: Extracted {len(self.universe.join_details)} join details")
        self._extract_context_details()
        print(f"DEBUG: Extracted {len(self.universe.context_details)} context details")
        self._analyze_context_incompatibilities()
        print(f"DEBUG: Found {len(self.universe.context_incompatibilities)} incompatibilities")
        self._extract_lov_definitions()
        print(f"DEBUG: Extracted {len(self.universe.lov_definitions)} LOV definitions")
        self._extract_stored_procedure_parameters()
        print(f"DEBUG: Extracted {len(self.universe.stored_procedure_parameters)} stored procedures with parameters")
        print("DEBUG: Enhanced analysis completed")

    # Helper methods for analysis

    def _extract_stored_procedure_parameters(self):
        """Extract stored procedure parameters from the UNW_Storage/Tables file"""
        import xml.etree.ElementTree as ET
        import re
        
        try:
            # Get the path to UNW_Storage if available
            unw_storage_path = self._get_unw_storage_path()
            
            if not unw_storage_path:
                # Try to read from content offsets if UNW_Storage is not available
                self._extract_procedure_params_from_binary()
            else:
                # Read from UNW_Storage/Tables file
                tables_file = os.path.join(unw_storage_path, "Tables", "Tables")
                if os.path.exists(tables_file):
                    with open(tables_file, 'rb') as f:
                        data = f.read()
                    self._parse_procedure_xml_from_binary(data)
                    
        except Exception as e:
            print(f"DEBUG: Error extracting stored procedure parameters: {e}")

    def _extract_procedure_params_from_binary(self):
        """Extract procedure parameters from the binary file content"""
        try:
            # Seek to Tables; section and extract procedure XML
            if 'Tables;' not in self.content_offsets:
                return
                
            self.file.seek(self.content_offsets['Tables;'])
            # Skip header information
            self.file.read(2)
            user_name = self.read_string()
            schema = self.read_string()
            max_table_id, = struct.unpack('<I', self.file.read(4))
            table_count, = struct.unpack('<I', self.file.read(4))
            
            # Read remaining content which may contain procedure XML
            remaining_data = self.file.read()
            self._parse_procedure_xml_from_binary(remaining_data)
            
        except Exception as e:
            print(f"DEBUG: Error reading procedure parameters from binary: {e}")

    def _parse_procedure_xml_from_binary(self, data):
        """Parse procedure XML from binary data to extract parameters"""
        try:
            # Convert binary data to string
            data_str = data.decode('latin-1', errors='ignore')
            
            # Find all Procedure tags
            proc_pattern = r'<Procedure[^>]*>.*?</Procedure>'
            proc_matches = re.findall(proc_pattern, data_str, re.DOTALL)
            
            for proc_xml_raw in proc_matches:
                # Clean up XML entities
                proc_xml = proc_xml_raw.replace('&quot;', '"')
                
                try:
                    # Parse the XML
                    root = ET.fromstring(proc_xml)
                    proc_name = root.get('name', 'Unknown')
                    
                    # Extract parameters
                    parameters = []
                    for param in root.findall('.//Parameter'):
                        param_info = {
                            'name': param.get('name', ''),
                            'type': param.get('type', ''),
                            'value': param.get('value', '')
                        }
                        parameters.append(param_info)
                    
                    if parameters:
                        self.universe.stored_procedure_parameters[proc_name] = parameters
                        
                except Exception as parse_err:
                    # Try manual parsing if XML parsing fails
                    self._parse_procedure_parameters_manual(proc_xml_raw)
                    
        except Exception as e:
            print(f"DEBUG: Error parsing procedure XML: {e}")

    def _parse_procedure_parameters_manual(self, proc_str):
        """Manually parse procedure parameters if XML parsing fails"""
        import re
        
        try:
            # Extract procedure name
            name_match = re.search(r'name="([^"]*)"', proc_str)
            proc_name = name_match.group(1) if name_match else 'Unknown'
            
            # Extract all Parameter tags
            param_pattern = r'<Parameter\s+name="([^"]*)"[^>]*type="([^"]*)"[^>]*value="([^"]*)"'
            param_matches = re.findall(param_pattern, proc_str)
            
            if param_matches:
                parameters = []
                for name, param_type, value in param_matches:
                    parameters.append({
                        'name': name,
                        'type': param_type,
                        'value': value
                    })
                
                self.universe.stored_procedure_parameters[proc_name] = parameters
                
        except Exception as e:
            pass  # Silent failure for manual parsing
        
    def _get_all_objects(self):
        """Get all objects from all classes recursively"""
        objects = []
        for cls in self.universe.classes:
            self._collect_objects_from_class(cls, objects)
        return objects

    def _collect_objects_from_class(self, cls, objects_list):
        """Recursively collect objects from a class and its subclasses"""
        objects_list.extend(cls.objects)
        for subclass in cls.subclasses:
            self._collect_objects_from_class(subclass, objects_list)

    def _extract_table_references(self, sql):
        """Extract table references from SQL"""
        if not sql:
            return []
        table_refs = []
        # Simple regex to find table references in SQL
        # This is a basic implementation - could be enhanced
        import re
        # Look for patterns like Table_Name. or @aggregate_aware(Table_Name.
        table_pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\.'
        matches = re.findall(table_pattern, sql)
        # Remove duplicates and filter out common SQL keywords
        sql_keywords = {'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL'}
        table_refs = [match for match in matches if match.upper() not in sql_keywords]
        return list(set(table_refs))  # Remove duplicates

    def _find_broken_references(self, sql):
        """Find broken table references in SQL"""
        if not sql:
            return []
        table_refs = self._extract_table_references(sql)
        broken_refs = []
        for table_ref in table_refs:
            # Check if table exists in universe
            table_exists = any(t.name == table_ref for t in self.universe.tables)
            if not table_exists:
                broken_refs.append(table_ref)
        return broken_refs

    def _analyze_dependencies(self):
        """Analyze dependencies between objects"""
        deps = {}
        for obj in self._get_all_objects():
            obj_deps = []
            if obj.select_sql:
                table_refs = self._extract_table_references(obj.select_sql)
                obj_deps.extend(table_refs)
            if obj.where_sql:
                table_refs = self._extract_table_references(obj.where_sql)
                obj_deps.extend(table_refs)
            deps[obj.id_] = obj_deps
        return deps
