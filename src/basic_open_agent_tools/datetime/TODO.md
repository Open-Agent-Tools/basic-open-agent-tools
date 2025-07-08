# DateTime Tools TODO

## Module Overview

The DateTime module provides agent-friendly date and time utilities for parsing, formatting, calculations, and timezone handling. All functions follow Google ADK standards with JSON-serializable types only.

## Planned Functions (🚧 NEXT PRIORITY)

### Core Date/Time Operations (`operations.py`)
- [ ] `parse_date_string(date_string: str, format_string: str) -> str`
- [ ] `format_date(date_string: str, input_format: str, output_format: str) -> str`
- [ ] `get_current_datetime(timezone: str) -> str`
- [ ] `get_current_date(timezone: str) -> str`
- [ ] `get_current_time(timezone: str) -> str`
- [ ] `convert_timezone(datetime_string: str, from_timezone: str, to_timezone: str) -> str`

### Date/Time Calculations (`calculations.py`)
- [ ] `add_days(date_string: str, days: int, format_string: str) -> str`
- [ ] `subtract_days(date_string: str, days: int, format_string: str) -> str`
- [ ] `add_hours(datetime_string: str, hours: int, format_string: str) -> str`
- [ ] `subtract_hours(datetime_string: str, hours: int, format_string: str) -> str`
- [ ] `calculate_date_difference(date1: str, date2: str, format_string: str, unit: str) -> int`
- [ ] `calculate_time_difference(time1: str, time2: str, format_string: str, unit: str) -> int`

### Date/Time Validation (`validation.py`)
- [ ] `is_valid_date(date_string: str, format_string: str) -> bool`
- [ ] `is_valid_time(time_string: str, format_string: str) -> bool`
- [ ] `is_valid_datetime(datetime_string: str, format_string: str) -> bool`
- [ ] `is_valid_timezone(timezone_string: str) -> bool`

### Formatting and Parsing (`formatting.py`)
- [ ] `format_date_human_readable(date_string: str, format_string: str) -> str`
- [ ] `format_time_human_readable(time_string: str, format_string: str) -> str`
- [ ] `parse_natural_date(natural_string: str) -> str`
- [ ] `format_duration(seconds: int, format_type: str) -> str`
- [ ] `parse_duration_string(duration_string: str) -> int`

### Timezone Utilities (`timezone.py`)
- [ ] `get_timezone_list() -> List[str]`
- [ ] `get_timezone_offset(timezone: str) -> str`
- [ ] `is_daylight_saving_time(datetime_string: str, timezone: str) -> bool`
- [ ] `get_local_timezone() -> str`

## Design Principles

### Google ADK Compliance
- **JSON-Serializable Types**: All functions use str, int, bool, List[str] only
- **No Default Parameters**: All parameters explicitly required
- **Consistent Returns**: Standardized return formats (ISO strings, integers)
- **Clear Error Handling**: Descriptive exceptions for invalid inputs

### Function Signature Examples
```python
def parse_date_string(date_string: str, format_string: str) -> str:
    """Parse a date string using the specified format and return ISO date.
    
    Args:
        date_string: The date string to parse (e.g., "2023-12-25")
        format_string: The format pattern (e.g., "%Y-%m-%d")
        
    Returns:
        ISO formatted date string (YYYY-MM-DD)
        
    Raises:
        ValueError: If date_string cannot be parsed with format_string
        TypeError: If arguments are not strings
    """

def calculate_date_difference(date1: str, date2: str, format_string: str, unit: str) -> int:
    """Calculate the difference between two dates in specified units.
    
    Args:
        date1: First date string
        date2: Second date string  
        format_string: Format pattern for both dates
        unit: Unit for difference ("days", "weeks", "months", "years")
        
    Returns:
        Integer difference in specified units (positive if date1 > date2)
        
    Raises:
        ValueError: If dates cannot be parsed or unit is invalid
    """
```

## Implementation Standards

### Error Handling
- Use `DateTimeError` custom exception for all date/time related errors
- Validate timezone strings against standard timezone database
- Handle edge cases (leap years, DST transitions, invalid dates)
- Provide clear error messages for agent understanding

### Testing Requirements
- Unit tests for all functions with edge cases
- Google ADK agent evaluation tests
- Cross-platform compatibility testing
- Timezone database validation tests
- Performance tests for bulk operations

### Documentation
- Comprehensive docstrings with agent framework examples
- Clear parameter descriptions and return value formats
- Usage examples for common date/time operations
- Error handling documentation for agents

## Module Structure
```
src/basic_open_agent_tools/datetime/
├── __init__.py           # Module exports
├── operations.py         # Core date/time operations
├── calculations.py       # Date/time arithmetic
├── validation.py         # Date/time validation
├── formatting.py         # Formatting and parsing utilities
└── timezone.py          # Timezone utilities
```

## Dependencies
- Python standard library `datetime` module
- Python standard library `zoneinfo` module (Python 3.9+)
- Fallback to `pytz` for older Python versions (optional dependency)

## Agent Integration
Functions will be available through helper functions:
```python
import basic_open_agent_tools as boat

# Load datetime tools
datetime_tools = boat.load_all_datetime_tools()

# Merge with other tools
all_tools = boat.merge_tool_lists(
    boat.load_all_filesystem_tools(),
    boat.load_all_text_tools(),
    boat.load_all_data_tools(),
    datetime_tools
)
```

## Development Priority
**Status**: 🚧 **NEXT PRIORITY** - Immediate implementation target
**Target**: 20+ agent-friendly date/time functions
**Timeline**: Implementation phase following current v0.8.1 release

---

**Last Updated**: v0.8.1 (2025-07-08) - Module planning and design