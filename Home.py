import streamlit as st
import sweat

st.set_page_config(
    page_title="Hello",
    page_icon="🚴",
)

st.write("# Welcome to *A Bit of Fit*! 🚴")

st.markdown(
    """
    *A Bit of Fit* is an open-source app built specifically for
    the analysis and enrichment of single cycling activities recorded in FIT files.
    **👈 Select your FIT file below and then check the results from the sidebar** to see some examples
    of what *A Bit of Fit* can do! Your data will not be stored anywhere (see [Streamlit's explanation](https://docs.streamlit.io/knowledge-base/using-streamlit/where-file-uploader-store-when-deleted)). The following demos are available:
    - Route demo: Maps, elevation and climbs
    - Power demo: Analysis of activity mostly using [sweapy](https://sweatpy.gssns.io/)
    - GenAI demo: Retrieve potentially useful facts about the region where the activity took place (using [OpenAi's ChatGPT](https://chat.openai.com))

"""
)

################################################################
# Data loading by file upload
################################################################
if 'data' in st.session_state and 'fn' in st.session_state:
    st.write("File currently loaded: {}".format(st.session_state["fn"]))
#st.sidebar.success("Select a FIT file and a demo above.")
uploaded_file = st.file_uploader("Choose a (new) file")
if uploaded_file is not None:
    try:
        data = sweat.read_fit(uploaded_file)
        data["elevation_gain"] = data["elevation"].diff()
        data["distance_gain"] = data["distance"].diff()
        data["gradient"] = (data["elevation_gain"]/data["distance_gain"])* 100
        data["distance"] = data["distance"] / 1000
        #st.write(f"Loaded {uploaded_file.name}")
        st.session_state["fn"] = uploaded_file.name
        st.session_state["data"] = data
        st.session_state["loc_start"] = (data["latitude"][0], data["longitude"][0])
        st.session_state["loc_end"] = (data["latitude"].values[-1], data["longitude"].values[-1])
    except Exception as e:
        st.write(e)
#################################################################


if 'data' in st.session_state and 'fn' in st.session_state:
    st.sidebar.success(f"{st.session_state['fn']} is currently loaded.")
    data = st.session_state["data"]
    
    st.title('Activity Summary')

    ascent = int(data[data["elevation_gain"] > 0]["elevation_gain"].sum())
    descent = int(abs(data[data["elevation_gain"] < 0]["elevation_gain"].sum()))
    distance = round(data["distance"].iloc[-1], 2)
    start_time = data.index[0]
    end_time = data.index[-1]
    elapsed_time = round((end_time - start_time).total_seconds()/60, 1)
    #st.write(data.head())
    speed = round(distance/(elapsed_time/60),1)
    st.write(f"Elapsed time: {elapsed_time} mins")
    st.write(f"Distance: {distance} kms")
    st.write(f"Speed: {speed} km/h")
    st.write(f"Ascent: {ascent} m")
    st.write(f"Descent: {descent} m")
    st.write("Positive elevation gain: {} m".format(ascent - descent))
