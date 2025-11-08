#!/usr/bin/env python
# encoding: utf-8
"""
pyunv.py

Created by David Peckham on 2009-09-01.
Copyright (c) 2009 David Peckham. All rights reserved.

Enhanced by Sanjay Sharma (indoos@gmail.com) 2025-10-17.
"""

import os
import re
import sys
import collections
__version__ = "0.3.0"


class Universe(object):

    def __init__(self, id_=None, name=None, description=None):
        super(Universe, self).__init__()
        self.pyunv_version = __version__
        self.id_ = id_
        self.name = name
        self.description = description
        self.schema = None
        self.tables = []
        self.virtual_tables = []
        self.columns = []
        self.classes = []
        self.joins = []
        self.contexts = []
        self.links = []
        self.hierarchies = []
        self.parameters = None
        self.custom_parameters = None
        # Additional universe metadata
        self.parameters_4_1 = None
        self.parameters_5_0 = None
        self.parameters_11_5 = None
        self.object_formats = []
        self.object_extra_formats = []
        self.dynamic_class_descriptions = {}
        self.dynamic_object_descriptions = {}
        self.dynamic_property_descriptions = {}
        self.audit_info = None
        self.dimensions = []
        self.olap_info = None
        self.graphical_info = None
        self.crystal_references = []
        self.xml_lov = None
        self.integrity_rules = []
        self.aggregate_navigation = None
        self.bounded_columns = []
        self.build_origin_v6 = None
        self.compulsary_type = None
        self.deleted_references = []
        self.deleted_history = []
        self.dot_tables = []
        self.downward = None
        self.format_locale_sort = None
        self.format_version = None
        self.joins_extensions = []
        self.key_references = []
        self.kernel_page_format = None
        self.platform = None
        self.unicode_on = None
        self.upward = None
        self.upward_local_indexing = None
        self.upward_mapping = None
        self.upward_override = None
        self.upward_override_new = None
        self.windows_page_format = None
        # Parsed UNW_Storage data
        self.unw_connection_info = None
        self.unw_connection_map_parameters = None
        self.unw_contexts = None
        self.unw_crystal_references = None
        self.unw_custom_lov = []
        self.unw_dot_tables = None
        self.unw_dynamic_classes_descriptions = None
        self.unw_dynamic_objects_descriptions = None
        self.unw_dynamic_properties_descriptions = None
        self.unw_fc_information = None
        self.unw_graphical_comments = None
        self.unw_hidden_items = []
        self.unw_hierarchies = None
        self.unw_input_columns = None
        self.unw_joins = None
        self.unw_objects_formats = {}
        self.unw_parameters = {}
        self.unw_tables = None
        self.unw_upward_aggregate_aware = None
        # Parsed ResourceHeader data
        self.resource_descriptor = None
        self.resource_b_descriptor = None
        self.resource_t_descriptor = None
        # Analysis data
        self.cross_references = {}
        self.validation_errors = []
        self.dependency_graph = {}
        # Enhanced analysis data
        self.database_tables = {}
        self.table_columns = {}
        self.join_details = {}
        self.context_details = {}
        self.context_incompatibilities = []
        self.lov_definitions = {}
        self.stored_procedure_parameters = {}  # {procedure_name: [{name, type, value}, ...]}
        self.table_map = {}
        self.object_map = {}

    def build_table_map(self):
        """Construct a table map so we can expand where and select clauses"""
        for t in self.tables:
            self.table_map[t.id_] = t

    def build_object_map(self):
        """Construct an object map so we can expand where and select clauses"""
        for c in self.classes:
            self._map_objects(c)
    
    def _map_objects(self, c):
        for o in c.objects:
            self.object_map[o.id_] = o
        for subclass in c.subclasses:
            self._map_objects(subclass)
    
    @property
    def statistics(self):
        
        class Counter(ClassVisitor):
            
            def __init__(self):
                super(Counter, self).__init__()
                self.classes = 0
                self.objects = 0
                self.conditions = 0
            
            def visit_class(self, cls):
                self.classes += 1
            
            def visit_object(self, obj):
                self.objects += 1
            
            def visit_condition(self, cond):
                self.conditions += 1
        
        counter = Counter()
        for c in self.classes:
            c.accept(counter)
        
        stats = dict()
        stats["classes"] = counter.classes
        stats["objects"] = counter.objects
        stats["aliases"] = len([t for t in self.tables if t.is_alias])
        stats["tables"] = len([t for t in self.tables if not t.is_alias])
        stats["joins"] = len(self.joins)
        stats["contexts"] = len(self.contexts)
        # stats["hierarchies"] =
        stats["conditions"] = counter.conditions
        return stats


