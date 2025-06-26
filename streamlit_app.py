import streamlit as st
import pandas as pd
import numpy as np
import inspect

st.set_page_config(layout="wide", page_title="Fee Calculator & Forecaster")
st.title("Fee Calculator & Forecaster")

st.markdown("""
This application helps you model tiered fee structures for client services, calculate expected revenue and margin, and forecast financial performance over time.

**How to use:**
1.  Define your fee tiers, including unit ranges, price per unit, and frequency.
2.  Specify the total number of units and the cost per unit.
3.  View the calculated revenue, cost, and margin, along with financial projections and breakeven points.
""")

st.header("1. Define Fee Tiers")

# Global setting for unit type
unit_type_options = ["Funds", "Classes", "Trades", "Investors"]
selected_unit_type = st.selectbox("What do the tiers represent?", unit_type_options)

# Frequency options
frequency_options = {
    "Per Year": 1,
    "Per 6 Months": 2,
    "Per Quarter": 4,
    "Per Month": 12,
    "Per 2 Years": 0.5,
    "Per 3 Years": 1/3,
    "Per 5 Years": 1/5
}

# Number of tiers input
num_tiers = st.number_input("Number of Tiers", min_value=1, max_value=10, value=3, step=1)

tiers_data = []
for i in range(num_tiers):
    st.subheader(f"Tier {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        min_units = st.number_input(f"Min {selected_unit_type} (Tier {i+1})", min_value=0, value=0 if i == 0 else tiers_data[i-1]['max_units'] + 1, step=1, key=f"min_{i}")
    with col2:
        max_units = st.number_input(f"Max {selected_unit_type} (Tier {i+1})", min_value=min_units, value=100 if i == 0 else min_units + 99, step=1, key=f"max_{i}")
    with col3:
        price_per_unit = st.number_input(f"Price per {selected_unit_type} (Tier {i+1})", min_value=0.0, value=100.0 - (i*10), step=0.01, key=f"price_{i}")
    
    frequency_selection = st.selectbox(f"Frequency (Tier {i+1})", list(frequency_options.keys()), key=f"freq_{i}")
    
    tiers_data.append({
        "min_units": min_units,
        "max_units": max_units,
        "price_per_unit": price_per_unit,
        "frequency_multiplier": frequency_options[frequency_selection]
    })

st.header("2. Input for Calculation")

total_units = st.number_input(f"Total Number of {selected_unit_type} to Service", min_value=0, value=150, step=1)
cost_per_unit = st.number_input(f"Cost per {selected_unit_type}", min_value=0.0, value=50.0, step=0.01)

st.header("3. Financial Calculations & Projections")

# Placeholder for calculations and display
st.info("Calculations will appear here after defining tiers and inputs.")

# Placeholder for forecasting and graphs
st.header("4. Forecasting & Visualizations")
projection_period_years = st.slider("Projection Period (Years)", min_value=1, max_value=10, value=5)
st.info("Graphs and breakeven analysis will appear here.")

st.markdown("---")

# --- Source Code Expander ---
with st.expander("View Application Source Code"):
    source_code = inspect.getsource(inspect.currentframe())
    st.code(source_code, language='python')
