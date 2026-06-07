import streamlit as st
import pandas as pd
import requests

# FastAPI URLs (Update with your live PSL FastAPI backend URLs)
BASE_URL = "http://ec2-3-109-101-141.ap-south-1.compute.amazonaws.com:8000/psl-team-results"
LOG_URL = "http://ec2-3-109-101-141.ap-south-1.compute.amazonaws.com:8000/log-click"
PLAYERS_URL = "http://ec2-3-109-101-141.ap-south-1.compute.amazonaws.com:8000/psl-players" 

# Cleaned list matching exactly the 6 core PSL teams
team_abbr_dict = {
    "KK": "Karachi Kings",
    "LQ": "Lahore Qalandars",
    "IU": "Islamabad United",
    "MS": "Multan Sultans",
    "PZ": "Peshawar Zalmi",
    "QG": "Quetta Gladiators"
}

# Function to fetch data from FastAPI (team results)
def fetch_data(team_name: str):
    try:
        response = requests.get(f"{BASE_URL}?team1={team_name}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

# Function to fetch player details from FastAPI
def fetch_players():
    try:
        response = requests.get(PLAYERS_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

# Function to log button click to FastAPI
def log_click(team_name: str, action: str):
    try:
        ip_response = requests.get("https://api64.ipify.org?format=json", timeout=3)
        ip_address = ip_response.json().get("ip")
    except Exception:
        ip_address = "Unknown IP"

    log_payload = {
        "ip_address": ip_address,
        "team_name": team_name,
        "action": action
    }
    headers = {"Content-Type": "application/json"}
    try:
        requests.post(LOG_URL, json=log_payload, headers=headers, timeout=3)
    except Exception:
        pass 

# Streamlit UI configuration
st.set_page_config(page_title="Realtime PSL Cricket Analytics", layout="wide")
st.set_option('client.showErrorDetails', False)

# Custom dark theme stylesheet
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #00a859;
        color: white;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 16px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: none;
    }
    .stButton>button:hover {
        background-color: #00763e;
    }
    .table-container {
        padding: 20px;
        background-color: #1f1f1f;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
    }
    .header {
        color: #ffffff;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .subheader {
        color: #a0a0a0;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 20px;
    }
    .section-header {
        color: #ffffff;
        font-size: 2em;
        margin-top: 40px;
        text-align: center;
    }
    @media only screen and (max-width: 768px) {
        .header { font-size: 2em; }
        .subheader { font-size: 1em; }
        .stButton>button { font-size: 14px; padding: 10px 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Banner image utilizing the requested psl gif file
st.image("streamlit_app.gif", use_container_width=True)
st.markdown('<p class="header">Realtime PSL Cricket Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">PSL Stats and Numbers in split seconds at your fingertips :)</p>', unsafe_allow_html=True)

# Navigation setup using a clean selectbox to guarantee UI rendering
tab = st.selectbox("Select a Module", ("Live Match Statistics", "Player Information"))

if tab == "Live Match Statistics":
    st.markdown("### Live Match Details By Team")
    
    # Pre-populating a clean dropdown selection box to bypass empty state rendering issues
    team_options = ["Select a Team..."] + list(team_abbr_dict.values())
    selected_team = st.selectbox("Choose a PSL Team", team_options)

    if selected_team != "Select a Team...":
        if st.button("Fetch PSL Live Scores", key="fetch_data"):
            with st.spinner('Preparing data streams...'):
                log_click(selected_team, "Fetch PSL Live Scores")
                data = fetch_data(selected_team)

                if data:
                    df = pd.DataFrame(data)
                    if 'team1' in df.columns:
                        cols = ['team1'] + [col for col in df.columns if col != 'team1']
                        df = df[cols]
                    st.markdown(f"### Total Records Found: {len(df)}")
                    st.markdown(f"### Showing PSL Data for: {selected_team}")
                    st.markdown('<div class="table-container">', unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("No data records returned for this team from the backend service.")
    else:
        st.info("Select a franchise from the dropdown menu to fetch metrics.")

elif tab == "Player Information":
    st.markdown("### Player Information")

    if st.button("Fetch Player Details", key="fetch_players"):
        with st.spinner('Compiling player database...'):
            log_click("Player Module", "Fetch Player Details")
            player_data = fetch_players()

            if player_data:
                df_players = pd.DataFrame(player_data)
                st.markdown('<p class="section-header">PSL Player Details</p>', unsafe_allow_html=True)
                st.markdown(f"### Total Registered Players: {len(df_players)}")
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                st.dataframe(df_players, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No data found inside the remote player table.")
