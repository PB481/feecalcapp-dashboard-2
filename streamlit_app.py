import streamlit as st
import pandas as pd
import numpy as np
import inspect
import plotly.express as px # Import plotly.express
import io # Import io for in-memory file operations

st.set_page_config(layout="wide", page_title="Fee Calculator & Forecaster")
st.title("Fee Calculator & Forecaster")

st.markdown("""
This application helps you model tiered fee structures for client services, calculate expected revenue and margin, and forecast financial performance over time.

**How to use:**
1.  Define your fee tiers, including unit ranges, price per unit, and frequency.
2.  Specify the total number of units and the cost per unit.
3.  View the calculated revenue, cost, and margin, along with financial projections and breakeven points.
""")

with st.sidebar:
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
            min_units = st.number_input(f"Min {selected_unit_type} (Tier {i+1})", min_value=0, value=0 if i == 0 else tiers_data[i-1]['max_units'] + 1, step=100, key=f"min_{i}")
        with col2:
            max_units = st.number_input(f"Max {selected_unit_type} (Tier {i+1})", min_value=min_units, value=100 if i == 0 else min_units + 99, step=100, key=f"max_{i}")
        with col3:
            price_per_unit = st.number_input(f"Price per {selected_unit_type} (Tier {i+1})", min_value=0.0, value=100.0 - (i*10), step=0.01, key=f"price_{i}")
        
        frequency_selection = st.selectbox(f"Frequency (Tier {i+1})", list(frequency_options.keys()), key=f"freq_{i}")
        
        tiers_data.append({
            "min_units": min_units,
            "max_units": max_units,
            "price_per_unit": price_per_unit,
            "frequency_multiplier": frequency_options[frequency_selection],
            "frequency_text": frequency_selection # Store text for report
        })

st.header("2. Input for Calculation")

total_units = st.number_input(f"Total Number of {selected_unit_type} to Service", min_value=0, value=150, step=100)
cost_per_unit = st.number_input(f"Cost per {selected_unit_type}", min_value=0.0, value=50.0, step=0.01)

# --- Core Calculation Logic ---
def calculate_annual_revenue(total_units, tiers_data):
    annual_revenue = 0
    
    # Sort tiers by min_units to ensure correct processing
    sorted_tiers = sorted(tiers_data, key=lambda x: x['min_units'])

    for i, tier in enumerate(sorted_tiers):
        tier_min = tier["min_units"]
        tier_max = tier["max_units"]
        price_per_unit = tier["price_per_unit"]
        frequency_multiplier = tier["frequency_multiplier"]

        # Determine the number of units that fall into this specific tier
        # Units are capped by total_units and the tier's max_units
        units_in_this_tier = max(0, min(total_units, tier_max) - tier_min + 1)

        # If there are previous tiers, subtract units already accounted for
        if i > 0:
            prev_tier_max = sorted_tiers[i-1]['max_units']
            units_already_counted = max(0, min(total_units, prev_tier_max) - tier_min + 1)
            units_in_this_tier = max(0, units_in_this_tier - units_already_counted)

        annual_revenue += (units_in_this_tier * price_per_unit * frequency_multiplier)

    return annual_revenue

annual_revenue = calculate_annual_revenue(total_units, tiers_data)
total_annual_cost = total_units * cost_per_unit
annual_margin = annual_revenue - total_annual_cost

st.header("3. Financial Calculations & Projections")

col_rev, col_cost, col_margin = st.columns(3)
with col_rev:
    st.metric("Expected Annual Revenue", f"${annual_revenue:,.2f}")
with col_cost:
    st.metric("Total Annual Cost", f"${total_annual_cost:,.2f}")
with col_margin:
    st.metric("Annual Margin", f"${annual_margin:,.2f}")


st.header("4. Forecasting & Visualizations")
projection_period_years = st.slider("Projection Period (Years)", min_value=1, max_value=10, value=5)

