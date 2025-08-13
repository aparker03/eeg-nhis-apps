import streamlit as st
import pandas as pd
import altair as alt

# --- Variable Descriptions ---
nhisVarDesc = {
    'SLPMEDINTRO_A': 'The next three questions are about sleep medications and supplements. For the first two questions, do not include marijuana or CBD products.',
    'SLPMED3_A': 'During the past 30 days, how often did you use marijuana or CBD products to help you fall asleep or stay asleep?',
    'SLPMED2_A': 'During the past 30 days, how often did you take any over the counter (OTC) medications or supplements to help you fall asleep or stay asleep?',
    'SLPMED1_A': 'During the past 30 days, how often did you take any medications prescribed by a doctor to help you fall asleep or stay asleep?',
    'SLPSTY_A': 'How often did you have trouble staying asleep?',
    'SLPFLL_A': 'During the past 30 days, how often did you have trouble falling asleep?',
    'SLPREST_A': 'During the past 30 days, how often did you wake up feeling well-rested?',
    'SLPHOURS_A': 'On average, how many hours of sleep do you get in a 24-hour period?',
    'SEX_A': 'Sex of Sample Adult',
    'AGEP_A': 'Age of Sample Adult (top coded)',
    'EDUCP_A': 'Educational level of sample adult',
}

