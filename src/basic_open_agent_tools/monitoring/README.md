# Monitoring Tools

## Overview
Comprehensive monitoring, health checking, and performance profiling tools for AI agents with detailed analytics and benchmarking capabilities.

## Current Status
**✅ FULLY IMPLEMENTED MODULE** - 8 functions available

## Current Features
- ✅ **File Watching**: watch_file_changes, monitor_directory
- ✅ **Health Checks**: check_url_status, ping_host
- ✅ **Performance Monitoring**: monitor_function_performance, get_system_load_average
- ✅ **Code Profiling**: profile_code_execution, benchmark_disk_io

## Function Reference

### File System Monitoring
```python
watch_file_changes(file_path: str, check_interval: int = 1)
monitor_directory(directory_path: str, recursive: bool = True)
```

### Health Checking
```python
check_url_status(url: str, timeout: int = 10)
ping_host(hostname: str, count: int = 4)
```

### Performance Analysis (NEW)
```python
# System performance monitoring
monitor_function_performance(duration_seconds: int = 60)
get_system_load_average()

# Code execution profiling
profile_code_execution(code_snippet: str, iterations: int = 1)
benchmark_disk_io(file_path: str, data_size_kb: int = 1024)
```

## Key Features

### Advanced Performance Monitoring
- **System Metrics**: CPU, memory, disk usage over time
- **Load Average**: Unix-style load averages with per-core analysis
- **Code Profiling**: Execution time analysis with statistics
- **I/O Benchmarking**: Disk read/write performance measurement

### Comprehensive Analytics
- **Statistical Analysis**: Min, max, average calculations
- **Performance Trends**: Time-series data collection
- **Benchmark Comparisons**: Performance baseline establishment
- **Resource Monitoring**: Real-time system resource tracking

## Usage Examples

### System Performance Analysis
```python
# Monitor system for 30 seconds
perf_result = monitor_function_performance(30)

print(f"CPU Usage - Avg: {perf_result['cpu_usage_percent']['avg']:.1f}%")
print(f"Memory Usage - Max: {perf_result['memory_usage_percent']['max']:.1f}%")
print(f"Samples taken: {perf_result['samples_taken']}")
```

### Code Performance Profiling
```python
# Profile algorithm performance
code = """
numbers = list(range(1000))
result = sum(x*x for x in numbers if x % 2 == 0)
"""

profile_result = profile_code_execution(code, iterations=100)
print(f"Average execution: {profile_result['avg_execution_time_seconds']:.6f}s")
print(f"Executions per second: {profile_result['executions_per_second']}")
```

### Disk I/O Benchmarking
```python
# Benchmark storage performance
benchmark_result = benchmark_disk_io("test_file.tmp", 10240)  # 10MB test

print(f"Write speed: {benchmark_result['write_speed_mbps']:.1f} MB/s")
print(f"Read speed: {benchmark_result['read_speed_mbps']:.1f} MB/s")
print(f"Data integrity: {benchmark_result['data_integrity_verified']}")
```

### Load Average Analysis
```python
# Get system load information
load_result = get_system_load_average()

if load_result['load_average_available']:
    print(f"Load (1min): {load_result['load_1min']}")
    print(f"Load per core: {load_result['load_per_core_1min']:.2f}")
    print(f"System busy: {load_result['system_busy_1min']}")
else:
    print(f"CPU usage: {load_result['alternative_cpu_usage_percent']:.1f}%")
```

## Agent Integration

### Google ADK
```python
import basic_open_agent_tools as boat
monitoring_tools = boat.load_all_monitoring_tools()
agent = Agent(tools=monitoring_tools)
```

### Performance Monitoring Pipeline
```python
# Comprehensive system analysis
def analyze_system_performance():
    # Get baseline load
    load_info = get_system_load_average()

    # Monitor for extended period
    perf_data = monitor_function_performance(60)

    # Benchmark I/O
    io_bench = benchmark_disk_io("benchmark.tmp", 5120)

    return {
        "load_average": load_info,
        "performance_stats": perf_data,
        "io_performance": io_bench
    }
```

## Dependencies

### Required Dependencies
Performance monitoring requires psutil:
```bash
pip install basic-open-agent-tools[system]
```

### Optional Dependencies
- **psutil**: System monitoring and load average (required for performance tools)

## Performance Notes
- **Monitoring Overhead**: Minimal impact on system performance
- **Sampling Frequency**: Configurable intervals (default 2 seconds)
- **Memory Usage**: Efficient data collection with bounded memory
- **Cross-Platform**: Windows, macOS, Linux compatibility

## Security Features
- **Code Execution Safety**: Restricted namespace for profiling
- **File System Safety**: Temporary file cleanup
- **Resource Limits**: Bounded execution times and data sizes
- **Input Validation**: Comprehensive parameter checking

## Testing
Comprehensive test coverage for all monitoring functions, cross-platform compatibility, and performance accuracy validation.