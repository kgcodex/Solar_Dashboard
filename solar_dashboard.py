import streamlit as st
import pandas as pd
import numpy as np
# import altair as alt # Altair is imported but not used in this version, can be removed if not needed
import time # For simulating real-time updates slightly

# --- Configuration ---
st.set_page_config(
    page_title="Solar Energy Dashboard",
    page_icon="☀️",
    layout="wide",  # Use wide layout for dashboard feel
    initial_sidebar_state="collapsed", # Collapse sidebar initially
)

# --- Mock Data Generation ---
def generate_hourly_data(hours=24):
    """Generates realistic-looking hourly solar production and battery data."""
    # FIX: Added format='%H:%M' to address UserWarning about format inference
    time_index = pd.to_datetime(pd.date_range(start='00:00', periods=hours, freq='h').strftime('%H:%M'), format='%H:%M')

    # Solar Production (peaks mid-day, zero at night)
    peak_hour = 13
    std_dev = 3.5
    max_prod = 6.5 # kW
    production = max_prod * np.exp(-((np.arange(hours) - peak_hour)**2 / (2 * std_dev**2)))
    production[production < 0.1] = 0
    production += np.random.rand(hours) * 0.3
    production = np.round(production, 2)

    # Battery Level
    battery = np.zeros(hours)
    min_charge, max_charge = 20, 95
    charge_rate, discharge_rate = 10, 3
    current_charge = 40
    for i in range(hours):
        if production[i] < 0.5 and current_charge > min_charge:
            current_charge -= discharge_rate + np.random.rand() * 1
        elif production[i] > 2.0 and current_charge < max_charge:
             charge_increase = min(charge_rate * (production[i] / max_prod), max_charge - current_charge)
             current_charge += charge_increase + np.random.rand() * 2
        current_charge = max(min_charge, min(max_charge, current_charge))
        battery[i] = round(current_charge)

    df = pd.DataFrame({'Time': time_index, 'Production (kW)': production, 'Battery Level (%)': battery})
    df = df.set_index('Time')
    return df

# Generate data for "Today"
today_data = generate_hourly_data()

# --- Calculate Weekly/Monthly Averages Correctly ---
means = today_data.mean()
num_days_week = 7
scaling_factors_week = 1 + (np.random.rand(num_days_week) - 0.5) * 0.2
week_avg_array = means.values.reshape(-1, 1) * scaling_factors_week
week_days = [f"Day {i+1}" for i in range(num_days_week)]
week_data_daily_avg = pd.DataFrame(week_avg_array, index=means.index, columns=week_days)
num_days_month = 30
scaling_factors_month = 1 + (np.random.rand(num_days_month) - 0.5) * 0.3
month_avg_array = means.values.reshape(-1, 1) * scaling_factors_month
month_days = [f"Day {i+1}" for i in range(num_days_month)]
month_data_daily_avg = pd.DataFrame(month_avg_array, index=means.index, columns=month_days)

# --- Current Status (Snapshot based on generated data) ---
current_time_index = np.random.randint(8, 18)
safe_time_index = min(current_time_index, len(today_data) - 1)
last_hour_index = max(0, safe_time_index - 1)
current_production = today_data['Production (kW)'].iloc[safe_time_index]
previous_production = today_data['Production (kW)'].iloc[last_hour_index]
production_delta = np.round(current_production - previous_production, 1)
current_battery_level = int(today_data['Battery Level (%)'].iloc[safe_time_index])
battery_status = "Charging" if current_production > 1.5 and current_battery_level < 95 else ("Discharging" if current_production < 0.5 and current_battery_level > 20 else "Idle")
current_efficiency = np.round(85 + np.random.rand() * 10, 1)

# --- Simple Flow Calculation ---
home_consumption = np.round(1.5 + np.random.rand() * 2, 2)
battery_power_flow = 0
if battery_status == "Charging":
    battery_power_flow = min(current_production - home_consumption if current_production > home_consumption else 0, 2.0 + np.random.rand())
    battery_power_flow = max(0, battery_power_flow)
