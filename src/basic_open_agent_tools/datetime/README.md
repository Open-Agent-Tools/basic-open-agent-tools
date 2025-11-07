# DateTime Tools Status

## Overview
Comprehensive date, time, and timezone utilities for AI agents.

## Current Status
All planned datetime modules have been implemented and tested:
- ✅ Date and time information extraction
- ✅ Timezone conversion and handling
- ✅ Date arithmetic and calculations
- ✅ Business day operations
- ✅ Date range generation and validation
- ✅ ISO format validation and parsing
- ✅ Advanced date/time operations
- ✅ Comprehensive validation functions

## Design Considerations for Agent Tools
- Timezone-aware datetime operations
- Functions designed as individual agent tools
- ISO 8601 standard compliance for date/time formats
- Clear error messages and handling
- Cross-timezone compatibility
- Consistent API design across modules
- Functions suitable for agent framework integration
- Clear function signatures optimized for AI tool usage
- Safe date parsing without execution risks
- Business calendar awareness (weekdays, holidays)
- **Focus on standard date/time operations** (no specialized calendars)
- **String-based inputs/outputs** for agent compatibility
- Support for common business scenarios
- Predictable behavior across timezones
- Memory-efficient date calculations

## Excluded from DateTime Module (Separate Module Considerations)
- **Complex Calendar Systems** - Lunar, Hebrew, Islamic calendars (specialized use cases)
- **Holiday Calculation** - Country-specific holiday calculations (region-specific data)
- **Advanced Scheduling** - Meeting scheduling, availability management (business logic)
- **Date Parsing Libraries** - Complex natural language date parsing (heavy ML dependencies)

## Function Signatures

### Current Date/Time
- `get_current_datetime(timezone: str) -> str` - Get current datetime in specified timezone
- `get_current_date(timezone: str) -> str` - Get current date in specified timezone
- `get_current_time(timezone: str) -> str` - Get current time in specified timezone

### Date Information
- `get_weekday_name(date_string: str) -> str` - Get day name (Monday, Tuesday, etc.)
- `get_month_name(date_string: str) -> str` - Get month name (January, February, etc.)
- `get_week_number(date_string: str) -> int` - Get ISO week number
- `get_day_of_year(date_string: str) -> int` - Get day number in year (1-366)
- `is_leap_year(year: int) -> bool` - Check if year is a leap year
- `get_days_in_month(year: int, month: int) -> int` - Get number of days in month

### Date/Time Validation
- `is_valid_iso_date(date_string: str) -> bool` - Validate ISO date format
- `is_valid_iso_time(time_string: str) -> bool` - Validate ISO time format
- `is_valid_iso_datetime(datetime_string: str) -> bool` - Validate ISO datetime format
- `is_valid_date_format(date_string: str, format_string: str) -> bool` - Validate custom date format
- `validate_date_range(date_string: str, min_date: str, max_date: str) -> bool` - Validate date within range
- `validate_datetime_range(datetime_string: str, min_datetime: str, max_datetime: str) -> bool` - Validate datetime within range

### Date Arithmetic
- `add_days(date_string: str, days: int) -> str` - Add days to date
- `subtract_days(date_string: str, days: int) -> str` - Subtract days from date
- `add_hours(datetime_string: str, hours: int) -> str` - Add hours to datetime
- `subtract_hours(datetime_string: str, hours: int) -> str` - Subtract hours from datetime
- `add_minutes(datetime_string: str, minutes: int) -> str` - Add minutes to datetime
- `subtract_minutes(datetime_string: str, minutes: int) -> str` - Subtract minutes from datetime
- `calculate_time_difference(time1: str, time2: str, unit: str) -> int` - Calculate difference between times

### Date Ranges
- `get_date_range(start_date: str, end_date: str) -> List[str]` - Generate list of dates in range
- `get_quarter_dates(year: int, quarter: int) -> Dict[str, str]` - Get quarter start/end dates
- `get_year_to_date_range(reference_date: str) -> Dict[str, str]` - Get year-to-date range
- `get_month_range(year: int, month: int) -> Dict[str, str]` - Get month start/end dates
- `calculate_days_between(start_date: str, end_date: str) -> int` - Count days between dates
- `is_date_in_range(check_date: str, start_date: str, end_date: str) -> bool` - Check if date is in range

### Relative Dates
- `get_days_ago(days: int, reference_date: str) -> str` - Get date N days ago
- `get_months_ago(months: int, reference_date: str) -> str` - Get date N months ago
- `is_future_date(date_string: str, reference_date: str) -> bool` - Check if date is in future
- `is_past_date(date_string: str, reference_date: str) -> bool` - Check if date is in past

### Business Days
- `get_next_business_day(date_string: str) -> str` - Get next weekday
- `get_last_business_day(reference_date: str) -> str` - Get previous weekday
- `is_business_day(date_string: str) -> bool` - Check if date is a weekday
- `get_business_days_in_range(start_date: str, end_date: str) -> int` - Count business days in range

### Timezone Operations
- `convert_timezone(datetime_string: str, from_timezone: str, to_timezone: str) -> str` - Convert between timezones
- `get_timezone_offset(timezone: str) -> str` - Get timezone offset from UTC
- `is_daylight_saving_time(datetime_string: str, timezone: str) -> bool` - Check if DST is active
- `is_valid_timezone(timezone_string: str) -> bool` - Validate timezone string

## Security Features
- No code execution or eval operations
- Input validation for all date/time strings
- Safe parsing with error handling
- Protection against malformed date inputs
- Timezone validation to prevent injection

## Performance Considerations
- Efficient datetime calculations using Python datetime module
- Memory-conscious operations for date ranges
- Optimized timezone handling with pytz
- Minimal object creation for string-based operations

## Agent Integration
Compatible with:
- **Google ADK**: Direct function imports as tools
- **LangChain**: Wrappable with StructuredTool
- **Strands Agents**: Native @strands_tool decorator support
- **Custom Agents**: Simple function-based API

## Example Usage

```python
import basic_open_agent_tools as boat

# Load datetime tools
datetime_tools = boat.load_all_datetime_tools()

# Individual function usage
from basic_open_agent_tools.datetime import get_current_date, add_days

# Get current date in specific timezone
today = get_current_date("America/New_York")

# Calculate future date
future_date = add_days(today, 30)
```

## Module Structure
- **operations.py** - Core date/time operations, validation, and parsing (15 functions)
- **formatting.py** - Human-readable date/time formatting (4 functions)
- **info.py** - Date/time information extraction (6 functions)
- **ranges.py** - Date range operations and calculations (10 functions)
- **business.py** - Business day operations (2 functions)
- **timezone.py** - Timezone conversion and handling (4 functions)
- **validation.py** - Date/time validation functions (5 functions)

## Common Use Cases
- **Scheduling**: Calculate meeting times across timezones
- **Reporting**: Generate date ranges for reports
- **Data Processing**: Validate and normalize date data
- **Business Logic**: Handle business day calculations
- **Time Tracking**: Calculate duration and differences
- **Data Analysis**: Extract date components for analysis

## Date Format Standards
- **ISO 8601 Compliance**: All functions use standard ISO formats
- **Date Format**: YYYY-MM-DD (e.g., "2025-09-11")
- **Time Format**: HH:MM:SS (e.g., "14:30:00")
- **DateTime Format**: YYYY-MM-DDTHH:MM:SS (e.g., "2025-09-11T14:30:00")
- **Timezone Format**: IANA timezone names (e.g., "America/New_York")

**Total Functions**: 42 agent-ready tools with Google ADK compatibility