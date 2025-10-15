# Tool Loss Investigation Report

## Problem Statement
Users report that `load_all_tools()` creates 326 tools, but agent frameworks only see ~188 tools - a silent loss of ~138 tools (42%).

## Investigation Summary

### Test Results

#### 1. Basic Loading (✅ PASS)
- `load_all_tools()` successfully loads **326 tools**
- All 326 tools have **unique names** (no duplicates)
- **No module import failures** - all 21 modules load successfully
- Deduplication logic in `merge_tool_lists()` works correctly

```
Total tools: 326
Unique names: 326
Duplicates: 0
```

#### 2. Google ADK Compatibility (⚠️ 27 FAILURES)
- **299 tools** pass Google ADK signature validation
- **27 tools** fail due to:
  - 21 tools with default parameter values
  - 4 tools with Union types
  - 2 tools with `Any` types

```
Valid tools: 299
Failed tools: 27
Success rate: 91.7%
```

#### 3. Optional Dependencies (⚠️ CRITICAL)
- **All 6 optional dependencies are MISSING** in test environment:
  - openpyxl (Excel)
  - python-docx (Word)
  - pypdf (PDF)
  - Pillow (Image)
  - diagrams (Diagrams)
  - python-pptx (PowerPoint)

```
✗ openpyxl             - Excel tools (MISSING)
✗ python-docx          - Word tools (MISSING)
✗ pypdf                - PDF tools (MISSING)
✗ Pillow               - Image tools (MISSING)
✗ diagrams             - Diagram tools (MISSING)
✗ python-pptx          - PowerPoint tools (MISSING)
```

However, **modules still import successfully** using try/except patterns:
```python
try:
    from openpyxl import load_workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
```

#### 4. Runtime Availability (📊 68 TOOLS AFFECTED)
Source code analysis shows:
- **258 tools** are fully available at runtime
- **68 tools** contain references to missing dependencies
- These tools will raise `ImportError` when called, but are still loadable

```
Available tools: 258
Unavailable tools (missing deps): 68
```

## Root Cause Analysis

### Why ~188 Tools Instead of 326?

The math:
- 326 total tools
- -27 tools (Google ADK incompatible)
- -??? more unidentified issues
= ~188-200 visible tools

### Likely Causes

1. **Google ADK Violations (27 tools lost)**
   - Functions with default parameters
   - Functions with Union types
   - Functions with Any types
   - **Impact**: Agent frameworks silently skip these during registration

2. **Agent Framework Filtering (Unknown number lost)**
   - Some frameworks may filter out tools based on:
     - Complex return types
     - Too many parameters
     - Docstring quality
     - Module path patterns

3. **Deferred Dependency Issues (Potential)**
   - While modules import successfully, agent frameworks might:
     - Try to instantiate/validate functions at registration time
     - Perform deeper introspection that triggers imports
     - Pre-validate that all type hints are resolvable

## Specific Violations Found

### Tools with Default Values (21 tools)
```
network.http_client.http_request: headers=None
network.dns.check_port_open: timeout=5
utilities.debugging.inspect_function_signature: module_name=None
utilities.debugging.format_exception_details: exception_info=None
system.shell.execute_shell_command: timeout=30
... and 16 more
```

### Tools with Union Types (4 tools)
```
file_system.editor.file_editor: kwargs: Union[str, int, bool]
utilities.timing.sleep_seconds: seconds: Union[int, float]
utilities.timing.sleep_milliseconds: milliseconds: Union[int, float]
utilities.timing.precise_sleep: seconds: Union[int, float]
```

### Tools with Any Type (2 tools)
```
utilities.debugging.validate_function_call: arguments: dict[str, Any]
utilities.debugging.trace_variable_changes: initial_value: Any
```

## Recommendations

### Priority 1: Fix Google ADK Violations (27 tools)

1. **Remove default parameters**
   - Convert all functions with defaults to require explicit values
   - Example: `timeout=30` → `timeout: int` (no default)

2. **Replace Union types**
   - Create separate functions for different types, OR
   - Use only the most common type (e.g., `float` for numeric values)

3. **Replace Any types**
   - Use specific types like `dict[str, str]` or `dict[str, object]`
   - Consider using JSON string representation for complex data

### Priority 2: Investigation

1. **Test with actual agent frameworks**
   - Google ADK
   - Strands Agents
   - LangChain
   - Identify which frameworks cause ~138 tool loss

2. **Enable debug logging**
   - Add logging to see which tools are being skipped
   - Capture warnings/errors during tool registration

3. **Check framework documentation**
   - Review tool registration requirements
   - Look for known limitations on tool counts
   - Check for naming conventions or patterns

### Priority 3: Documentation

1. **Document optional dependencies**
   - Clearly state which tools require which packages
   - Provide installation instructions per module
   - Consider creating "profiles" (e.g., `pip install basic-open-agent-tools[office]`)

2. **Add tool availability checking**
   ```python
   def get_available_tools() -> dict[str, bool]:
       """Check which tool categories are available."""
       return {
           'excel': HAS_OPENPYXL,
           'word': HAS_DOCX,
           'pdf': HAS_PYPDF,
           # ...
       }
   ```

## Test Scripts Created

1. `test_tool_introspection.py` - Basic introspection tests
2. `test_agent_conversion.py` - Google ADK compatibility testing
3. `test_import_failures.py` - Dependency availability testing
4. `test_runtime_failures.py` - Runtime tool availability
5. `test_import_error.py` - Module-level import testing

## Next Steps

1. Fix the 27 Google ADK violations (highest priority)
2. Test with actual agent framework to confirm ~188 tool count
3. Add framework-specific compatibility testing
4. Consider adding a tool validation utility:
   ```python
   boat.validate_tools_for_framework('google_adk')
   ```

## Appendix: Tool Count by Module

```
archive             :   9 tools
color               :  14 tools
crypto              :  14 tools
data                :  23 tools
datetime            :  40 tools
diagrams            :  16 tools
excel               :  24 tools
file_system         :  19 tools
html                :  17 tools
image               :  12 tools
logging             :   5 tools
markdown            :  12 tools
network             :   4 tools
pdf                 :  20 tools
powerpoint          :  10 tools
system              :  19 tools
text                :  10 tools
todo                :   8 tools
utilities           :   8 tools
word                :  18 tools
xml                 :  24 tools
----------------------------
Total               : 326 tools
```
