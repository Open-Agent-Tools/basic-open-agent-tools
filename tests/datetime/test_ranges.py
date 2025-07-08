"""Tests for datetime ranges module."""

import pytest

from src.basic_open_agent_tools.datetime.ranges import (
    calculate_days_between,
    get_business_days_in_range,
    get_date_range,
    get_days_ago,
    get_last_business_day,
    get_month_range,
    get_months_ago,
    get_quarter_dates,
    get_year_to_date_range,
    is_date_in_range,
)


class TestGetDateRange:
    """Test get_date_range function."""

    def test_get_date_range_basic(self):
        """Test basic date range generation."""
        result = get_date_range("2025-01-01", "2025-01-03")
        expected = ["2025-01-01", "2025-01-02", "2025-01-03"]
        assert result == expected

    def test_get_date_range_single_day(self):
        """Test date range with same start and end date."""
        result = get_date_range("2025-01-01", "2025-01-01")
        assert result == ["2025-01-01"]

    def test_get_date_range_month_boundary(self):
        """Test date range across month boundary."""
        result = get_date_range("2025-01-30", "2025-02-02")
        expected = ["2025-01-30", "2025-01-31", "2025-02-01", "2025-02-02"]
        assert result == expected

    def test_get_date_range_year_boundary(self):
        """Test date range across year boundary."""
        result = get_date_range("2024-12-30", "2025-01-02")
        expected = ["2024-12-30", "2024-12-31", "2025-01-01", "2025-01-02"]
        assert result == expected

    def test_get_date_range_invalid_order(self):
        """Test get_date_range with start_date after end_date."""
        with pytest.raises(
            ValueError, match="start_date must be less than or equal to end_date"
        ):
            get_date_range("2025-01-02", "2025-01-01")

    def test_get_date_range_invalid_dates(self):
        """Test get_date_range with invalid date formats."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_date_range("invalid", "2025-01-01")

    def test_get_date_range_non_string_input(self):
        """Test get_date_range with non-string input."""
        with pytest.raises(TypeError, match="start_date must be a string"):
            get_date_range(123, "2025-01-01")


class TestGetQuarterDates:
    """Test get_quarter_dates function."""

    def test_get_quarter_dates_q1(self):
        """Test Q1 dates."""
        result = get_quarter_dates(2025, 1)
        expected = {"start": "2025-01-01", "end": "2025-03-31"}
        assert result == expected

    def test_get_quarter_dates_q2(self):
        """Test Q2 dates."""
        result = get_quarter_dates(2025, 2)
        expected = {"start": "2025-04-01", "end": "2025-06-30"}
        assert result == expected

    def test_get_quarter_dates_q3(self):
        """Test Q3 dates."""
        result = get_quarter_dates(2025, 3)
        expected = {"start": "2025-07-01", "end": "2025-09-30"}
        assert result == expected

    def test_get_quarter_dates_q4(self):
        """Test Q4 dates."""
        result = get_quarter_dates(2025, 4)
        expected = {"start": "2025-10-01", "end": "2025-12-31"}
        assert result == expected

    def test_get_quarter_dates_leap_year(self):
        """Test Q1 in leap year."""
        result = get_quarter_dates(2024, 1)
        expected = {"start": "2024-01-01", "end": "2024-03-31"}
        assert result == expected

    def test_get_quarter_dates_invalid_quarter(self):
        """Test get_quarter_dates with invalid quarter."""
        with pytest.raises(ValueError, match="quarter must be 1, 2, 3, or 4"):
            get_quarter_dates(2025, 5)

    def test_get_quarter_dates_non_integer_input(self):
        """Test get_quarter_dates with non-integer input."""
        with pytest.raises(TypeError, match="year must be an integer"):
            get_quarter_dates("2025", 1)


class TestGetYearToDateRange:
    """Test get_year_to_date_range function."""

    def test_get_year_to_date_range_basic(self):
        """Test basic year-to-date range."""
        result = get_year_to_date_range("2025-06-30")
        expected = {"start": "2025-01-01", "end": "2025-06-30"}
        assert result == expected

    def test_get_year_to_date_range_january(self):
        """Test year-to-date range in January."""
        result = get_year_to_date_range("2025-01-15")
        expected = {"start": "2025-01-01", "end": "2025-01-15"}
        assert result == expected

    def test_get_year_to_date_range_december(self):
        """Test year-to-date range in December."""
        result = get_year_to_date_range("2025-12-31")
        expected = {"start": "2025-01-01", "end": "2025-12-31"}
        assert result == expected

    def test_get_year_to_date_range_invalid_date(self):
        """Test get_year_to_date_range with invalid date."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_year_to_date_range("invalid")

    def test_get_year_to_date_range_non_string_input(self):
        """Test get_year_to_date_range with non-string input."""
        with pytest.raises(TypeError, match="reference_date must be a string"):
            get_year_to_date_range(123)


