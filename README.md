
````markdown
# 🧠 EIAA — Excel Import Autonomous Agent

**EIAA** is an AI-powered backend service designed to intelligently map and transform Excel/CSV files to the [Sage 50](https://www.sage.com/en-gb/products/sage-50cloud/) customer import template format using a Large Language Model (LLM).

> Ideal for accounting teams, data entry workflows, and ERP migrations.

---

## 🚀 Features

✅ AI-powered **semantic column mapping** (e.g., `"Phone"` → `"Telephone Number"`)  
✅ Supports **CSV and Excel (.xlsx/.xls)** file formats  
✅ Automatically detects **missing required fields** (like `Account Reference`)  
✅ Extracts and analyzes **preview data** to improve accuracy  
✅ Clean, consistent **JSON feedback** for frontend integration  
✅ Download-ready **formatted file output** compatible with Sage 50

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/eiaa-backend.git
cd eiaa-backend
````

### 2. Create and Activate Virtual Environment

```bash
python -m venv env
source env/bin/activate        # On Linux/macOS
# OR
env\Scripts\activate           # On Windows
```

### 3. Install Dependencies

```bash
uv sync  # (recommended if using uv)
```

### 4. Set Environment Variables

Create a `.env` file in the root directory with the following:

```env
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
```

---

## 🛠 Tech Stack

* **FastAPI** — for building high-performance APIs
* **Pandas** — for parsing, previewing, and transforming tabular data
* **OpenAI SDK** — using DeepSeek or compatible models
* **Python 3.10+**

```

---

Let me know if you want to merge this into your earlier full `README.md` or want me to recompile the full, updated version in one block.
```
