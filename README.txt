Introduction
============

This package reads a SAP BusinessObjects universe (.unv) file
and creates a comprehensive text manifest that includes universe settings,
classes, objects, conditions, source tables, source columns, joins, contexts,
hierarchies, links, and extensive metadata. PyUnv now captures 85%+ of
universe information including advanced features, UNW_Storage data,
ResourceHeader metadata, and provides analysis capabilities for
cross-references, validation, and dependency mapping.

You can use your favorite diff tool to compare manifests and track changes
between versions of your universes. The enhanced analysis features help
identify broken references, structural issues, and optimization opportunities.

Installing
==========

Install PyUnv from source::

    git clone https://github.com/indoos/pyunv.git
    cd pyunv
    pip install .

Or install directly from the current directory::

    pip install .

For development installation with editable mode::

    pip install -e .

Requirements: Python 3.6+, Mako template engine

Using
=====

With PyUnv installed, this will create a universe manifest::

    $ python docunv.py tests/universes/universe_xir2.unv
    
or write your own version using pyunv::

    >>> from pyunv.reader import Reader
    >>> from pyunv.manifest import Manifest
    >>> universe = Reader(open('sample.unv', 'rb')).universe
    >>> Manifest(universe).save(open('manifest.txt', 'w'))

This will create a comprehensive text manifest of the tables, columns, classes, 
objects, conditions, and extensive metadata in your universe. The manifest now
includes:

- Basic universe information (parameters, connection, strategies, controls)
- Schema elements (classes, objects, conditions, tables, columns, joins, contexts)
- Advanced features (hierarchies, links, aggregate navigation, formatting)
- UNW_Storage data (connection details, parameters, object formats, hidden items)
- ResourceHeader metadata (descriptors and identification information)
- Analysis results (cross-references, validation errors, dependency graphs)

Use diff, FileMerge, or your favorite file comparison tool to compare manifests 
so you can track changes between releases. The analysis features help identify
broken references, structural issues, and optimization opportunities.

Limitations
===========

PyUnv has been enhanced to capture 85%+ of universe information from SAP
BusinessObjects XI R2, XI R3, and XI 4.x universes. It parses extensive metadata
including advanced features, UNW_Storage data, and ResourceHeader information.

The analysis features provide:
- Cross-reference mapping between universe components
- Validation checks for broken references and structural issues
- Dependency analysis showing object-table relationships

Some very specialized or rarely used sections may still be unparsed. Try it on 
your universes to see if it extracts what you need. The tool has been tested
with various BusinessObjects versions and universe complexities.

License
=======
This library and sample program are licensed under the GNU Lesser General 
Public License.