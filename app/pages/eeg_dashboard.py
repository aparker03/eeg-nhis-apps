import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="EEG Dashboard", layout="wide")
st.title("🧠 EEG Sleep Deprivation Explorer")

DATA_PATH = "data/clean/eeg_summary.csv"

@st.cache_data
def load_eeg_data(path):
    return pd.read_csv(path)

df = load_eeg_data(DATA_PATH)

if df.empty:
    st.warning("No EEG data found.")
else:
    # Step 1: Select session
    condition_map = {
        "Normal Sleep (NS)": "NS",
        "Sleep Deprived (SD)": "SD"
    }
    selected_label = st.selectbox("Choose Sleep Condition:", list(condition_map.keys()))
    suffix = condition_map[selected_label]

    # --- Mood Scores ---
    st.markdown(f"### Mood Scores during **{selected_label}**")
    panas_p = f"PANAS_P_{suffix}"
    panas_n = f"PANAS_N_{suffix}"

    mood_cols = [panas_p, panas_n]
    if all(col in df.columns for col in mood_cols):
        mood_df = df[mood_cols].copy()
        mood_df.columns = ["Positive Affect", "Negative Affect"]

        fig, ax = plt.subplots()
        sns.boxplot(data=mood_df, ax=ax)
        ax.set_ylabel("Score")
        st.pyplot(fig)
    else:
        st.info(f"Some PANAS scores are missing for {suffix}.")

    # --- PVT Reaction Time ---
    st.markdown(f"### Reaction Time (PVT) - Sample Items ({suffix})")

    pvt_cols = [f"PVT_item{i}_{suffix}" for i in range(1, 4)]
    pvt_available = [col for col in pvt_cols if col in df.columns]

    if pvt_available:
        pvt_df = df[pvt_available].melt(var_name="Trial", value_name="Reaction Time (ms)")
        fig2, ax2 = plt.subplots()
        sns.boxplot(x="Trial", y="Reaction Time (ms)", data=pvt_df, ax=ax2)
        ax2.set_ylabel("Reaction Time (ms)")
        st.pyplot(fig2)
    else:
        st.info(f"No PVT data found for {suffix}.")

    # --- EEG Band Power ---
    st.markdown(f"### EEG Band Power during {selected_label}")

    theta_col = "theta_mean"
    alpha_col = "alpha_mean"
    beta_col = "beta_mean"

    # Filter by session (NS or SD)
    filtered_df = df[df["condition"] == suffix]

    if all(col in filtered_df.columns for col in [theta_col, alpha_col, beta_col]):
        band_df = filtered_df[[theta_col, alpha_col, beta_col]].copy()
        band_df.columns = ["Theta (4–7 Hz)", "Alpha (8–12 Hz)", "Beta (13–30 Hz)"]

        fig3, ax3 = plt.subplots()
        sns.boxplot(data=band_df, ax=ax3)
        ax3.set_ylabel("Power (dB)")
        st.pyplot(fig3)
    else:
        st.warning("Some EEG band power columns are missing.")

    # --- Missing Band Data ---
    st.markdown("### ⚠️ Sessions Missing Band Power")
    if any(col not in df.columns for col in [theta_col, alpha_col, beta_col]):
        st.info("One or more EEG bands are not in this dataset.")
    else:
        skipped = df[df[[theta_col, alpha_col, beta_col]].isna().any(axis=1)]
        if skipped.empty:
            st.success("All EEG sessions include theta, alpha, and beta power.")
        else:
            st.warning(f"{len(skipped)} session(s) missing full band power:")
            st.dataframe(skipped[["participant_id", "session", "task"]])

    # --- Participant Table ---
    st.markdown("### Participant Info")
    st.dataframe(
        df[["participant_id", "Gender", "Age"]].drop_duplicates().sort_values("participant_id"),
        use_container_width=True
    )
