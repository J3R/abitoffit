import streamlit as st
from openai import OpenAI
import sweat

@st.cache_data
def get_facts(coordinates):

    client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=st.secrets["OPENAI_KEY"],
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""Find the neareast mountain pass or town near {coordinates}. 
                If the location is a mountain pass, indicate the duration of the Known Best Time and which cyclist holds it.
                Present in detail the 3 most famous victories in professional cycling races near this location. 
                List 3 touristic activities to do near this location, 3 sites to visit, and 3 local places where quality bikes can be rented.
                Find the date of a local cycling sportive or fondo taking place nearby.
                """
            }
        ],
        max_tokens = 3000,
        model="gpt-3.5-turbo",
        temperature = 0
    )

    return response.choices[0].message.content


if 'data' not in st.session_state or 'fn' not in st.session_state:
    st.sidebar.warning("Select a FIT file from the Home page.")
else:
    st.sidebar.success(f"{st.session_state['fn']} is currently loaded.")
    st.title("Activity Insights Powered by OpenAI's ChatGPT")

    ##############################################################################################
    # Facts
    ##############################################################################################

    st.header("Facts about the region")

    st.warning("This may take some time to load...")

    facts = get_facts(st.session_state["loc_start"])
    st.write(facts)