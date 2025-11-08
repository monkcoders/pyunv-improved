# PyUnv - SAP BusinessObjects Universe Parser

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-LGPL--2.1-green.svg)](https://www.gnu.org/licenses/lgpl-2.1.html)

PyUnv is a comprehensive Python library for parsing and documenting SAP BusinessObjects universe (`.unv`) files. It extracts extensive metadata and provides advanced analysis capabilities to help you understand, validate, and document your BusinessObjects universes. It is a fork of https://github.com/davidpeckham/pyunv for python3 support and wider SAP BO Universe parsing.

## 🚀 Key Features

### Core Functionality
- **Complete Universe Parsing**: Extracts 85%+ of universe information from SAP BusinessObjects XI R2, XI R3, and XI 4.x universes
- **Comprehensive Manifest Generation**: Creates detailed text manifests with universe settings, classes, objects, conditions, tables, columns, joins, contexts, hierarchies, and links
- **Advanced Metadata Extraction**: Parses extensive metadata including parameters, formatting, audit information, and structural data

### Enhanced Analysis Features ✨
- **Cross-Reference Analysis**: Maps relationships between universe components (objects ↔ tables, joins ↔ tables)
- **Validation Checks**: Identifies broken references, orphaned objects, and structural issues
- **Dependency Analysis**: Builds dependency graphs showing object-table relationships
- **UNW_Storage Parsing**: Extracts structured data including connection details, object formats, and hidden items
- **ResourceHeader Metadata**: Parses descriptor and identification information

### Python 3 Support 🐍
- **Full Python 3 Compatibility**: Tested and optimized for Python 3.6+
- **Modern Python Standards**: Uses contemporary Python patterns and best practices
- **Enhanced Error Handling**: Improved exception handling and backward compatibility
- **Type Safety**: Better data structure handling and validation

## 📦 Installation

### From Source
```bash
git clone https://github.com/indoos/pyunv.git
cd pyunv
pip install .
```

### Development Installation
```bash
pip install -e .
```

### Requirements
- Python 3.6 or later
- Mako template engine

## 🛠️ Usage

### Command Line
```bash
# Generate a universe manifest
python docunv.py tests/universes/universe_xir2.unv
```

### Python API
```python
from pyunv.reader import Reader
from pyunv.manifest import Manifest

# Parse a universe file
with open('sample.unv', 'rb') as f:
    universe = Reader(f).universe

# Generate manifest
manifest = Manifest(universe)
manifest.save(open('manifest.txt', 'w'))

# Access analysis results
print(f"Cross-references found: {len(universe.cross_references)}")
print(f"Validation errors: {len(universe.validation_errors)}")
print(f"Universe: {universe.parameters.universe_name}")
```

### Analysis Features
```python
# Cross-reference analysis
for ref_key, ref_data in universe.cross_references.items():
    print(f"{ref_data['type']}: {ref_data['object_name']} → {ref_data['table_name']}")

# Validation results
for error in universe.validation_errors:
    print(f"Error: {error['message']}")

# Dependency graph
for dep_key, dep_data in universe.dependency_graph.items():
    print(f"Dependency: {dep_key}")
```

## 📋 Manifest Content

The generated manifest includes:

### Basic Information
- Universe parameters (name, description, connection details)
- Creation/modification metadata
- Statistics (classes, objects, tables, joins, contexts)

### Schema Elements
- **Classes & Objects**: Hierarchical structure with properties
- **Conditions**: Business rules and filters
- **Tables & Columns**: Source database schema
- **Joins & Contexts**: Data relationships and integrity rules
- **Hierarchies & Links**: Advanced navigation structures

### Advanced Features
- Aggregate navigation and bounded columns
- Object formatting and extra formats
- Dynamic descriptions and audit information
- OLAP information and graphical metadata
- Crystal references and XML LOV data

### Enhanced Sections (v0.3.0+)
- **UNW_Storage Data**: Connection info, parameters, formats, hidden items
- **ResourceHeader Metadata**: Descriptors and identification data
- **Analysis Results**: Cross-references, validation errors, dependency graphs

## 🔍 Analysis Capabilities

### Cross-Reference Analysis
Automatically maps relationships between:
- Objects and their source tables
- Joins and referenced tables
- Contexts and their join components

### Validation Checks
Identifies:
- Broken table references in SQL
- Orphaned objects without table dependencies
- Structural inconsistencies

### Dependency Analysis
Builds comprehensive dependency graphs showing:
- Object-to-table relationships
- Join dependencies
- Context hierarchies

## 📊 Sample Output

```
Universe Manifest created by pyunv 0.3.0

    Name: eFashion
    Filename: eFashion.unv
    Description: eFashion retail Data Warehouse

General Information
    Created by: Administrator on 2025-09-01
    Statistics: 5 classes, 34 objects, 4 tables, 9 joins, 2 contexts

Classes
    Time Period
        Year (id: 188) - select: ..., where: ...
        Quarter (id: 186) - select: ..., where: ...
        Month (id: 185) - select: ..., where: ...

Analysis Results
    Cross References: 29 entries
    Validation Errors: 39 issues found
    Dependency Graph: relationships mapped
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/ -v
```

Test specific functionality:
```bash
# Test universe parsing
python -c "from pyunv.reader import Reader; u = Reader(open('tests/universes/eFashion.unv', 'rb')).universe; print(f'Loaded: {u.parameters.universe_name}')"

# Test manifest generation
python -c "from pyunv.reader import Reader; from pyunv.manifest import Manifest; u = Reader(open('tests/universes/eFashion.unv', 'rb')).universe; Manifest(u).save(open('test.txt', 'w'))"
```

## ⚖️ Limitations

- Captures 85%+ of universe information (significant improvement from ~15% in v0.2.x)
- Some very specialized or rarely used sections may remain unparsed
- Requires SAP BusinessObjects XI R2, XI R3, or XI 4.x universe files
- UNW_Storage and ResourceHeader parsing depends on file system access (may be limited in some environments)

## 🔄 Version History

### v0.3.0 (October 17, 2025) - Major Enhancement
- **Python 3 Support**: Full compatibility with Python 3.6+
- **Extended Parsing**: 35+ new content markers for comprehensive universe parsing
- **UNW_Storage Support**: Structured data extraction for connections, formats, and metadata
- **ResourceHeader Parsing**: Descriptor and identification metadata
- **Analysis Engine**: Cross-reference, validation, and dependency analysis
- **Enhanced Manifest**: Complete template with all metadata categories
- **Improved Error Handling**: Better exception management and backward compatibility

### v0.2.4 (October 26, 2009)
- PyPI description updates
- File overwrite protection in docunv.py

### v0.2.3 (October 25, 2009)
- Added docunv console program
- py2exe support for Windows executables
- Custom template support
- Enhanced unit tests

### v0.2.2 (September 28, 2009)
- Improved manifest constructor
- PEP8 compliance

### v0.2.1 (September 27, 2009)
- Context parsing
- Custom parameter support
- Table/alias differentiation

## 📄 License

This library is licensed under the GNU Lesser General Public License v2.1.

```
Copyright (C) 1991, 1999 Free Software Foundation, Inc.
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Report bugs or request features](https://github.com/indoos/pyunv/issues)
- Documentation: Comprehensive inline documentation and examples

## 🙏 Acknowledgments

- Original development by David Peckham
- Enhanced by Sanjay Sharma (indoos@gmail.com) - Python 3 support and advanced features
- SAP BusinessObjects community for format documentation