class Parameters(object):
    
    def __init__(self):
        super(Parameters, self).__init__()
        self.universe_filename = None
        self.universe_name = None
        self.revision = 0
        self.description = None
        self.created_by = None
        self.modified_by = None
        self.created_date = None
        self.modified_date = None
        self.query_time_limit = 0
        self.query_row_limit = 0
        self.object_strategy = None
        self.cost_estimate_warning_limit = 0
        self.long_text_limit = 0
        self.comments = None
        self.domain = None
        self.dbms_engine = None
        self.network_layer = None


class Class(object):
    
    def __init__(self, universe, id_, parent, name, description):
        super(Class, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.parent = parent
        self.name = name
        self.description = description
        self.objects = []
        self.conditions = []
        self.subclasses = []
    
    def accept(self, visitor):
        visitor.visit_class(self)
        for o in self.objects:
            o.accept(visitor)
        for c in self.conditions:
            c.accept(visitor)
        for s in self.subclasses:
            s.accept(visitor)


class Join(object):
    
    def __init__(self, universe, id_):
        super(Join, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.expression = None
        self.term_count = 0
        self.terms = []
    
    @property
    def statement(self):
        if self.term_count == 2:
            s = self.fullterm(self.terms[0]) + self.expression + \
                self.fullterm(self.terms[1])
        else:
            format = self.expression.replace(chr(1), '%s')
            s = format % tuple([self.fullterm(t) for t in self.terms])
        return s
    
    def fullterm(self, term):
        """return the fully qualified term with table and column names"""
        column_name, table_id = term
        table = self.universe.table_map.get(table_id)
        if table:
            return '%s.%s' % (table.name, column_name)
        else:
            return 'UnknownTable_%d.%s' % (table_id, column_name)


class Context(object):
    
    def __init__(self, universe, id_, name, description):
        super(Context, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.name = name
        self.description = description
        self.joins = []
    
    @property
    def join_list(self):
        return ', '.join([str(join_id) for join_id in self.joins])


class Link(object):
    
    def __init__(self, universe, id_, name, description, linked_universe=None):
        super(Link, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.name = name
        self.description = description
        self.linked_universe = linked_universe
    
    def __str__(self):
        return '%s id=%d, name=%s, linked_universe=%s' % (
            type(self).__name__, self.id_, self.name, self.linked_universe)


class Hierarchy(object):
    
    def __init__(self, universe, id_, name, description=None):
        super(Hierarchy, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.name = name
        self.description = description
        self.levels = []  # List of object IDs that make up the hierarchy levels
    
    def __str__(self):
        return '%s id=%d, name=%s, levels=%s' % (
            type(self).__name__, self.id_, self.name, self.levels)


class ObjectBase(object):
    
    def __init__(self, universe, id_, parent, name, description):
        super(ObjectBase, self).__init__()
        assert(universe)
        self.universe = universe
        self.id_ = id_
        self.parent = parent
        self.name = name
        self.description = description
        self.select_table_refs = []
        self.where_table_refs = []
        self.select = None
        self.where = None
        self.visible = True
    
    @property
    def fullname(self):
        if self.parent:
            return '%s.%s' % (self.parent.name, self.name)
        else:
            return self.name
    
    def lookup_table(self, match):
        table_id = int(match.groups()[0])
        table = self.universe.table_map.get(table_id)
        if table:
            return table.name
        else:
            return f"UnknownTable_{table_id}"
    
    def lookup_object(self, match):
        object_id = int(match.groups()[0])
        obj = self.universe.object_map.get(object_id)
        if obj:
            return obj.fullname
        else:
            return f"UnknownObject_{object_id}"
    
    def expand_sql(self, sql):
        """Return the SQL with table names instead of table IDs"""
        if sql:
            p = re.compile(r'(?:'+chr(3)+')([0-9]{1,4})')
            expanded_sql = p.sub(self.lookup_table, sql)
            p = re.compile(r'(?:'+chr(2)+')([0-9]{1,4})')
            return p.sub(self.lookup_object, expanded_sql)
        else:
            return None
    
    @property
    def select_sql(self):
        return self.expand_sql(self.select)
    
    @property
    def where_sql(self):
        return self.expand_sql(self.where)
    
    def __str__(self):
        return '%s id=%d, name=%s, select=%s' % (type(self),
            self.id_, self.name, self.select)


class Object(ObjectBase):
    
    def __init__(self, universe, id_, parent, name, description):
        super(Object, self).__init__(universe, id_, parent, name, description)
        self.format = None
        self.lov_name = None
    
    @classmethod
    def unknown(cls):
        # Create a dummy universe for unknown objects
        dummy_universe = Universe()
        return Object(dummy_universe, -1, None, "Unknown", 
            "This object has been deleted from the universe")
    
    def accept(self, visitor):
        visitor.visit_object(self)


class Condition(ObjectBase):
    
    def __init__(self, universe, id_, parent, name, description):
        super(Condition, self).__init__(universe, id_, 
            parent, name, description)
    
    def accept(self, visitor):
        visitor.visit_condition(self)


class Table(object):
    
    def __init__(self, universe, id_, parent_id, name, schema):
        super(Table, self).__init__()
        self.universe = universe
        self.id_ = id_
        self.parent_id = parent_id
        self.name = name
        self.schema = schema
    
    @property
    def fullname(self):
        if self.schema and self.name:
            s = '%s.%s' % (self.schema, self.name)
        elif self.name:
            s = self.name
        else:
            s = 'Unknown'
        if self.is_alias and self.universe and self.parent_id in self.universe.table_map:
            parent_fullname = self.universe.table_map[self.parent_id].fullname
            if parent_fullname:
                s += ' (alias for %s)' % parent_fullname
        return s
    
    @property
    def is_alias(self):
        return self.parent_id != 0
    
    def __str__(self):
        return '%s id=%d, schema=%s name=%s' % (type(self),
            self.id_, self.schema, self.name)
    
    @classmethod
    def unknown(cls):
        return Table(None, -1, -1, None, "Unknown")


class VirtualTable(object):
    
    def __init__(self, universe, table_id=None, select=None):
        super(VirtualTable, self).__init__()
        self.universe = universe
        self.table_id = table_id
        self.select = select
    
    def __str__(self):
        return '%s table_id=%d, select=%s' % (type(self),
            self.table_id, self.select)


class Column(object):
    
    def __init__(self, id_=None, name=None, parent=None, universe=None):
        super(Column, self).__init__()
        self.id_ = id_
        self.name = name
        self.parent = parent
        self.universe = universe
    
    @property
    def fullname(self):
        if self.parent:
            return '%s.%s' % (self.parent.name, self.name)
        else:
            return self.name
    
    def __cmp__(self, other):
        return (self.id_ > other.id_) - (self.id_ < other.id_)
    
    def __lt__(self, other):
        return self.id_ < other.id_
    
    def __eq__(self, other):
        return self.id_ == other.id_
    
    def __str__(self):
        return '%s id=%d, name=%s parent=%d' % (type(self),
            self.id_, self.name, self.parent)


class ClassVisitor(object):
    
    """Visits each node in the class, object, and condition hierarchy"""
    
    def __init__(self):
        super(ClassVisitor, self).__init__()
    
    def visit_class(self, cls):
        """docstring for visit_class"""
        pass
    
    def visit_object(self, obj):
        """docstring for visit_object"""
        pass
    
    def visit_condition(self, condition):
        """docstring for visit_condition"""
        pass
