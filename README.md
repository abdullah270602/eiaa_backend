# 🧠 EIAA — Excel Import Autonomous Agent

**EIAA** is an AI-powered backend service that intelligently maps and transforms 
Excel/CSV files to the [Sage 50](https://www.sage.com/en-gb/products/sage-50cloud/) 
customer import template format using advanced Large Language Model (LLM) technology.

> 💡 **Perfect for** accounting teams, data entry workflows, and ERP migrations.

---

## 🚀 Key Features

- **🎯 Smart Column Mapping** — AI-powered semantic mapping  
  (e.g., `"Phone"` → `"Telephone Number"`)
- **📊 Multi-Format Support** — Handles CSV and Excel (.xlsx/.xls) files
- **🔍 Intelligent Validation** — Auto-detects missing required fields  
  like `Account Reference`
- **👀 Preview Analysis** — Extracts and analyzes sample data for  
  improved accuracy
- **⚡ Clean API Response** — Consistent JSON feedback for seamless  
  frontend integration
- **📥 Ready-to-Use Output** — Download-ready formatted files  
  compatible with Sage 50

---

## 📦 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/eiaa-backend.git
cd eiaa-backend
```

### 2. Set Up Virtual Environment

```bash
python -m venv env

# On Linux/macOS
source env/bin/activate

# On Windows
env\Scripts\activate
```

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
```

### 5. Run the Application

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | High-performance REST API |
| **Data Processing** | Pandas | Excel/CSV parsing & transformation |
| **AI Integration** | OpenAI SDK | LLM-powered column mapping |
| **Runtime** | Python 3.10+ | Core application environment |

---

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs/swagger`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | ✅ Yes |
| `DEEPSEEK_API_BASE_URL` | DeepSeek API endpoint | ✅ Yes |
| `TEMPLATE_PATH` | Path to the Sage 50 template file | ✅ Yes |

### Supported File Formats

- **CSV**: `.csv` files with various delimiters
- **Excel**: `.xlsx` and `.xls` formats
---