class TestGetDaysAgo:
    """Test get_days_ago function."""

    def test_get_days_ago_basic(self):
        """Test basic days ago calculation."""
        result = get_days_ago(7, "2025-01-08")
        assert result == "2025-01-01"

    def test_get_days_ago_90_days(self):
        """Test 90 days ago calculation."""
        result = get_days_ago(90, "2025-04-10")
        assert result == "2025-01-10"

    def test_get_days_ago_zero_days(self):
        """Test zero days ago."""
        result = get_days_ago(0, "2025-01-01")
        assert result == "2025-01-01"

    def test_get_days_ago_month_boundary(self):
        """Test days ago across month boundary."""
        result = get_days_ago(5, "2025-02-03")
        assert result == "2025-01-29"

    def test_get_days_ago_year_boundary(self):
        """Test days ago across year boundary."""
        result = get_days_ago(10, "2025-01-05")
        assert result == "2024-12-26"

    def test_get_days_ago_negative_days(self):
        """Test get_days_ago with negative days."""
        with pytest.raises(ValueError, match="days must be positive"):
            get_days_ago(-7, "2025-01-01")

    def test_get_days_ago_non_integer_days(self):
        """Test get_days_ago with non-integer days."""
        with pytest.raises(TypeError, match="days must be an integer"):
            get_days_ago("7", "2025-01-01")


class TestGetMonthsAgo:
    """Test get_months_ago function."""

    def test_get_months_ago_basic(self):
        """Test basic months ago calculation."""
        result = get_months_ago(1, "2025-02-15")
        assert result == "2025-01-15"

    def test_get_months_ago_12_months(self):
        """Test 12 months ago calculation."""
        result = get_months_ago(12, "2025-07-08")
        assert result == "2024-07-08"

    def test_get_months_ago_year_boundary(self):
        """Test months ago across year boundary."""
        result = get_months_ago(3, "2025-02-15")
        assert result == "2024-11-15"

    def test_get_months_ago_day_overflow(self):
        """Test months ago with day overflow (Jan 31 -> Feb 31)."""
        result = get_months_ago(1, "2025-01-31")
        assert result == "2024-12-31"  # Should use last day of target month

    def test_get_months_ago_leap_year_handling(self):
        """Test months ago with leap year handling."""
        result = get_months_ago(1, "2024-03-29")
        assert result == "2024-02-29"  # Feb 29 exists in 2024

    def test_get_months_ago_zero_months(self):
        """Test zero months ago."""
        result = get_months_ago(0, "2025-01-15")
        assert result == "2025-01-15"

    def test_get_months_ago_negative_months(self):
        """Test get_months_ago with negative months."""
        with pytest.raises(ValueError, match="months must be positive"):
            get_months_ago(-1, "2025-01-01")

    def test_get_months_ago_non_integer_months(self):
        """Test get_months_ago with non-integer months."""
        with pytest.raises(TypeError, match="months must be an integer"):
            get_months_ago("1", "2025-01-01")


