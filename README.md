# VITA Access Map

An interactive data-science project designed to identify communities with
potential need for free tax-preparation assistance in Alameda County,
California.

## Project Motivation

The IRS Volunteer Income Tax Assistance (VITA) program provides free tax
preparation to qualifying taxpayers. However, barriers such as poverty,
disability, language access, internet access, and geographic distance may
affect whether communities can access assistance.

This project combines aggregated IRS and U.S. Census data to explore those
barriers and support data-informed VITA outreach decisions.

## Current Features

- Interactive map of Alameda County ZIP codes
- Preliminary community-need ranking
- ZIP-code-level poverty and disability statistics
- Earned Income Tax Credit claim rates
- Paid tax-preparer usage rates
- Individual ZIP-code explorer
- Transparent scoring methodology

## Preliminary Need Score

The current score standardizes poverty and disability rates using z-scores
and assigns both variables equal weight:

\[
\text{Preliminary Need Score}
=
\frac{\text{Poverty z-score}+\text{Disability z-score}}{2}
\]

A positive score indicates above-average estimated need relative to the
other ZIP codes in the analysis.

This score is preliminary. Future versions will incorporate language,
internet-access, and proximity-to-VITA indicators.

## Data Sources

- IRS Statistics of Income, 2022 ZIP Code Data
- U.S. Census Bureau, 2022 American Community Survey 5-Year Estimates
- U.S. Census Bureau, 2022 Gazetteer Files

All data are aggregated and publicly available. The project contains no
individual taxpayer information.

## Technologies

- Python
- pandas
- scikit-learn
- Streamlit
- Plotly
- Matplotlib
- Seaborn
- Jupyter

## Running the Project

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate