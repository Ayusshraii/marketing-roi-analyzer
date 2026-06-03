# Marketing Campaign ROI Analyzer

I built this project because I kept wondering — why do marketing dashboards only tell you *what* happened but never *why*? A campaign flops, ROAS drops, and the team just guesses what went wrong with the ad copy.

So I tried to solve that. This project analyzes ad campaign performance using SQL and Python, runs A/B significance tests, and then uses the Gemini AI API to actually read the top and bottom performing ad copies and explain what's driving the difference — in plain English.

It's not perfect, but it taught me a lot about combining traditional analytics with AI in a way that's actually useful for non-technical teams.

---

## What it does

- Pulls campaign performance data and calculates CTR, ROAS, CPC, and conversion rate
- Compares creative variants using chi-squared A/B testing to check if differences are statistically significant
- Sends top vs bottom performing ad copies to Gemini API and gets a diagnosis of what copy patterns are working
- Generates a formatted Excel report with all the KPIs across 3 sheets
- Power BI dashboard for visual exploration of campaign and creative performance

---

## Tech used

- Python (Pandas, SciPy, OpenPyXL)
- MySQL
- Power BI + DAX
- Gemini AI API
- Excel

---

## Project structure

```
marketing-roi-analyzer/
├── data/
│   ├── raw/                  
│   └── processed/            
├── sql/
│   ├── 01_create_tables.sql  
│   ├── 02_campaign_metrics.sql
│   └── 03_ab_test_analysis.sql
├── src/
│   ├── data_prep.py          
│   ├── ab_test.py            
│   ├── ai_diagnosis.py       
│   └── report_generator.py  
├── powerbi/
│   └── campaign_dashboard.pbix
├── outputs/
├── requirements.txt
└── .env.example
```

---

## How to run it

```bash
git clone https://github.com/Ayusshraii/marketing-roi-analyzer.git
cd marketing-roi-analyzer

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt --prefer-binary

cp .env.example .env
# add your Gemini API key inside .env

python src/data_prep.py --generate-sample
python src/ab_test.py
python src/ai_diagnosis.py
python src/report_generator.py
```

You'll need a free Gemini API key from [aistudio.google.com](https://aistudio.google.com). No credit card needed.

---

## Sample AI output

This is what the Gemini diagnosis looks like for a campaign where Variant D massively outperformed Variant B:

> *Top-performing ads consistently used urgency-triggering language combined with a benefit-first headline. Bottom performers led with the brand name and lacked a clear CTA. The "Learn More" CTA introduced a decision pause where there should have been a decision close. Recommendation: restructure copy to lead with customer benefit + scarcity signal.*

That kind of insight would normally take a marketing analyst hours to write up manually.

---

## What I learned

- How to structure a real analytics pipeline end to end, not just individual scripts
- Chi-squared testing for conversion rate comparison (turns out t-test is wrong for this)
- Prompt engineering — getting the AI to return structured sections I can actually parse
- How much time goes into data cleaning vs the actual analysis (way more than I expected)

---

## Dataset

The project generates synthetic campaign data by default — 5 campaigns, 5 creative variants each, 30 days of daily metrics. You can swap in real data from Meta Ads Manager or Google Ads exports by matching the column format in `data/raw/`.

---

## About

Final year B.E. CSE student at Chandigarh University. Building projects to break into data analytics. This is my second project combining traditional DA skills with Gen AI.

Connect on [LinkedIn](https://linkedin.com/in/ayusshraii)