import streamlit as st
import pandas as pd
import requests

# Predefined list of 8 PSL teams (including expansion franchises)
team_abbr_dict = {
    "KK": "Karachi Kings",
    "LQ": "Lahore Qalandars",
    "IU": "Islamabad United",
    "MS": "Multan Sultans",
    "PZ": "Peshawar Zalmi",
    "QG": "Quetta Gladiators",
    "RWP": "Rawalpindiz",
    "HHK": "Hyderabad Kingsmen"
}

# --- STATIC PSL 2026 COMBINED MATCH ENGINE ---
# Unified match database to easily query Head-to-Head encounters
PSL_MATCHES_DATABASE = [
    {"team1": "Karachi Kings", "opponent": "Lahore Qalandars", "venue": "National Bank Stadium, Karachi", "result": "Karachi Kings Won", "margin": "5 wickets", "date": "2026-02-14", "man_of_the_match": "Shan Masood"},
    {"team1": "Karachi Kings", "opponent": "Islamabad United", "venue": "Gaddafi Stadium, Lahore", "result": "Islamabad United Won", "margin": "12 runs", "date": "2026-02-18", "man_of_the_match": "Shadab Khan"},
    {"team1": "Karachi Kings", "opponent": "Rawalpindiz", "venue": "Rawalpindi Cricket Stadium", "result": "Karachi Kings Won", "margin": "7 runs", "date": "2026-02-22", "man_of_the_match": "Shoaib Malik"},
    {"team1": "Lahore Qalandars", "opponent": "Multan Sultans", "venue": "Gaddafi Stadium, Lahore", "result": "Lahore Qalandars Won", "margin": "4 wickets", "date": "2026-02-19", "man_of_the_match": "Fakhar Zaman"},
    {"team1": "Lahore Qalandars", "opponent": "Hyderabad Kingsmen", "venue": "Gaddafi Stadium, Lahore", "result": "Lahore Qalandars Won", "margin": "44 runs", "date": "2026-02-25", "man_of_the_match": "Shaheen Afridi"},
    {"team1": "Islamabad United", "opponent": "Quetta Gladiators", "venue": "Rawalpindi Cricket Stadium", "result": "Islamabad United Won", "margin": "8 wickets", "date": "2026-02-21", "man_of_the_match": "Naseem Shah"},
    {"team1": "Multan Sultans", "opponent": "Peshawar Zalmi", "venue": "Multan Cricket Stadium", "result": "Multan Sultans Won", "margin": "19 runs", "date": "2026-02-24", "man_of_the_match": "Mohammad Rizwan"},
    {"team1": "Peshawar Zalmi", "opponent": "Rawalpindiz", "venue": "Rawalpindi Cricket Stadium", "result": "Peshawar Zalmi Won", "margin": "41 runs", "date": "2026-02-28", "man_of_the_match": "Babar Azam"},
    {"team1": "Quetta Gladiators", "opponent": "Hyderabad Kingsmen", "venue": "National Bank Stadium, Karachi", "result": "Quetta Gladiators Won", "margin": "6 wickets", "date": "2026-03-02", "man_of_the_match": "Saud Shakeel"},
    {"team1": "Rawalpindiz", "opponent": "Hyderabad Kingsmen", "venue": "Rawalpindi Cricket Stadium", "result": "Rawalpindiz Won", "margin": "3 wickets", "date": "2026-03-05", "man_of_the_match": "RWP Local Star"}
]