class TestGetLastBusinessDay:
    """Test get_last_business_day function."""

    def test_get_last_business_day_monday(self):
        """Test last business day when reference is Monday."""
        result = get_last_business_day("2025-07-07")  # Monday
        assert result == "2025-07-07"

    def test_get_last_business_day_friday(self):
        """Test last business day when reference is Friday."""
        result = get_last_business_day("2025-07-04")  # Friday
        assert result == "2025-07-04"

    def test_get_last_business_day_saturday(self):
        """Test last business day when reference is Saturday."""
        result = get_last_business_day("2025-07-05")  # Saturday
        assert result == "2025-07-04"  # Previous Friday

    def test_get_last_business_day_sunday(self):
        """Test last business day when reference is Sunday."""
        result = get_last_business_day("2025-07-06")  # Sunday
        assert result == "2025-07-04"  # Previous Friday

    def test_get_last_business_day_invalid_date(self):
        """Test get_last_business_day with invalid date."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_last_business_day("invalid")

    def test_get_last_business_day_non_string_input(self):
        """Test get_last_business_day with non-string input."""
        with pytest.raises(TypeError, match="reference_date must be a string"):
            get_last_business_day(123)


class TestIsDateInRange:
    """Test is_date_in_range function."""

    def test_is_date_in_range_within_range(self):
        """Test date within range."""
        result = is_date_in_range("2025-05-15", "2025-05-01", "2025-05-31")
        assert result is True

    def test_is_date_in_range_start_boundary(self):
        """Test date at start boundary."""
        result = is_date_in_range("2025-05-01", "2025-05-01", "2025-05-31")
        assert result is True

    def test_is_date_in_range_end_boundary(self):
        """Test date at end boundary."""
        result = is_date_in_range("2025-05-31", "2025-05-01", "2025-05-31")
        assert result is True

    def test_is_date_in_range_before_range(self):
        """Test date before range."""
        result = is_date_in_range("2025-04-30", "2025-05-01", "2025-05-31")
        assert result is False

    def test_is_date_in_range_after_range(self):
        """Test date after range."""
        result = is_date_in_range("2025-06-01", "2025-05-01", "2025-05-31")
        assert result is False

    def test_is_date_in_range_invalid_date(self):
        """Test is_date_in_range with invalid date."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            is_date_in_range("invalid", "2025-05-01", "2025-05-31")

    def test_is_date_in_range_non_string_input(self):
        """Test is_date_in_range with non-string input."""
        with pytest.raises(TypeError, match="check_date must be a string"):
            is_date_in_range(123, "2025-05-01", "2025-05-31")


class TestGetMonthRange:
    """Test get_month_range function."""

    def test_get_month_range_january(self):
        """Test January month range."""
        result = get_month_range(2025, 1)
        expected = {"start": "2025-01-01", "end": "2025-01-31"}
        assert result == expected

    def test_get_month_range_february_non_leap(self):
        """Test February in non-leap year."""
        result = get_month_range(2025, 2)
        expected = {"start": "2025-02-01", "end": "2025-02-28"}
        assert result == expected

    def test_get_month_range_february_leap(self):
        """Test February in leap year."""
        result = get_month_range(2024, 2)
        expected = {"start": "2024-02-01", "end": "2024-02-29"}
        assert result == expected

    def test_get_month_range_april(self):
        """Test April (30 days)."""
        result = get_month_range(2025, 4)
        expected = {"start": "2025-04-01", "end": "2025-04-30"}
        assert result == expected

    def test_get_month_range_december(self):
        """Test December."""
        result = get_month_range(2025, 12)
        expected = {"start": "2025-12-01", "end": "2025-12-31"}
        assert result == expected

    def test_get_month_range_invalid_month(self):
        """Test get_month_range with invalid month."""
        with pytest.raises(ValueError, match="month must be between 1 and 12"):
            get_month_range(2025, 13)

    def test_get_month_range_non_integer_input(self):
        """Test get_month_range with non-integer input."""
        with pytest.raises(TypeError, match="year must be an integer"):
            get_month_range("2025", 1)


