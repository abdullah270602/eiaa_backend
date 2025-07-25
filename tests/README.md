# Template System Testing

Comprehensive test suite for the template processing system with parallel execution capabilities and template filtering.

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

# Test specific template type only
uv run python tests/test_parallel.py test_files nominal_record

# Combine template filter with concurrency
uv run python tests/test_parallel.py test_files customer 2

# Use concurrency=1 or 2 for most reliable results
```

**Template-Specific Testing**
```bash
# Test only customer templates
uv run python tests/test_parallel.py test_files customer

# Test only product templates  
uv run python tests/test_parallel.py test_files product

# Test only audit trail templates
uv run python tests/test_parallel.py test_files audit_trail

# Test only supplier templates
uv run python tests/test_parallel.py test_files supplier

# Test only nominal record templates
uv run python tests/test_parallel.py test_files nominal_record
```

## Test Coverage

- **21 test files** across 6 template types
- **26+ total test cases** (standard + forced detection)
- **Template types**: Customer, Product, Audit Trail, Supplier, Nominal Record, Stock Transactions
- **File formats**: CSV and Excel (.xlsx)

## Configuration

Edit `tests/config.py` to customize:
- Server URL
- Concurrency limits  
- Timeout settings
- Test file patterns
- Template keywords for filtering

## Template Filtering

The test system supports intelligent template filtering using keywords:

```python
TEMPLATE_KEYWORDS = {
    "customer": ["customer", "account"],
    "product": ["product", "stock", "item"],
    "audit_trail": ["audit", "trail", "transaction"],
    "supplier": ["supplier", "vendor", "purchase"],
    "nominal_record": ["nominal", "budget", "refn"]
}
```

## Output

Tests generate detailed reports in `test_results/`:
- JSON results with full metadata
- CSV summary for analysis
- Console output with accuracy metrics
- Template detection confidence scores
- Performance timing data

## Usage Examples

**Comprehensive Testing**
```bash
# Test all templates
uv run python tests/test_parallel.py test_files

# Results: ~35 tests across 5 template types
```

**Efficient Development Testing**
```bash
# Test only what you're working on
uv run python tests/test_parallel.py test_files nominal_record

# Results: ~8 tests for nominal record only
```

**Performance Testing**
```bash
# Test with higher concurrency
uv run python tests/test_parallel.py test_files 3

# Note: Use concurrency=1 or 2 for most reliable results
```

## Troubleshooting

- **Connection errors**: Ensure server is running at configured URL
- **Timeout issues**: Reduce concurrency or increase timeout in config
- **Failed tests**: Check server logs for processing errors
- **Template detection issues**: Verify template files exist in templates/ directory
- **No files found**: Check TEMPLATE_KEYWORDS match your test file names