elif battery_status == "Discharging":
    battery_power_flow = -min(home_consumption - current_production if home_consumption > current_production else 0, 1.0 + np.random.rand())
    battery_power_flow = min(0, battery_power_flow)
grid_flow = np.round(current_production - home_consumption - battery_power_flow, 2)
grid_status = "Exporting" if grid_flow > 0.1 else ("Importing" if grid_flow < -0.1 else "Idle")
self_sufficiency = max(0, min(100, int(((current_production + max(0, -battery_power_flow)) / (home_consumption + 1e-6)) * 100)))

# --- Consumption Breakdown Data ---
consumption_items = [
    {"name": "Water Heater", "icon": "🌡️", "percentage": np.random.randint(12, 18), "kwh": np.round(np.random.rand() * 2 + 2.5, 1)},
    {"name": "Air Conditioning", "icon": "💨", "percentage": np.random.randint(10, 16), "kwh": np.round(np.random.rand() * 2 + 1.8, 1)},
    {"name": "Kitchen Appliances", "icon": "🍳", "percentage": np.random.randint(8, 12), "kwh": np.round(np.random.rand() * 1.5 + 1.0, 1)},
    {"name": "Laundry Machine", "icon": "🧺", "percentage": np.random.randint(5, 9), "kwh": np.round(np.random.rand() * 1 + 0.5, 1)},
    {"name": "Electronics", "icon": "💻", "percentage": np.random.randint(5, 10), "kwh": np.round(np.random.rand() * 1 + 0.8, 1)},
    {"name": "Storage Freezer", "icon": "🧊", "percentage": np.random.randint(4, 7), "kwh": np.round(np.random.rand() * 0.5 + 0.4, 1)},
]
total_percentage = sum(item['percentage'] for item in consumption_items)
consumption_items.append({"name": "Other", "icon": "💡", "percentage": max(0, 100 - total_percentage), "kwh": np.round(np.random.rand() * 0.5 + 0.3, 1)})

# --- Optimization Insights ---
insights = [
    {"type": "prediction", "icon": "📈", "text": f"High solar production forecast for 11 AM - 3 PM ({np.round(today_data['Production (kW)'].iloc[11:16].mean(), 1)} kW avg)."},
    {"type": "action", "icon": "🔋", "text": "Battery charging optimized: Scheduled to maximize self-consumption during evening peak."},
    {"type": "prediction", "icon": "⏳", "text": f"Evening consumption predicted to be {np.random.choice(['slightly higher', 'average', 'lower'])} than yesterday."},
    {"type": "action", "icon": "💲", "text": f"Grid status: {grid_status}. System is prioritizing self-consumption." if grid_status != "Exporting" else "Grid status: Exporting. Maximizing profit potential."},
]

# --- UI Layout ---

# --- Header ---
header_cols = st.columns([1, 4])
with header_cols[0]:
    st.markdown("<h1 style='font-size: 3em; text-align: center;'>☀️</h1>", unsafe_allow_html=True)
with header_cols[1]:
    st.title("Solar Energy Dashboard")
    st.markdown("Welcome, **Kunal**! Real-time monitoring and optimization.")
st.markdown("---")

# --- Main Dashboard Area (3 Columns) ---
col1, col2, col3 = st.columns([2, 2, 1.5])

