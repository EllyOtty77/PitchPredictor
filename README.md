# ⚽ PitchPredictor

**PitchPredictor** is your one-stop machine learning toolkit for scraping soccer match data and predicting outcomes like a stats wizard. 
Built for data nerds, bettors, and football fanatics who want to outsmart the bookies (or just flex predictive power).

---

## 🧠 What It Does

- 📅 Scrapes upcoming fixture data
- 🧹 Cleans & structures match info
- 📊 Stores past data for long-term modeling
- 🤖 Trains predictive models (win/draw/loss, odds movement, etc.)
- 🧪 Supports EDA, feature engineering, and evaluation
- 📈 Outputs predictions 

---

## Setup Instructions

```bash
# Clone the repo
git clone https://github.com/EllyOtty77/PitchPredictor.git
cd PitchPredictor

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python pitch.py