forecast_df = pd.DataFrame()
if total_units > 0:
    # --- Forecasting Data ---
    forecast_data = []
    for year in range(1, projection_period_years + 1):
        forecast_data.append({
            "Year": year,
            "Revenue": annual_revenue,
            "Cost": total_annual_cost,
            "Margin": annual_margin
        })
    forecast_df = pd.DataFrame(forecast_data)

    st.subheader("Projected Financials")
    st.dataframe(forecast_df.set_index("Year").style.format("${:,.2f}"))

    # --- Breakeven Analysis ---
    if annual_margin < 0 and annual_revenue > 0: # Only calculate breakeven if currently losing money but have revenue
        # Find breakeven units (simplified: where revenue equals cost)
        # This assumes a linear relationship for simplicity in this initial version
        # More complex breakeven would involve iterating through units and recalculating tiered revenue
        if cost_per_unit > 0:
            breakeven_units = annual_revenue / cost_per_unit
            st.info(f"Breakeven Point: Approximately {breakeven_units:,.0f} {selected_unit_type} to cover costs.")
        else:
            st.info("Cost per unit is zero, so breakeven is at 0 units.")
    elif annual_margin >= 0:
        st.success("Already profitable at current unit levels!")
    else:
        st.warning("Cannot calculate breakeven: Revenue is zero or negative.")

    # --- Visualizations ---
    st.subheader("Financial Projections Over Time")

    fig_revenue = px.line(forecast_df, x="Year", y="Revenue", title="Projected Annual Revenue")
    st.plotly_chart(fig_revenue, use_container_width=True)

    fig_cost = px.line(forecast_df, x="Year", y="Cost", title="Projected Annual Cost")
    st.plotly_chart(fig_cost, use_container_width=True)

    fig_margin = px.line(forecast_df, x="Year", y="Margin", title="Projected Annual Margin")
    st.plotly_chart(fig_margin, use_container_width=True)

else:
    st.info("Enter a 'Total Number of Units to Service' greater than 0 to see projections.")


# --- Report Generation ---
@st.cache_data # Cache the report generation to avoid re-running unnecessarily
def generate_excel_report(tiers_data, total_units, cost_per_unit, annual_revenue, total_annual_cost, annual_margin, forecast_df, selected_unit_type, projection_period_years):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary Sheet
        summary_data = {
            "Metric": [
                "Unit Type",
                f"Total Number of {selected_unit_type} Serviced",
                f"Cost per {selected_unit_type}",
                "Expected Annual Revenue",
                "Total Annual Cost",
                "Annual Margin",
                "Projection Period (Years)"
            ],
            "Value": [
                selected_unit_type,
                total_units,
                cost_per_unit,
                annual_revenue,
                total_annual_cost,
                annual_margin,
                projection_period_years
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Tiers Data Sheet
        tiers_report_df = pd.DataFrame(tiers_data)
        tiers_report_df = tiers_report_df.rename(columns={
            "min_units": f"Min {selected_unit_type}",
            "max_units": f"Max {selected_unit_type}",
            "price_per_unit": f"Price per {selected_unit_type}",
            "frequency_text": "Frequency",
            "frequency_multiplier": "Annual Multiplier"
        })
        tiers_report_df.to_excel(writer, sheet_name='Tiers Data', index=False)

        # Forecast Sheet
        if not forecast_df.empty:
            forecast_df.to_excel(writer, sheet_name='Forecast', index=False)

    output.seek(0)
    return output

if total_units > 0:
    excel_report = generate_excel_report(tiers_data, total_units, cost_per_unit, annual_revenue, total_annual_cost, annual_margin, forecast_df, selected_unit_type, projection_period_years)
    st.download_button(
        label="Download Full Report (Excel)",
        data=excel_report,
        file_name="Fee_Calculation_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("---")

# --- Source Code Expander ---
with st.expander("View Application Source Code"):
    source_code = inspect.getsource(inspect.currentframe())
    st.code(source_code, language='python')