# --- Page Setup ---
st.set_page_config(
    page_title="Sleep Insights",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global Style Block with Dark/Light Mode Support ---
STYLE_BLOCK = r"""
<style>
    h1 {
        font-size: 2.3rem !important;
        margin-bottom: 0.5rem;
    }
    h3 {
        font-size: 1.5rem !important;
        margin-top: 2rem;
    }
    .section-note {
        font-size: 1rem;
        color: #555;
        margin-top: 0;
        max-width: 800px;
    }
    .footer {
        font-size: 0.85rem;
        color: #777;
        text-align: center;
        padding-top: 40px;
        margin-top: 30px;
    }

    /* Variable dictionary styles that adapt to Streamlit's theme */
    .variable-desc {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ff4b4b;
        background-color: rgba(255, 75, 75, 0.1);
    }

    .variable-desc h4 {
        margin-bottom: 10px;
        color: #ff4b4b;
    }

    .variable-item {
        margin: 8px 0;
        padding: 8px 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    }

    .variable-item:last-child {
        border-bottom: none;
    }

    .variable-code {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #ff4b4b;
    }

    /* Metrics explanation styles */
    .metric-explanation {
        background-color: rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(0, 123, 255, 0.3);
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        color: inherit;
    }

    /* Force theme-aware colors using Streamlit's CSS variables if available */
    @media (prefers-color-scheme: dark) {
        .variable-desc {
            background-color: rgba(255, 75, 75, 0.15);
        }
        .metric-explanation {
            background-color: rgba(0, 123, 255, 0.15);
        }
    }
</style>
"""
st.markdown(STYLE_BLOCK, unsafe_allow_html=True)

# --- App Header ---
st.markdown("""
    <h1>Sleep Insights: National Health Interview Survey</h1>
    <p class='section-note'>
        This dashboard visualizes responses from the NHIS sleep dataset. You can filter by demographic factors, examine usage of sleep aids, and explore patterns in sleep quality and duration.
    </p>
""", unsafe_allow_html=True)


# --- Load Data ---
@st.cache_data
def load_sleep_data():
    return pd.read_csv("data/clean/nhis_sleep_demo_clean.csv")


df = load_sleep_data()

# --- Filter Controls (On-Page) ---
st.markdown("### 🎚️ Filter Options")
col1, col2, col3 = st.columns(3)

with col1:
    age_filter = st.slider(
        "Age Range",
        18,
        85,
        (18, 85),
        key="age_range_slider"
    )

with col2:
    sex_filter = st.multiselect(
        "Sex (encoded)",
        options=sorted(df["SEX_A"].dropna().unique()),
        default=sorted(df["SEX_A"].dropna().unique()),
        key="sex_multiselect"
    )

with col3:
    edu_filter = st.multiselect(
        "Education Level (encoded)",
        options=sorted(df["EDUCP_A"].dropna().unique()),
        default=sorted(df["EDUCP_A"].dropna().unique()),
        key="edu_multiselect"
    )

# --- Apply Filters ---
filtered_df = df[
    (df["AGEP_A"].between(age_filter[0], age_filter[1])) &
    (df["SEX_A"].isin(sex_filter)) &
    (df["EDUCP_A"].isin(edu_filter))
    ]

# --- Frequency label map ---
sleep_freq_labels = {
    1: "Never", 2: "Rarely", 3: "Sometimes", 4: "Often", 5: "Always"
}

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🔍 Overview", "📊 Visualizations", "💾 Export"])

# --- Tab 1: Overview ---
with tab1:
    st.markdown("### 📋 Overview")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("#### Filtered Data Preview")
        st.dataframe(filtered_df.head(), use_container_width=True)

    with col2:
        st.markdown("#### Summary Stats")
        avg_sleep = filtered_df["SLPHOURS_A"].mean()
        poor_sleep_count = filtered_df["SLPFLL_A"].isin([4, 5]).sum()

        st.metric("Avg Sleep (hrs)", f"{avg_sleep:.1f}")
        st.metric("Often/Always Trouble Falling Asleep", f"{poor_sleep_count:,} respondents")

# --- Tab 2: Visualizations ---
with tab2:
    st.markdown("### 📊 Interactive Visualizations")

    # --- Column Descriptions Section ---
    st.markdown("#### 📚 Column Descriptions")

    with st.expander("Click to see variable definitions", expanded=False):
        st.markdown("""
        <div class="variable-desc">
            <h4>📖 Variable Dictionary</h4>
        </div>
        """, unsafe_allow_html=True)

        for var_code, description in nhisVarDesc.items():
            st.markdown(f"""
            <div class="variable-item">
                <span class="variable-code">{var_code}:</span> {description}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Correlation Matrix (Altair) excluding SLPMEDINTRO_A ---
    st.markdown("#### 🔗 Correlation Matrix")
    # Select columns for correlation, excluding 'SLPMEDINTRO_A'
    corr_cols = [col for col in filtered_df.select_dtypes(include='number').columns if col != 'SLPMEDINTRO_A']
    corr = filtered_df[corr_cols].corr()
    corr_df = corr.reset_index().melt(id_vars='index')
    corr_df.columns = ['Variable 1', 'Variable 2', 'Correlation']

    heatmap = alt.Chart(corr_df).mark_rect().encode(
        x=alt.X('Variable 1:O', title=None),
        y=alt.Y('Variable 2:O', title=None),
        color=alt.Color('Correlation:Q', scale=alt.Scale(scheme='redblue', domain=(-1, 1))),
        tooltip=['Variable 1', 'Variable 2', alt.Tooltip('Correlation:Q', format=".2f")]
    ).properties(width=600, height=600)

    text = alt.Chart(corr_df).mark_text(baseline='middle').encode(
        x='Variable 1:O',
        y='Variable 2:O',
        text=alt.Text('Correlation:Q', format=".2f"),
        color=alt.condition(
            "datum.Correlation > 0.5 || datum.Correlation < -0.5",
            alt.value('white'),
            alt.value('black')
        )
    )

    st.altair_chart(heatmap + text, use_container_width=True)

    # 1. Distribution of Sleep Hours
    st.markdown("#### ⏳ Distribution of Sleep Hours")
    hist = alt.Chart(filtered_df).mark_bar(opacity=0.7).encode(
        alt.X("SLPHOURS_A:Q", bin=alt.Bin(maxbins=20), title="Sleep Hours (per 24 hrs)"),
        alt.Y("count()", title="Number of Respondents"),
        tooltip=["count()"]
    ).properties(width=600, height=400)
    st.altair_chart(hist, use_container_width=True)

    # 2. Sleep Hours vs. Age
    st.markdown("#### 👤 Sleep Hours vs. Age")
    scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X("AGEP_A:Q", title="Age"),
        y=alt.Y("SLPHOURS_A:Q", title="Sleep Hours"),
        tooltip=["AGEP_A", "SLPHOURS_A"]
    ).properties(width=600, height=400)
    regression = scatter.transform_regression("AGEP_A", "SLPHOURS_A").mark_line(color="red")
    st.altair_chart(scatter + regression, use_container_width=True)

    # 3. Sleep Aid Usage by Age Groups (NEW VISUALIZATION)
    st.markdown("#### 💊 Sleep Aid Usage by Age Groups")


    # Create age groups
    def create_age_groups(age):
        if age < 30:
            return "18-29"
        elif age < 40:
            return "30-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        elif age < 70:
            return "60-69"
        else:
            return "70+"


    # Add age groups to filtered dataframe
    viz_df = filtered_df.copy()
    viz_df["Age_Group"] = viz_df["AGEP_A"].apply(create_age_groups)

    # Create sleep aid usage data
    sleep_aid_cols = ['SLPMED1_A', 'SLPMED2_A', 'SLPMED3_A']
    sleep_aid_labels = {
        'SLPMED1_A': 'Prescription Sleep Medication',
        'SLPMED2_A': 'OTC Sleep Aids/Supplements',
        'SLPMED3_A': 'Marijuana/CBD Products'
    }

    # Calculate percentage of people who use each sleep aid "Often" or "Always" (4 or 5)
    sleep_aid_data = []

    for age_group in sorted(viz_df["Age_Group"].unique()):
        age_group_data = viz_df[viz_df["Age_Group"] == age_group]

        for col, label in sleep_aid_labels.items():
            if col in viz_df.columns:
                # Count people who use "Often" (4) or "Always" (5)
                users = age_group_data[col].isin([4, 5]).sum()
                total = age_group_data[col].notna().sum()
                percentage = (users / total * 100) if total > 0 else 0

                sleep_aid_data.append({
                    'Age_Group': age_group,
                    'Sleep_Aid_Type': label,
                    'Usage_Percentage': percentage,
                    'Users_Count': users,
                    'Total_Count': total
                })

    sleep_aid_df = pd.DataFrame(sleep_aid_data)

    # Create grouped bar chart
    sleep_aid_chart = alt.Chart(sleep_aid_df).mark_bar().encode(
        x=alt.X('Age_Group:N', title='Age Group', sort=['18-29', '30-39', '40-49', '50-59', '60-69', '70+']),
        y=alt.Y('Usage_Percentage:Q', title='Percentage Using Often/Always (%)'),
        color=alt.Color('Sleep_Aid_Type:N',
                        title='Sleep Aid Type',
                        scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c'])),
        xOffset=alt.XOffset('Sleep_Aid_Type:N'),
        tooltip=[
            'Age_Group:N',
            'Sleep_Aid_Type:N',
            alt.Tooltip('Usage_Percentage:Q', format='.1f', title='Usage %'),
            alt.Tooltip('Users_Count:Q', title='Number of Users'),
            alt.Tooltip('Total_Count:Q', title='Total Respondents')
        ]
    ).properties(
        width=700,
        height=400,
        title='Sleep Aid Usage by Age Group (Often/Always Users)'
    )

    st.altair_chart(sleep_aid_chart, use_container_width=True)

    # Add summary statistics with explanations
    st.markdown("#### 📈 Sleep Aid Usage Metrics")

    # Explanation box
    st.markdown("""
    <div class="metric-explanation">
        <strong>📊 How to Read These Metrics:</strong><br>
        These percentages show the proportion of respondents in your filtered dataset who use each type of sleep aid 
        <strong>"Often"</strong> or <strong>"Always"</strong> (responding 4 or 5 on the 5-point scale). The numbers in smaller text 
        show the actual count of frequent users out of the total respondents who answered each question.
        <br><br>
        <strong>🔍 What This Tells Us:</strong><br>
        • <strong>Higher percentages</strong> suggest more prevalent sleep issues requiring intervention<br>
        • <strong>Prescription vs. OTC patterns</strong> can indicate severity of sleep problems<br>
        • <strong>Marijuana/CBD usage</strong> reflects alternative treatment preferences<br>
        • <strong>Age group differences</strong> in the chart above show how sleep aid needs change across life stages
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        prescription_users = viz_df['SLPMED1_A'].isin([4, 5]).sum() if 'SLPMED1_A' in viz_df.columns else 0
        prescription_total = viz_df['SLPMED1_A'].notna().sum() if 'SLPMED1_A' in viz_df.columns else 1
        st.metric("Prescription Sleep Meds", f"{prescription_users / prescription_total * 100:.1f}%",
                  f"{prescription_users:,} of {prescription_total:,} respondents")

    with col2:
        otc_users = viz_df['SLPMED2_A'].isin([4, 5]).sum() if 'SLPMED2_A' in viz_df.columns else 0
        otc_total = viz_df['SLPMED2_A'].notna().sum() if 'SLPMED2_A' in viz_df.columns else 1
        st.metric("OTC Sleep Aids", f"{otc_users / otc_total * 100:.1f}%",
                  f"{otc_users:,} of {otc_total:,} respondents")

    with col3:
        cannabis_users = viz_df['SLPMED3_A'].isin([4, 5]).sum() if 'SLPMED3_A' in viz_df.columns else 0
        cannabis_total = viz_df['SLPMED3_A'].notna().sum() if 'SLPMED3_A' in viz_df.columns else 1
        st.metric("Marijuana/CBD", f"{cannabis_users / cannabis_total * 100:.1f}%",
                  f"{cannabis_users:,} of {cannabis_total:,} respondents")

# --- Tab 3: Export ---
with tab3:
    st.markdown("### 💾 Export Filtered Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="filtered_sleep_data.csv",
        mime="text/csv"
    )

    st.markdown("### 📝 Notes")
    st.info("Sleep frequency variables are coded as: 1 = Never, 2 = Rarely, 3 = Sometimes, 4 = Often, 5 = Always.")

# --- Footer ---
st.markdown(
    "<hr class='footer'><div class='footer'>😴 Built with Streamlit • Data Source: NHIS • © 2025 Your Name</div>",
    unsafe_allow_html=True)