PSL_PLAYERS_DATA = [
    {"Player Name": "Babar Azam", "Team": "Peshawar Zalmi", "Role": "Batter", "Matches": 12, "Runs": 542, "Wickets": 0, "Strike Rate": 138.5, "Average": 54.20},
    {"Player Name": "Shaheen Afridi", "Team": "Lahore Qalandars", "Role": "Bowler", "Matches": 11, "Runs": 85, "Wickets": 19, "Economy": 7.42, "Average": 18.30},
    {"Player Name": "Mohammad Rizwan", "Team": "Multan Sultans", "Role": "Wicketkeeper-Batter", "Matches": 12, "Runs": 489, "Wickets": 0, "Strike Rate": 130.2, "Average": 48.90},
    {"Player Name": "Shadab Khan", "Team": "Islamabad United", "Role": "All-Rounder", "Matches": 10, "Runs": 210, "Wickets": 14, "Strike Rate": 145.0, "Economy": 7.85},
    {"Player Name": "Shan Masood", "Team": "Karachi Kings", "Role": "Batter", "Matches": 10, "Runs": 310, "Wickets": 0, "Strike Rate": 128.4, "Average": 31.00},
    {"Player Name": "Saud Shakeel", "Team": "Quetta Gladiators", "Role": "Batter", "Matches": 11, "Runs": 395, "Wickets": 0, "Strike Rate": 134.1, "Average": 39.50},
    {"Player Name": "Haris Rauf", "Team": "Lahore Qalandars", "Role": "Bowler", "Matches": 9, "Runs": 12, "Wickets": 15, "Economy": 8.12, "Average": 22.40},
    {"Player Name": "Naseem Shah", "Team": "Islamabad United", "Role": "Bowler", "Matches": 12, "Runs": 45, "Wickets": 18, "Economy": 6.95, "Average": 19.10},
    {"Player Name": "Saim Ayub", "Team": "Peshawar Zalmi", "Role": "Batter", "Matches": 12, "Runs": 360, "Wickets": 4, "Strike Rate": 152.3, "Average": 30.00},
    {"Player Name": "RWP Skipper", "Team": "Rawalpindiz", "Role": "All-Rounder", "Matches": 10, "Runs": 280, "Wickets": 11, "Strike Rate": 142.1, "Economy": 8.10},
    {"Player Name": "HHK Express", "Team": "Hyderabad Kingsmen", "Role": "Bowler", "Matches": 10, "Runs": 30, "Wickets": 16, "Economy": 7.35, "Average": 20.15}
]

# Streamlit Configuration Setup
st.set_page_config(page_title="Realtime PSL 2026 Analytics", layout="wide")
st.set_option('client.showErrorDetails', False)

