# UK Flu Hospital Admissions Analyser

Simple Python project analysing UKHSA data on influenza hospital admission rates in England.

## Relevance
Tracks NHS pressure from flu during the 2025–26 winter season (Doctor proposed strike starting on Dec. 22, 2025 and early onset of flu season, shows a lot of growing pressure on the NHS) – a key public health indicator.

![python project](https://github.com/user-attachments/assets/e421cf53-caca-4bf8-bf4b-31f9c5463255)
![uk-flu-seasonal-comparison](https://github.com/user-attachments/assets/eb4e939e-bb9c-4bf3-804a-95bb43040b0b)


## Setup & Run
1. `python -m venv .venv`
2. Activate venv
3. `pip install -r requirements.txt`
4. `python fetch_and_analyze.py`

## Data Source
UKHSA Public API (Open Government Licence):  
Metric: Influenza_healthcare_hospitalAdmissionRateByWeek  
https://ukhsa-dashboard.data.gov.uk/

## Limitations
- Sentinel surveillance (subset of trusts).
- Weekly data, updated Thursdays.

Latest national flu reports: https://www.gov.uk/government/collections/influenza-surveillance-reports