# --- Column 1: Solar Production & Battery ---
with col1:
    st.subheader("☀️ Solar Array Status")
    prod_cols = st.columns(2)
    prod_cols[0].metric("Production Now", f"{current_production:.2f} kW", delta=f"{production_delta:.1f} kW vs last hour", delta_color="normal")
    prod_cols[1].metric("Current Efficiency", f"{current_efficiency:.1f}%")
    prod_tab1, prod_tab2, prod_tab3 = st.tabs(["Today (kW)", "Week Avg (kW)", "Month Avg (kW)"])
    with prod_tab1:
        st.line_chart(today_data['Production (kW)'], use_container_width=True)
    with prod_tab2:
        st.bar_chart(week_data_daily_avg.loc['Production (kW)'], use_container_width=True)
        st.caption("Average Daily Production This Week")
    with prod_tab3:
        st.bar_chart(month_data_daily_avg.loc['Production (kW)'], use_container_width=True)
        st.caption("Average Daily Production This Month")
    st.markdown("---")
    st.subheader("🔋 Battery Storage")
    bat_cols = st.columns([1,2])
    with bat_cols[0]:
         st.markdown("<p style='font-size: 2.5em; text-align: center;'>🔋</p>", unsafe_allow_html=True)
         status_color = "green" if battery_status == "Charging" else ("orange" if battery_status == "Discharging" else "grey")
         st.markdown(f"<p style='text-align: center;'>Status: <span style='color:{status_color}; font-weight:bold;'>{battery_status}</span></p>", unsafe_allow_html=True)
    with bat_cols[1]:
        st.metric("Current Level", f"{current_battery_level}%")
        st.progress(current_battery_level)
    st.line_chart(today_data['Battery Level (%)'], use_container_width=True)
    st.caption("Battery Level Today (%)")

# --- Column 2: Energy Flow & Consumption ---
with col2:
    st.subheader("⚡ Energy Flow Now")
    flow_cols = st.columns([1, 2])
    with flow_cols[0]:
        st.markdown("<p style='font-size: 3em; text-align: center;'>⚡</p>", unsafe_allow_html=True)
    with flow_cols[1]:
        st.metric("Home Consumption", f"{home_consumption:.2f} kW")
        grid_delta_color = "inverse" if grid_status == "Exporting" else ("normal" if grid_status == "Importing" else "off")
        grid_label = f"{grid_status}:"
        grid_value_display = f"{abs(grid_flow):.2f} kW" if grid_status != "Idle" else "0.00 kW"
        st.metric(grid_label, grid_value_display, delta_color=grid_delta_color)
        st.metric("Self-Sufficiency", f"{self_sufficiency}%")
    st.markdown("---")
    st.subheader("🏠 Household Consumption")
    st.caption("Estimated Daily Consumption Breakdown")
    for item in consumption_items:
        item_cols = st.columns([1, 4, 2, 2])
        item_cols[0].markdown(f"<span style='font-size: 1.2em;'>{item['icon']}</span>", unsafe_allow_html=True)
        item_cols[1].markdown(f"{item['name']}")
        # FIX: Provide non-empty placeholder labels
        item_cols[2].metric(label="Percentage", value=f"{item['percentage']}%", label_visibility="collapsed")
        item_cols[3].metric(label="kWh", value=f"{item['kwh']} kWh", label_visibility="collapsed")

# --- Column 3: Optimization & User ---
with col3:
    st.subheader("💡 Optimization Insights")
    for insight in insights:
        if insight["type"] == "prediction":
            st.info(f"{insight['icon']} {insight['text']}")
        elif insight["type"] == "action":
            st.success(f"{insight['icon']} {insight['text']}")
        else:
            st.markdown(f"{insight['icon']} {insight['text']}")
    st.markdown("---")
    st.subheader("👤 User Profile")
    user_cols = st.columns([1, 3])
    with user_cols[0]:
        st.markdown("<p style='font-size: 2.5em; text-align: center;'>👤</p>", unsafe_allow_html=True)
    with user_cols[1]:
        st.markdown("Logged in as **Teresa**")
        st.button("View Account Settings", key="user_settings_button")
    st.markdown("---")
    st.caption("System ID: SPG-4521 | Status: Online")

# --- Footer ---
st.markdown("---")
st.caption("Solar Energy Management System v1.0 | © 2024 SPG")
