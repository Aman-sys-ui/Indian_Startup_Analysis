# startup_analysis_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# Page Configuration
# =======================
st.set_page_config(layout="wide", page_title='Indian Startup Funding Analysis')

# =======================
# Load & Prepare Data
# =======================
@st.cache_data
def load_data(path='startup_cleaned.csv'):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['amount(in cr)'] = pd.to_numeric(df['amount(in cr)'], errors='coerce')
    return df

df = load_data()

# =======================
# Sidebar Options
# =======================
st.sidebar.title('Startup Funding Dashboard')
option = st.sidebar.selectbox('Select Analysis Type', ['Select', 'Overall Analysis', 'Start Up', 'Investor'])

# =======================
# Helper Functions
# =======================
def display_metrics(total, max_funding, avg_funding, total_startups):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Investment', f"{round(total,2)} Cr")
    col2.metric('Max Investment', f"{round(max_funding['Amount'].values[0],2)} Cr ({max_funding['Startup'].values[0]})")
    col3.metric('Avg Investment', f"{round(avg_funding,2)} Cr")
    col4.metric('Total Funded Startups', total_startups)

def plot_mom_graph(df, value_type='Total'):
    if value_type == 'Total':
        temp_df = df.groupby(['year','month'])['amount(in cr)'].sum().reset_index()
    else:
        temp_df = df.groupby(['year','month'])['amount(in cr)'].count().reset_index()
    temp_df['Month-Year'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)

    fig = px.line(
        temp_df,
        x='Month-Year',
        y='amount(in cr)',
        markers=True,
        title=f"Month-over-Month {value_type} Analysis",
        labels={'amount(in cr)':'Investment (Cr)'},
        hover_data={'amount(in cr)':':.2f'}
    )
    st.plotly_chart(fig, use_container_width=True)

# =======================
# Overall Analysis
# =======================
def load_overall_analysis():
    st.title('Overall Startup Funding Analysis')
    req_df = df.dropna(subset=['amount(in cr)']).copy()

    total = round(req_df['amount(in cr)'].sum())
    max_funding = req_df.groupby('startup')['amount(in cr)'].max().sort_values(ascending=False).head(1).reset_index()
    max_funding.columns = ['Startup','Amount']
    avg_funding = req_df.groupby('startup')['amount(in cr)'].sum().mean()
    total_startups = df['startup'].nunique()

    display_metrics(total, max_funding, avg_funding, total_startups)

    st.header('Month-over-Month (MoM) Trends')
    value_type = st.selectbox('Select Metric for MoM Graph', ['Total','Count'])
    plot_mom_graph(req_df, value_type=value_type)

    # Top 10 Funded Startups
    st.header("Top 10 Funded Startups")
    top10 = req_df.groupby('startup')['amount(in cr)'].sum().sort_values(ascending=False).head(10).reset_index()
    top10.columns = ['Startup','Amount']
    fig_top10 = px.bar(
        top10, x='Startup', y='Amount',
        title="Top 10 Funded Startups",
        labels={'Startup':'Startup','Amount':'Investment (Cr)'},
        hover_data={'Amount':':.2f'}
    )
    st.plotly_chart(fig_top10, use_container_width=True)

    # Sector-wise Distribution
    st.header("Investment Distribution Across Sectors")
    sector_df = req_df.groupby('vertical')['amount(in cr)'].sum().reset_index()
    sector_df.columns = ['Sector','Amount']
    fig_sector = px.pie(
        sector_df,
        names='Sector',
        values='Amount',
        title='Sector-wise Investment Distribution',
        hover_data={'Amount':':.2f'}
    )
    st.plotly_chart(fig_sector, use_container_width=True)

# =======================
# Investor Analysis
# =======================
def load_recent_investments(investor):
    st.title(f"Investor: {investor} Funding Details")
    req_df = df[df['investors'].str.contains(investor, na=False)].copy()

    st.subheader('Recent Investments')
    st.dataframe(req_df[['date','startup','vertical','city','rounds','amount(in cr)']].head())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Biggest Investments')
        big_series = req_df.groupby('startup')['amount(in cr)'].sum().sort_values(ascending=False).head(10)
        big_df = big_series.reset_index()
        big_df.columns = ['Startup','Amount']
        fig1 = px.bar(
            big_df,
            x='Startup',
            y='Amount',
            title='Top 10 Investments by Investor',
            labels={'Startup':'Startup','Amount':'Investment (Cr)'},
            hover_data={'Amount':':.2f'}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader('Sectors Invested In')
        vertical_df = req_df.groupby('vertical')['amount(in cr)'].sum().reset_index()
        vertical_df.columns = ['Sector','Amount']
        fig2 = px.pie(
            vertical_df,
            names='Sector',
            values='Amount',
            title='Sector Distribution for Investor',
            hover_data={'Amount':':.2f'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Year-over-Year (YOY) Investment Growth")
    yoy_df = req_df.groupby('year')['amount(in cr)'].sum().reset_index()
    yoy_df.columns = ['Year','Amount']
    fig3 = px.line(
        yoy_df,
        x='Year',
        y='Amount',
        markers=True,
        title='YOY Investment Growth',
        labels={'Amount':'Investment (Cr)'},
        hover_data={'Amount':':.2f'}
    )
    st.plotly_chart(fig3, use_container_width=True)

# =======================
# Startup Drill-Down Analysis
# =======================
def load_startup_analysis(startup):
    st.title(f"{startup} Funding Drill-Down Analysis")
    req_df = df[df['startup'] == startup].copy()
    
    if req_df.empty:
        st.warning("No data available for this startup.")
        return

    # Metrics
    total_investment = req_df['amount(in cr)'].sum()
    max_investment = req_df['amount(in cr)'].max()
    avg_investment = req_df['amount(in cr)'].mean()
    total_rounds = req_df.shape[0]

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Total Investment", f"{round(total_investment,2)} Cr")
    col2.metric("Max Investment", f"{round(max_investment,2)} Cr")
    col3.metric("Avg Investment", f"{round(avg_investment,2)} Cr")
    col4.metric("Number of Rounds", total_rounds)

    # MO/M Trend
    st.header("Month-over-Month (MoM) Funding Trend")
    mom_df = req_df.groupby(['year','month'])['amount(in cr)'].sum().reset_index()
    mom_df['Month-Year'] = mom_df['month'].astype(str) + '-' + mom_df['year'].astype(str)
    fig_mom = px.line(mom_df, x='Month-Year', y='amount(in cr)', markers=True,
                      title=f"{startup} - MoM Funding Trend", labels={'amount(in cr)':'Investment (Cr)'},
                      hover_data={'amount(in cr)':':.2f'})
    st.plotly_chart(fig_mom, use_container_width=True)

    # Round Distribution
    st.header("Funding Distribution by Round Type")
    round_df = req_df.groupby('rounds')['amount(in cr)'].sum().reset_index()
    fig_round = px.pie(round_df, names='rounds', values='amount(in cr)',
                       title=f"{startup} - Round Type Distribution", hover_data={'amount(in cr)':':.2f'})
    st.plotly_chart(fig_round, use_container_width=True)

    # City Distribution
    st.header("City-wise Investment Distribution")
    city_df = req_df.groupby('city')['amount(in cr)'].sum().reset_index()
    fig_city = px.pie(city_df, names='city', values='amount(in cr)',
                      title=f"{startup} - City Distribution", hover_data={'amount(in cr)':':.2f'})
    st.plotly_chart(fig_city, use_container_width=True)

    # Top Investors
    st.header("Top Investors")
    inv_df = req_df.copy()
    inv_df['investor_list'] = inv_df['investors'].str.split(',')
    inv_exploded = inv_df.explode('investor_list')
    inv_exploded['investor_list'] = inv_exploded['investor_list'].str.strip()
    investor_df = inv_exploded.groupby('investor_list')['amount(in cr)'].sum().reset_index()
    investor_df = investor_df.sort_values(by='amount(in cr)', ascending=False).head(10)
    fig_inv = px.bar(investor_df, x='investor_list', y='amount(in cr)',
                     title=f"{startup} - Top 10 Investors", labels={'investor_list':'Investor','amount(in cr)':'Investment (Cr)'},
                     hover_data={'amount(in cr)':':.2f'})
    st.plotly_chart(fig_inv, use_container_width=True)

    # YOY Growth
    st.header("Year-over-Year (YOY) Funding Growth")
    yoy_df = req_df.groupby('year')['amount(in cr)'].sum().reset_index()
    yoy_df.columns = ['Year','Amount']
    fig_yoy = px.line(yoy_df, x='Year', y='Amount', markers=True,
                      title=f"{startup} - YOY Funding Growth", labels={'Amount':'Investment (Cr)'},
                      hover_data={'Amount':':.2f'})
    st.plotly_chart(fig_yoy, use_container_width=True)

# =======================
# Main Streamlit Logic
# =======================
if option == 'Select':
    st.write("Please select an option from the sidebar to begin analysis.")

elif option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'Start Up':
    startup = st.sidebar.selectbox('Select StartUp', df['startup'].unique().tolist())
    if st.sidebar.button(f'Find {startup} details'):
        load_startup_analysis(startup)

elif option == 'Investor':
    investor_list = sorted(set(df['investors'].dropna().str.split(',').sum()))
    investor = st.sidebar.selectbox('Select Investor', investor_list)
    if st.sidebar.button(f'Find {investor} details'):
        load_recent_investments(investor)
