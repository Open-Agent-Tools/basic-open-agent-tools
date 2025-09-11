# Utilities Tools Status

## Overview
Development utilities, logging, caching, and helper functions for AI agents.

## Current Status
**📋 PLANNED MODULE** - Not yet implemented

This module is planned for future development to provide essential development and operational utilities for AI agents.

## Planned Features
- ✅ **Planned**: Simple logging utilities
- ✅ **Planned**: Basic caching mechanisms
- ✅ **Planned**: Retry and backoff utilities
- ✅ **Planned**: Rate limiting helpers
- ✅ **Planned**: Simple debugging tools
- ✅ **Planned**: Performance timing utilities
- ✅ **Planned**: Data structure helpers

## Design Considerations for Agent Tools
- Simple, lightweight utility functions
- Functions designed as individual agent tools
- Memory-efficient operations
- Clear error messages and handling
- Thread-safe where applicable
- Consistent API design with other modules
- Functions suitable for agent framework integration
- **No complex framework dependencies** (keep utilities simple)
- **No persistent storage backends** (use simple in-memory solutions)
- Focus on common development patterns and needs

## Excluded from Utilities Module
- **Complex Logging Frameworks** - Advanced logging systems (use dedicated logging libraries)
- **Database Connections** - ORM, database abstraction (use specialized database tools)
- **Message Queues** - Complex messaging systems (use dedicated queue libraries)
- **Web Framework Utilities** - HTTP utilities, web helpers (use web frameworks)

## Planned Function Signatures

### Logging Utilities
- `setup_simple_logger(name: str, level: str) -> str` - Create basic logger configuration
- `log_info(message: str, logger_name: str) -> bool` - Log info message
- `log_error(message: str, logger_name: str) -> bool` - Log error message
- `log_debug(message: str, logger_name: str) -> bool` - Log debug message
- `get_log_level(logger_name: str) -> str` - Get current log level

### Caching Utilities
- `create_simple_cache(max_size: int) -> str` - Create in-memory cache
- `cache_get(cache_id: str, key: str) -> str` - Get value from cache
- `cache_set(cache_id: str, key: str, value: str, ttl: int) -> bool` - Set cache value with TTL
- `cache_delete(cache_id: str, key: str) -> bool` - Delete cache entry
- `cache_clear(cache_id: str) -> bool` - Clear entire cache

### Retry Utilities
- `retry_with_backoff(max_attempts: int, base_delay: float) -> Dict[str, str]` - Create retry configuration
- `should_retry(attempt: int, max_attempts: int) -> bool` - Check if should retry
- `calculate_backoff_delay(attempt: int, base_delay: float, max_delay: float) -> float` - Calculate delay

### Rate Limiting
- `create_rate_limiter(requests_per_second: float) -> str` - Create rate limiter
- `check_rate_limit(limiter_id: str) -> bool` - Check if request allowed
- `reset_rate_limiter(limiter_id: str) -> bool` - Reset rate limiter state

### Performance Timing
- `start_timer(timer_name: str) -> bool` - Start performance timer
- `stop_timer(timer_name: str) -> float` - Stop timer and get elapsed seconds
- `get_timer_stats(timer_name: str) -> Dict[str, float]` - Get timer statistics
- `clear_all_timers() -> bool` - Clear all performance timers

### Data Structure Helpers
- `deep_merge_dicts(dict1: Dict[str, str], dict2: Dict[str, str]) -> Dict[str, str]` - Merge dictionaries recursively
- `flatten_dict(nested_dict: Dict[str, str], separator: str) -> Dict[str, str]` - Flatten nested dictionary
- `chunk_list(items: List[str], chunk_size: int) -> List[List[str]]` - Split list into chunks
- `unique_list_preserve_order(items: List[str]) -> List[str]` - Remove duplicates while preserving order

### Debugging Utilities
- `get_function_info() -> Dict[str, str]` - Get information about calling function
- `format_exception(exception_obj: str) -> str` - Format exception for logging
- `get_memory_usage() -> Dict[str, int]` - Get current memory usage stats

## Security Features
- No persistent data storage (memory-only operations)
- Input validation for all utility functions
- Safe error handling with appropriate cleanup
- No external network dependencies
- Thread-safe implementations where needed

## Agent Integration
When implemented, will be compatible with:
- **Google ADK**: Direct function imports as tools
- **LangChain**: Wrappable with StructuredTool
- **Strands Agents**: Native @strands_tool decorator support
- **Custom Agents**: Simple function-based API

## Common Use Cases
- **Development**: Simple logging and debugging during agent development
- **Performance**: Time operations and monitor resource usage
- **Resilience**: Add retry logic and rate limiting to agent operations
- **Caching**: Simple in-memory caching for agent computations
- **Data Processing**: Common operations on data structures

## Implementation Priority
This module is planned for implementation last, as it provides supporting utilities for other modules and agent development.

**Estimated Functions**: 20-25 agent-ready tools with Google ADK compatibility
**Implementation Status**: Not yet started
**Target Version**: v1.4.0+