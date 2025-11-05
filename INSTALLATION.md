# 📦 Installation Guide

## Quick Installation

### Step 1: Install Required Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- ✅ Flask 3.0.0
- ✅ requests 2.31.0
- ✅ python-dotenv 1.0.0

### Step 2: Install Optional Dependencies (for Excel Export)

If you want to export to Excel format, install these optional packages:

**For Python 3.8 (and older)**:
```bash
pip install pandas==2.0.3 openpyxl
```

**For Python 3.9+**:
```bash
pip install pandas openpyxl
```

## Troubleshooting

### Python 3.8 Compatibility

If you're using **Python 3.8**, pandas 2.1.4 is not available. Use:

```bash
pip install pandas==2.0.3 openpyxl
```

### Python Version Check

Check your Python version:
```bash
python --version
```

**Recommended**: Python 3.9 or higher for best compatibility.

### Alternative Installation Methods

#### Method 1: Install Everything (Recommended)
```bash
pip install Flask==3.0.0 requests==2.31.0 python-dotenv
pip install pandas openpyxl
```

#### Method 2: Install Only Required (CSV/JSON Export Only)
```bash
pip install Flask==3.0.0 requests==2.31.0 python-dotenv
```
Excel export will be disabled, but CSV and JSON will work.

#### Method 3: Upgrade Pip First
If you encounter version conflicts:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Version Compatibility

| Python Version | pandas Version | Status |
|----------------|----------------|--------|
| Python 3.8     | pandas 2.0.3   | ✅ Compatible |
| Python 3.9+    | pandas 2.0.3+  | ✅ Compatible |
| Python 3.7     | pandas 1.5.3   | ⚠️ Limited support |

## Verify Installation

After installation, verify everything works:

```bash
python -c "import flask; import requests; import dotenv; print('✅ Core dependencies installed')"
python -c "import pandas; import openpyxl; print('✅ Excel export available')" 2>/dev/null || echo "⚠️ Excel export not available (optional)"
```

## Common Issues

### Issue: "Could not find a version that satisfies the requirement pandas==2.1.4"

**Solution**: 
- For Python 3.8: Use `pandas==2.0.3`
- For Python 3.9+: Use latest pandas version
- Or skip pandas if you don't need Excel export

### Issue: "No module named 'pandas'"

**Solution**: 
```bash
pip install pandas openpyxl
```

### Issue: "No module named 'openpyxl'"

**Solution**: 
```bash
pip install openpyxl
```

### Issue: "pip version is old"

**Solution**: 
```bash
python -m pip install --upgrade pip
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Create `config.env` file (see SETUP_GUIDE.md)
3. ✅ Run the app: `python app.py`
4. ✅ Open browser: `http://127.0.0.1:5000`

---

**Need help?** Check the other guides:
- `SETUP_GUIDE.md` - Where to put API keys
- `UNLIMITED_SCRAPING_GUIDE.md` - Unlimited scraping setup
- `README.md` - Full documentation

