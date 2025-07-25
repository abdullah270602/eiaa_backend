# 🧠 EIAA — Excel Import Autonomous Agent

**EIAA** is an AI-powered backend service that intelligently maps and transforms Excel/CSV files to multiple [Sage 50](https://www.sage.com/en-gb/products/sage-50cloud/) template formats using advanced Large Language Model (LLM) technology and intelligent template detection.

> 💡 **Perfect for** accounting teams, data entry workflows, ERP migrations, and automated data transformation pipelines.

---

## 🚀 Key Features

### 🎯 **Intelligent Template Detection**
- **Auto-detection** of 6 Sage 50 template types: Customer, Product, Audit Trail, Supplier, Nominal Record, and Stock Transactions
- **Rule-based** + **LLM-powered** detection for maximum accuracy
- **Confidence scoring** to ensure reliable template identification
- **Manual override** option for forcing specific template types

### 🧠 **AI-Powered Column Mapping**
- **Semantic mapping** using DeepSeek AI (e.g., `"Phone"` → `"Telephone Number"`)
- **Template-specific prompts** with hundreds of mapping examples
- **Context-aware** mapping based on sample data analysis
- **Missing field detection** for required columns

### 📊 **Multi-Format Support**
- **CSV files** with automatic delimiter detection
- **Excel files** (.xlsx/.xls) with robust parsing
- **Preview analysis** for improved mapping accuracy
- **Same-format output** (CSV→CSV, Excel→Excel)

### ⚡ **Production-Ready API**
- **FastAPI** framework with automatic documentation
- **Streaming responses** for large file handling
- **Comprehensive metadata** in response headers
- **CORS support** for frontend integration
- **Error handling** with detailed feedback

### 🧪 **Testing & Quality**
- **Comprehensive test suite** with 26+ test files
- **Parallel testing** capabilities
- **Confidence threshold** validation
- **Template-specific test scenarios**

---

## 📁 Supported Template Types

| Template Type | Purpose | Key Fields | Use Case |
|---------------|---------|------------|----------|
| **Customer** | Customer/Account records | Account Reference, Name, Contact Info, Financial Terms | CRM imports, customer onboarding |
| **Product** | Product/Stock records | Stock Code, Description, Pricing, Inventory | Inventory management, catalog imports |
| **Audit Trail** | Transaction records | Transaction Type, Amounts, Dates, References | Financial auditing, transaction imports |
| **Supplier** | Supplier/Vendor records | Supplier Code, Contact Info, Payment Terms | Vendor management, procurement |
| **Nominal Record** | Chart of accounts | Account Reference, Budget Data, Historical Data | Financial planning, budget imports |
| **Stock Transactions** | Stock movements/transactions | Type, Stock Code, Date, Quantity, Prices | Inventory tracking, stock movements |

---

## 📦 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/abdullah270602/eiaa_backend.git
cd eiaa_backend
```

### 2. Install Dependencies (using UV - recommended)

```bash
# Install UV package manager (if not installed)
pip install uv

# Install project dependencies
uv sync
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
```

### 4. Run the Application

```bash
# Using UV
uv run uvicorn main:app --reload --port 8000

# Or traditional method
uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`

---

## 🛠 Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **API Framework** | FastAPI | ≥0.115.14 | High-performance REST API |
| **Data Processing** | Pandas | ≥2.3.1 | Excel/CSV parsing & transformation |
| **AI Integration** | OpenAI SDK | ≥1.95.1 | DeepSeek LLM integration |
| **File Handling** | openpyxl, xlrd | Latest | Excel file processing |
| **Environment** | Python | ≥3.13 | Core runtime |
| **Package Manager** | UV | Latest | Fast dependency management |

---

## 📚 API Endpoints

### Upload and Process File
```http
POST /upload/
```
**Description**: Upload and automatically process CSV/Excel files with intelligent template detection.

**Parameters**:
- `file`: Multipart file upload (CSV, .xlsx, .xls)
- `force_template` (optional): Manual template selection (`customer`, `product`, `audit_trail`, `supplier`, `nominal_record`)

**Response Headers**:
- `X-Processing-Result`: Complete processing metadata (JSON)
- `X-Template-Type`: Detected template type
- `X-Template-Confidence`: Detection confidence score

### Get Available Templates
```http
GET /upload/templates
```
**Description**: Retrieve information about all supported template types and their configurations.

### API Documentation
- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | ✅ Yes | - |
| `DEEPSEEK_API_BASE_URL` | DeepSeek API endpoint | ✅ Yes | `https://api.deepseek.com` |

### Supported File Formats

- **CSV**: `.csv` files with automatic delimiter detection
- **Excel**: `.xlsx` and `.xls` formats with robust parsing

---

## 🧪 Testing

### Run Test Suite

```bash
# Run parallel tests
uv run python tests/test_parallel.py

# Run with specific configuration
cd tests && python test_parallel.py
```

### Test Files Structure
The project includes 26+ test files covering various scenarios:
- Complete data scenarios
- Missing required fields
- Alternative column naming
- Different data formats
- Edge cases and error handling

---

## 🏗 Project Architecture

```
app/
├── routes/
│   └── upload.py              # API endpoints
├── services/
│   ├── unified_processing_service.py    # Main orchestration
│   ├── template_detection_agent.py     # Template detection logic
│   ├── dynamic_mapping_agent.py        # AI-powered column mapping
│   ├── template_manager.py             # Template configuration
│   ├── formatter.py                    # Data transformation
│   ├── file_utils.py                   # File processing utilities
│   └── prompts.py                      # AI prompt templates
templates/                              # Sage 50 template files
test_files/                            # Comprehensive test dataset
tests/                                 # Test suite and utilities
```

---

## 🚀 Advanced Features

### Template Detection Logic
1. **Rule-based detection** using key column indicators
2. **LLM fallback** for ambiguous cases
3. **Confidence scoring** with threshold validation
4. **Manual override** for specific use cases

### AI-Powered Mapping
- Template-specific prompts with 100+ mapping examples
- Semantic understanding of column relationships
- Context-aware mapping using sample data
- Intelligent handling of missing required fields

### Error Handling
- Comprehensive error messages
- Fallback mechanisms for failed operations
- Detailed logging for debugging
- Graceful degradation for edge cases


