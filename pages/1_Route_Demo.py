import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sweat

MIN_GRADIENT = 1
MIN_CLIMB_LENGTH = 3

def mypath(k, df, color):
    y=list(df['elevation'])
    dt = df.index
    zero = 0
    return dict(type='path',
                path=f'M {dt[k]}, {y[k]} L {dt[k+1]}, {y[k+1]}  L {dt[k+1]} {zero} L {dt[k]}, {zero} Z',
                fillcolor=color,
                line=dict(color=color, width=0)
               )



def get_shapes(df):

    shapes = []

    for k in range(len(df)-1):
        #if df.vals[k] < df.vals[k+1]:
        #print(k, df.vals[k])
        if df.vals[k] < 3:
            shapes.append(mypath(k, df, 'rgb(254, 240, 1)' ))# Yellow Rose
        #elif df.vals[k] == df.vals[k+1]:
        elif df.vals[k] >= 3 and df.vals[k] < 5:
            shapes.append(mypath(k,df, 'rgb(253, 154, 1)' ))# RYB Orange
        elif df.vals[k] >= 5 and df.vals[k] < 10:
            shapes.append(mypath(k,df, 'rgb(253, 97, 4)' )) # Vivid Orange
        else:
            shapes.append(mypath(k,df, 'rgb(240, 5, 5)' )) #Electric Red
    return shapes

def get_climbs(items, min_gradient=1.5, min_len=3):
    slices = []
    current_slice = []

    for elevation,gradient in items:
        if gradient > min_gradient:
            current_slice.append((elevation,gradient))
        elif len(current_slice) >= min_len:
            slices.append(current_slice)
            current_slice = []

    if len(current_slice) >= min_len:
        slices.append(current_slice)

    return slices


POINTS = [1,5,10,15,30,60,120,180,240,300,360,480,600,900,1200,2400,3600,4800]

TIME_DURATION_UNITS = (
    ('week', 60*60*24*7),
    ('day', 60*60*24),
    ('h', 60*60),
    ('m', 60),
    ('s', 1)
)

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
    data = st.session_state["data"]
    
    st.title('Route Info')

    ##############################################################################################
    # Map for route
    ##############################################################################################

    start, end = st.session_state["loc_start"], st.session_state["loc_end"]

    mymap = folium.Map(location=start, zoom_start=11)
    folium.Marker(
        location=start,
        tooltip="Start @ {} m".format(int(data["elevation"][0])),
        #popup="Start",
        icon=folium.Icon(icon="blue"),
    ).add_to(mymap)

    route_coordinates = list(zip(data["latitude"].values, data["longitude"].values))
    folium.PolyLine(route_coordinates, tooltip="Route").add_to(mymap)

    folium.Marker(
        location=end,
        tooltip="End @ {} m".format(int(data["elevation"].iloc[-1])),
        #popup="End",
        icon=folium.Icon(color="green"),
    ).add_to(mymap)

    st.header(f"Route Map")
    st_folium(mymap, width=700)

    ##############################################################################################
    # Route Elevation Profile (elevation vs. distance)
    ##############################################################################################

    st.header("Route's elevation profile")

    #st.line_chart(data, x="distance", y="elevation")
    elevation_fig = go.Figure(data=go.Scatter(x=data.distance, y=data.elevation, mode='lines'), layout_yaxis_range=[0,max([500, data.elevation.max()])])
    elevation_fig.add_annotation(x=data.distance[0], y=data.elevation[0], text=f"{int(data.elevation[0])}", showarrow=True, arrowhead=1)     
    elevation_fig.add_annotation(x=data.distance[-1], y=data.elevation[-1], text=f"{int(data.elevation[-1])}", showarrow=True, arrowhead=1)     
    elevation_fig.update_layout(xaxis_title="Distance (kms)", yaxis_title="Elevation (m)")
    st.plotly_chart(elevation_fig)   

    ##############################################################################################
    # Climbs based on detection of route segments with high average gradients
    ##############################################################################################
    
    # Research:
    # https://chart-studio.plotly.com/~empet/14750/shapes-associated-to-timeseries-for/#/
    # https://github.com/better-data-science/data-science-for-cycling/blob/main/004_Calculate_and_Visualize_Gradients.ipynb

    # Normalize all distances so that gradients can be grouped by kilometer
    #data['distance_km'] = data['distance'].apply(lambda x: round(x * 2) / 2)
    data['distance_km'] = data['distance'].apply(round)
    avg_gradients = data.groupby("distance_km")['gradient'].mean()
    avg_gradients_with_elevation = [(data[data['distance_km']==km]['elevation'][0], avg_gradient) for km, avg_gradient in avg_gradients.items()]

    # FIXME: we are not capturing the final elevation
    #st.write(avg_gradients_with_elevation)

    climbs = get_climbs(avg_gradients_with_elevation, min_gradient=MIN_GRADIENT, min_len=MIN_CLIMB_LENGTH)

    if climbs:

        #FIXME: Does not work for RGTCycling_Paterberg_2022-10-24_11-00-00.fit
        # RGTCycling_Dunoon_2022-11-06_12-13-39.fit

        st.header("Climbs")

        st.write(f"A climb should consist of a minimum of {MIN_CLIMB_LENGTH} kms, each of which with an average gradient greater than {MIN_GRADIENT}%.")

        st.warning("The results may not be accurate as this feature is experimental.")

        for climb_nbr, climb in enumerate(climbs, start=1):

            elevations, gradients = zip(*climb)

            df = pd.DataFrame({"elevation": elevations, "vals": gradients})

            # DEBUG
            #st.write(df)

            avg_gradient = round(np.mean(gradients),1)
            climb_distance = len(elevations)

            fig= go.Figure(go.Scatter(  
               x=df.index, 
               #x=dt,
               y=df.elevation,
               mode='lines',
               line_width=1.5, 
               line_color='rgb(10,10,10)',
               name='Elevation'))

            for gradient_idx, gradient in enumerate(gradients[:-1]):
                gradient = round(gradient, 1)
                fig.add_annotation(x=gradient_idx+0.5, y=10,
                text=f"{gradient}%",
                showarrow=True,
                arrowhead=1)            


            #axis=dict(zeroline=False, showline=True, mirror=True, showgrid=False)
            fig.update_layout(title=f'Climb {climb_nbr}: ~{climb_distance} kms @ {avg_gradient}%',
                width=600, height=450,
                hovermode='x',
                shapes=get_shapes(df))


            st.plotly_chart(fig)