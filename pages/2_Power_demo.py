import time
import pandas as pd
import streamlit as st
import plotly.express as px
import sweat

POINTS = [1,5,10,15,30,60,120,180,240,300,360,480,600,900,1200,2400,3600,4800]

TIME_DURATION_UNITS = (
    ('week', 60*60*24*7),
    ('day', 60*60*24),
    ('h', 60*60),
    ('m', 60),
    ('s', 1)
)

#FN = "RGTCycling_Leuven-City-Flanders_2022-10-06_20-07-31.fit"
FN = "RGTCycling_Mont-Ventoux_2022-09-26_11-00-00.fit"


@st.cache_data
def get_data(fn):

    return sweat.read_fit(FN)

def human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            #parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
            parts.append('{} {}'.format(amount, unit))
    return ', '.join(parts)


if 'data' not in st.session_state or 'fn' not in st.session_state:
    st.sidebar.warning("Select a FIT file from the Home page.")
else:
    st.sidebar.success(f"{st.session_state['fn']} is currently loaded.")
    st.title('Activity Results')
    data = st.session_state["data"]

    #############################################################
    # Power Curve
    #############################################################

    st.header("Power Curve")

    mmp_values = data["power"].sweat.mean_max().values

    # Try and detect best 20-min effort and estimate FTP
    try:
        ftp = int(mmp_values[1200] * 0.95)    
    except:
        ftp = 180

    selected_points = [point for point in POINTS if point < mmp_values.size] + [mmp_values.size -1]

    new_df = pd.DataFrame({"watts": [mmp_values[point] for point in selected_points], "time": [human_time_duration(point) for point in selected_points]})

    fig2 = px.line(new_df, x="time", y="watts")

    fig2.add_hline(y=ftp, line_width=3, line_dash="dash", line_color="red")

    st.plotly_chart(fig2)

    #############################################################
    # Power distribution
    #############################################################

    st.header("Power Distribution")

    fig = px.histogram(data, x="power")

    fig.add_vline(x=ftp, line_width=3, line_dash="dash", line_color="red")    

    st.plotly_chart(fig)

    #############################################################
    # Power Training Zones
    #############################################################

    # https://www.procyclingcoaching.com/resources/power-training-zones-for-cycling/
    st.header(f"Time in Power Training Zones (based on estimated FTP of {ftp})")

    time_in_power_zone  = data["power"].sweat.time_in_zone(
        bins=[0, ftp*0.4, ftp*0.60, ftp*0.8, ftp*0.95, ftp*1.2, ftp*1.5, ftp*3],
        labels=["rest", "Z1 (recovery)", "Z2 (endurance)", "Z3 (tempo)", "Z4 (threshold)", "Z5 (Vo2)", "Z6 (Neuro)"])

    #st.write("Time in Power Training Zones")

    st.write(time_in_power_zone)    

    #############################################################
    # Heart Rate Zones
    #############################################################

    # st.header("Time in Heart Rate Zones")

    # time_in_heart_zone  = data["heartrate"].sweat.time_in_zone(
    #     bins=[0, 100, 120, 140, 160, 170, 180, 999],
    #     labels=["rest", "Z1", "Z2", "Z3", "Z4", "Z5", "Z6"])

    # #st.write("Time in Heart Rate Zones")

    # st.write(time_in_heart_zone )