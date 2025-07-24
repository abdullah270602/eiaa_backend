# Template System Testing

Comprehensive test suite for the template processing system with parallel execution capabilities.

## Quick Start

### Prerequisites
```bash
# Install test dependencies
uv sync --extra test
```

### Running Tests

**Parallel Testing (Recommended)**
```bash
# Run all tests with default settings
uv run python tests/test_parallel.py

# Custom test directory and concurrency
uv run python tests/test_parallel.py test_files 1

# Use concurrency=1 for reliable results
```

**Quick Testing**
```bash
# Run subset of priority tests
uv run python tests/test_quick.py
```

## Test Coverage

- **18 test files** across 4 template types
- **23 total test cases** (standard + forced detection)
- **Template types**: Customer, Product, Audit Trail, Supplier
- **File formats**: CSV and Excel (.xlsx)

## Configuration

Edit `tests/config.py` to customize:
- Server URL
- Concurrency limits
- Timeout settings
- Test file patterns

## Output

Tests generate detailed reports in `test_results/`:
- JSON results with full metadata
- CSV summary for analysis
- Console output with accuracy metrics

## Troubleshooting

- **Connection errors**: Ensure server is running
- **Timeout issues**: Reduce concurrency or increase timeout
- **Failed tests**: Check server logs for processing errors