class TestCalculateDaysBetween:
    """Test calculate_days_between function."""

    def test_calculate_days_between_basic(self):
        """Test basic days between calculation."""
        result = calculate_days_between("2025-01-01", "2025-01-31")
        assert result == 30

    def test_calculate_days_between_same_date(self):
        """Test days between same date."""
        result = calculate_days_between("2025-01-01", "2025-01-01")
        assert result == 0

    def test_calculate_days_between_negative(self):
        """Test days between with end before start."""
        result = calculate_days_between("2025-01-31", "2025-01-01")
        assert result == -30

    def test_calculate_days_between_year_boundary(self):
        """Test days between across year boundary."""
        result = calculate_days_between("2024-12-25", "2025-01-05")
        assert result == 11

    def test_calculate_days_between_leap_year(self):
        """Test days between in leap year."""
        result = calculate_days_between("2024-02-28", "2024-03-01")
        assert result == 2  # Includes Feb 29

    def test_calculate_days_between_invalid_date(self):
        """Test calculate_days_between with invalid date."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            calculate_days_between("invalid", "2025-01-01")

    def test_calculate_days_between_non_string_input(self):
        """Test calculate_days_between with non-string input."""
        with pytest.raises(TypeError, match="start_date must be a string"):
            calculate_days_between(123, "2025-01-01")


class TestGetBusinessDaysInRange:
    """Test get_business_days_in_range function."""

    def test_get_business_days_in_range_full_week(self):
        """Test business days in full work week (Mon-Fri)."""
        result = get_business_days_in_range("2025-07-07", "2025-07-11")  # Mon-Fri
        assert result == 5

    def test_get_business_days_in_range_with_weekend(self):
        """Test business days with weekend included."""
        result = get_business_days_in_range("2025-07-05", "2025-07-07")  # Sat-Mon
        assert result == 1  # Only Monday

    def test_get_business_days_in_range_weekend_only(self):
        """Test business days in weekend only."""
        result = get_business_days_in_range("2025-07-05", "2025-07-06")  # Sat-Sun
        assert result == 0

    def test_get_business_days_in_range_single_business_day(self):
        """Test single business day."""
        result = get_business_days_in_range("2025-07-07", "2025-07-07")  # Monday
        assert result == 1

    def test_get_business_days_in_range_single_weekend_day(self):
        """Test single weekend day."""
        result = get_business_days_in_range("2025-07-05", "2025-07-05")  # Saturday
        assert result == 0

    def test_get_business_days_in_range_two_weeks(self):
        """Test business days in two weeks."""
        result = get_business_days_in_range(
            "2025-07-07", "2025-07-18"
        )  # Mon-Fri, Mon-Fri
        assert result == 10

    def test_get_business_days_in_range_invalid_order(self):
        """Test get_business_days_in_range with start after end."""
        with pytest.raises(
            ValueError, match="start_date must be less than or equal to end_date"
        ):
            get_business_days_in_range("2025-07-08", "2025-07-07")

    def test_get_business_days_in_range_invalid_date(self):
        """Test get_business_days_in_range with invalid date."""
        with pytest.raises(ValueError, match="Invalid ISO date format"):
            get_business_days_in_range("invalid", "2025-07-07")

    def test_get_business_days_in_range_non_string_input(self):
        """Test get_business_days_in_range with non-string input."""
        with pytest.raises(TypeError, match="start_date must be a string"):
            get_business_days_in_range(123, "2025-07-07")


class TestDateTimeRangesIntegration:
    """Integration tests for datetime ranges operations."""

    def test_quarter_to_date_range_conversion(self):
        """Test converting quarter dates to date range."""
        quarter_dates = get_quarter_dates(2025, 1)
        date_range = get_date_range(quarter_dates["start"], quarter_dates["end"])

        assert len(date_range) == 90  # Q1 2025 has 90 days
        assert date_range[0] == "2025-01-01"
        assert date_range[-1] == "2025-03-31"

    def test_month_range_to_business_days(self):
        """Test counting business days in month range."""
        month_range = get_month_range(2025, 7)  # July 2025
        business_days = get_business_days_in_range(
            month_range["start"], month_range["end"]
        )

        assert business_days == 23  # July 2025 has 23 business days

    def test_days_ago_in_range_check(self):
        """Test checking if days ago date is in range."""
        reference_date = "2025-07-08"
        days_ago_30 = get_days_ago(30, reference_date)
        ytd_range = get_year_to_date_range(reference_date)

        result = is_date_in_range(days_ago_30, ytd_range["start"], ytd_range["end"])
        assert result is True

    def test_business_day_range_calculation(self):
        """Test business day calculation with last business day."""
        sunday = "2025-07-06"
        last_biz_day = get_last_business_day(sunday)
        days_ago_7 = get_days_ago(7, sunday)

        business_days = get_business_days_in_range(days_ago_7, last_biz_day)
        assert business_days == 5  # One work week
