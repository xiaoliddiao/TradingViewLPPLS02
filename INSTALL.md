# Installation Guide

## macOS Installation

### Prerequisites

- macOS 10.13 or higher
- Python 3.9+ (Python 3.13 recommended)
- Homebrew (optional, for easy Python installation)

### Step-by-Step Installation

#### 1. Install Python (if not already installed)

Check if Python is installed:
```bash
python3 --version
```

If Python is not installed or version is < 3.9, install using Homebrew:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.13
```

#### 2. Navigate to Project Directory

```bash
cd /path/to/trading-data-aggregator
```

#### 3. Create Virtual Environment

```bash
python3 -m venv venv
```

#### 4. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

#### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI 0.115.0 (web framework)
- Uvicorn 0.32.1 (ASGI server)
- httpx 0.28.1 (async HTTP client)
- pydantic 2.10.3 (data validation)
- python-dotenv 1.0.1 (environment variables)
- aiohttp 3.11.11 (async HTTP client)

#### 6. Configure API Keys (Optional)

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
nano .env  # or use your preferred editor
```

**Note**: CoinGecko and Stooq work without API keys!

Get free API keys:
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **CoinMarketCap**: https://coinmarketcap.com/api/

#### 7. Start the Server

```bash
python3 -m uvicorn backend.main:app --reload
```

Or use the provided script:
```bash
./run.sh
```

#### 8. Access the Application

Open your browser and go to:
```
http://localhost:8000
```

### Troubleshooting

#### Virtual Environment Issues

If `python3 -m venv venv` fails:
```bash
# On macOS with Homebrew Python
python3.13 -m venv venv

# Or install venv package
pip3 install virtualenv
virtualenv venv
```

#### Port Already in Use

If port 8000 is already in use:
```bash
python3 -m uvicorn backend.main:app --reload --port 8080
```

Then access at `http://localhost:8080`

#### Missing Dependencies

If you get import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### API Key Issues

- **Alpha Vantage** and **CoinMarketCap** require API keys
- **CoinGecko** and **Stooq** work without API keys
- The application will still work with only 2 working adapters

### Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

---

## Linux/Ubuntu Installation

The process is similar to macOS:

```bash
# Install Python (if needed)
sudo apt update
sudo apt install python3.13 python3.13-venv python3-pip

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 -m uvicorn backend.main:app --reload
```

---

## Windows Installation

### Using PowerShell:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn backend.main:app --reload
```

### Using Command Prompt:

```cmd
# Activate virtual environment
venv\Scripts\activate.bat
```

---

## Quick Test

To verify the installation:

```bash
# Start the server
python3 -m uvicorn backend.main:app --reload

# In another terminal, test the API
curl http://localhost:8000/api/health
```

You should see:
```json
{
  "status": "healthy",
  "adapters": {
    "stocks": ["Alpha Vantage", "Stooq"],
    "crypto": ["CoinGecko", "CoinMarketCap"]
  }
}
```

---

## Production Deployment

For production use:

```bash
# Without --reload flag
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Or with Gunicorn (recommended for production)
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove cached files
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review the main README.md
3. Check ADAPTERS.md for adapter-specific issues
4. Ensure all dependencies are installed correctly
5. Verify Python version is 3.9 or higher

For specific adapter issues, see ADAPTERS.md.