# Custom Dark Responsive Styling UI
st.markdown(
    """
    <style>
    body { background-color: #121212; color: #E0E0E0; }
    .stButton>button {
        background-color: #00a859; color: white; border-radius: 8px;
        padding: 12px 30px; font-size: 16px; font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); border: none;
    }
    .stButton>button:hover { background-color: #00763e; }
    .table-container {
        padding: 20px; background-color: #1f1f1f; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); margin-top: 20px;
    }
    .header { color: #ffffff; text-align: center; font-size: 2.5em; margin-bottom: 10px; font-weight: bold; }
    .subheader { color: #a0a0a0; text-align: center; font-size: 1.2em; margin-bottom: 30px; }
    @media only screen and (max-width: 768px) {
        .header { font-size: 2em; } .subheader { font-size: 1em; }
        .stButton>button { font-size: 14px; padding: 10px 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render Banner Graphic Component
st.image("streamlit_app.gif", use_container_width=True)
st.markdown('<p class="header">Realtime PSL 2026 Cricket Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">PSL Stats and Numbers in split seconds at your fingertips :)</p>', unsafe_allow_html=True)

# Navigation Tab System
tab = st.selectbox("Select a Module", ("Live Match Statistics", "Player Information"))

if tab == "Live Match Statistics":
    st.markdown("### Head-to-Head Match Analytics Engine")
    
    # 2x Team Selection Dropdowns for Head to Head analysis
    teams_list = list(team_abbr_dict.values())
    col1, col2 = st.columns(2)
    
    with col1:
        team1_selection = st.selectbox("Select Team 1", ["Choose Team 1..."] + teams_list)
    with col2:
        team2_selection = st.selectbox("Select Team 2", ["Choose Team 2..."] + teams_list)

    if team1_selection != "Choose Team 1..." and team2_selection != "Choose Team 2...":
        if team1_selection == team2_selection:
            st.error("Please pick two different franchises to view Head-to-Head statistics.")
        else:
            if st.button("Fetch Head-to-Head Stats", key="fetch_h2h"):
                with st.spinner('Calculating historical metrics...'):
                    # Search filter criteria accommodating both directions
                    h2h_records = [
                        m for m in PSL_MATCHES_DATABASE 
                        if (m["team1"] == team1_selection and m["opponent"] == team2_selection) or 
                           (m["team1"] == team2_selection and m["opponent"] == team1_selection)
                    ]

                    if h2h_records:
                        df_h2h = pd.DataFrame(h2h_records)
                        st.markdown(f"### Head-to-Head Records Between **{team1_selection}** vs **{team2_selection}**")
                        st.markdown(f"**Total Head-to-Head Matches Played:** {len(df_h2h)}")
                        st.markdown('<div class="table-container">', unsafe_allow_html=True)
                        st.dataframe(df_h2h, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"No direct Head-to-Head matches found for {team1_selection} vs {team2_selection} in the current fixture list.")
                        
                        # Fallback: Show standalone data cards for individual context
                        st.markdown("#### Individual Team Historical Outings")
                        t1_records = [m for m in PSL_MATCHES_DATABASE if m["team1"] == team1_selection or m["opponent"] == team1_selection]
                        if t1_records:
                            st.write(f"Recent matches involving **{team1_selection}**:")
                            st.dataframe(pd.DataFrame(t1_records), use_container_width=True)
    else:
        st.info("Please explicitly configure both Team 1 and Team 2 options to verify rivalry analytics.")

elif tab == "Player Information":
    st.markdown("### Player Information Profiles")

    # Dynamic individual profile lookups
    player_names = [p["Player Name"] for p in PSL_PLAYERS_DATA]
    search_options = ["All Players Roster"] + player_names
    selected_player = st.selectbox("Select a Player to View Profile", search_options)

    if st.button("Fetch Player Details", key="fetch_players"):
        with st.spinner('Compiling performance analytics cards...'):
            if selected_player == "All Players Roster":
                df_players = pd.DataFrame(PSL_PLAYERS_DATA)
                st.markdown('### Complete PSL Player Database')
                st.markdown(f"**Total Registered Profiles:** {len(df_players)}")
                st.markdown('<div class="table-container">', unsafe_allow_html=True)
                st.dataframe(df_players, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Isolate target player's metrics card
                profile = [p for p in PSL_PLAYERS_DATA if p["Player Name"] == selected_player][0]
                
                # Render profile metric grid layout
                st.markdown(f"## Player Profile: {profile['Player Name']}")
                st.markdown(f"**Franchise Squad:** {profile['Team']} | **Role:** {profile['Role']}")
                
                p_col1, p_col2, p_col3, p_col4 = st.columns(4)
                p_col1.metric("Matches Played", profile["Matches"])
                
                if profile["Role"] == "Bowler":
                    p_col2.metric("Wickets Taken", profile["Wickets"])
                    p_col3.metric("Economy Rate", profile.get("Economy", "N/A"))
                    p_col4.metric("Bowling Avg", profile["Average"])
                elif profile["Role"] == "Batter" or profile["Role"] == "Wicketkeeper-Batter":
                    p_col2.metric("Total Runs Scored", profile["Runs"])
                    p_col3.metric("Batting Strike Rate", profile.get("Strike Rate", "N/A"))
                    p_col4.metric("Batting Avg", profile["Average"])
                else: # All-Rounder
                    p_col2.metric("Runs Scored", profile["Runs"])
                    p_col3.metric("Wickets Taken", profile["Wickets"])
                    p_col4.metric("Batting Strike Rate", profile.get("Strike Rate", "N/A"))
