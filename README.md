# 🛡️ SocialEng Detector

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Web_App-009688?logo=fastapi)]()
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)]()
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn)]()
[![Status](https://img.shields.io/badge/Status-Educational-success)]()

**SocialEng Detector** is a Python-based project for detecting signs of **social engineering** in text messages.  
It supports both **CLI** and **web modes**, stores analysis history in **SQLite**, uses a simple **machine learning model**, exports reports to **PDF**, and includes **unit tests**.

---

## ✨ Features

- Analyze message fields:
  - `sender`
  - `subject`
  - `body`

- Multi-layered analysis:
  - **Heuristics**: detects patterns such as **urgency**, **fear**, **authority**, **greed**, **reciprocity**, and **scarcity**
  - **Statistical signals**: exclamation marks, CAPS ratio, links, suspicious domains
  - **Machine learning model**: `LogisticRegression` trained on a synthetic dataset

- Synthetic dataset with **300 examples**
- Detailed output report including:
  - **risk score (0–100)**
  - detected manipulation techniques
  - explanations
  - protection recommendations
- **FastAPI** web interface
- **SQLite** storage for analysis history
- **PDF export**
- **Unit tests**
- **Docker** support

---

## 📁 Project Structure

```text
app.py           # Web application and CLI entry point
detector.py      # Core detection logic
data_factory.py  # Synthetic dataset generation
ml_model.py      # Model training and loading
storage.py       # SQLite database operations
templates/       # HTML templates
static/          # CSS and static assets
tests/           # Unit tests
data/            # CSV dataset, trained model, and SQLite database
```

⚙️ Installation
```bash
pip install -r requirements.txt
python data_factory.py
python ml_model.py
```
🌐 Run the Web Version
```text
http://127.0.0.1:8000
```

💻 Run the CLI Version
```bash
python app.py --mode cli \
  --sender "security-alert@verify-now.help" \
  --subject "URGENT: Confirm your account" \
  --body "Immediately follow the link http://verify-account-now.xyz/login or your access will be blocked!!!"
```

🔒 Security Notice

This project uses synthetic data only and is intended for local educational use.
It is designed to demonstrate detection and awareness techniques in a safe environment.
