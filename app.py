import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="AFL Pro Dashboard", layout="wide")

AFL_TEAM_COLORS = {
    "Adelaide": "#002B5C", "Brisbane Lions": "#A50044", "Carlton": "#031A29",
    "Collingwood": "#000000", "Essendon": "#E2231A", "Fremantle": "#2A1A54",
    "Geelong": "#1C3C63", "Gold Coast": "#E41E31", "GWS Giants": "#F47920",
    "Hawthorn": "#4D2004", "Melbourne": "#07092D", "North Melbourne": "#004A99",
    "Port Adelaide": "#000000", "Richmond": "#FFD200", "St Kilda": "#ED1C24",
    "Sydney": "#ED171F", "West Coast": "#F2AA00", "Western Bulldogs": "#014896"
}

# --- UPLOAD & DATA LOADING ---
with st.sidebar:
    st.title("🏉 AFL Data Hub")
    uploaded_file = st.file_uploader("Upload AFL_Data.xlsx", type=["xlsx"])

if uploaded_file:
    # Read both sheets
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    matches = all_sheets.get('Matches')
    player_data = all_sheets.get('Player_Stats')

    tab1, tab2, tab3 = st.tabs(["Match Results", "The Ladder", "Stat Leaders"])

    # --- TAB 1: MATCH RESULTS ---
    with tab1:
        st.header("Latest Game Results")
        # (Filtered views and scorecards go here - see previous code version)
        st.dataframe(matches, use_container_width=True)

    # --- TAB 2: LIVE LADDER CALCULATION ---
    with tab2:
        st.header("Premiership Ladder")
        
        # Logic to build ladder from match scores
        home = matches[['Home_Team', 'Home_Score', 'Away_Score']].rename(columns={'Home_Team':'Team', 'Home_Score':'For', 'Away_Score':'Against'})
        away = matches[['Away_Team', 'Away_Score', 'Home_Score']].rename(columns={'Away_Team':'Team', 'Away_Score':'For', 'Home_Score':'Against'})
        ladder_df = pd.concat([home, away])
        
        # Group by Team
        ladder = ladder_df.groupby('Team').agg({'For':'sum', 'Against':'sum'}).reset_index()
        
        # Calculate Wins/Draws (approximate for this sample)
        # Note: In a full app, you'd compare row-by-row for W/L/D
        ladder['Percentage'] = (ladder['For'] / ladder['Against'] * 100).round(2)
        ladder = ladder.sort_values(by=['For', 'Percentage'], ascending=False).reset_index(drop=True)
        ladder.index += 1 # Rank 1 to 18
        
        st.table(ladder)

    # --- TAB 3: STAT LEADERS ---
    with tab3:
        if player_data is not None:
            st.header("League Leaders")
            stat_to_view = st.selectbox("Select Statistic", ["Goals", "Disposals", "Tackles", "Clearances"])
            
            top_players = player_data.groupby(['Player', 'Team'])[stat_to_view].sum().sort_values(ascending=False).head(10).reset_index()
            
            fig = px.bar(top_players, x=stat_to_view, y='Player', color='Team',
                         orientation='h', color_discrete_map=AFL_TEAM_COLORS,
                         title=f"Top 10: Total {stat_to_view}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please add a 'Player_Stats' sheet to your Excel file to see individual leaders.")

else:
    st.info("Please upload an Excel file with 'Matches' and 'Player_Stats' sheets.")