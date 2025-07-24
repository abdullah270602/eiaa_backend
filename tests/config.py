# Configuration constants for template system testing

# Server Configuration
# BASE_URL = "http://localhost:8000"
BASE_URL = "https://api.eiaa.lab47.xyz"

UPLOAD_ENDPOINT = "/upload/"

# Test Configuration
DEFAULT_TEST_DIR = "test_files"
MAX_CONCURRENT_REQUESTS = 1  # Set to 1 for reliable results
REQUEST_TIMEOUT = 60  # Timeout for each request in seconds

# File Configuration
SUPPORTED_EXTENSIONS = ('.csv', '.xlsx', '.xls')

# Template Configuration
TEMPLATE_KEYWORDS = {
    "customer": ["customer", "account"],
    "product": ["product", "stock", "item"],
    "audit_trail": ["audit", "trail", "transaction"],
    "supplier": ["supplier", "vendor", "purchase"],
    "nominal_record": ["nominal", "budget", "refn"]
}

# Test Modes
TEST_MODES = {
    "STANDARD": {"description": "Standard auto-detection"},
    "FORCED": {"force_template": True, "description": "Forced template detection"}
}

# Report Configuration
REPORT_OUTPUT_DIR = "test_results"
CONFIDENCE_THRESHOLDS = {
    "HIGH": 0.8,
    "MEDIUM": 0.6,
    "LOW": 0.0
}

# Path Detection
POSSIBLE_TEST_DIRS = [
    "test_files",           # From project root
    "../test_files",        # From tests/ directory
    "../../test_files",     # From nested directory
]
