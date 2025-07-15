import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from huggingface_hub import hf_hub_download

HF_REPO = "aparker03/eeg-csv"

# --- EEG channel descriptions ---
CHANNEL_INFO = {
    "Fp1": "Frontopolar left (near forehead)",
    "Fp2": "Frontopolar right (near forehead)",
    "AF3": "Anterior frontal left",
    "AF4": "Anterior frontal right",
    "AF7": "Anterior frontal left (lateral)",
    "AF8": "Anterior frontal right (lateral)",
    "Fz": "Frontal midline",
    "F1": "Frontal left mid",
    "F2": "Frontal right mid",
    "F3": "Frontal left",
    "F4": "Frontal right",
    "FC1": "Frontal-central left",
    "FC2": "Frontal-central right",
    "Cz": "Central midline (top of head)",
    "C3": "Central left",
    "C4": "Central right",
    "CP1": "Central-parietal left",
    "CP2": "Central-parietal right",
    "Pz": "Parietal midline",
    "P3": "Parietal left",
    "P4": "Parietal right",
    "O1": "Occipital left (visual area)",
    "O2": "Occipital right (visual area)",
    "Oz": "Occipital midline",
    "T7": "Temporal left",
    "T8": "Temporal right",
    "POz": "Parieto-occipital midline"
}

# --- Page config ---
st.set_page_config(page_title="EEG Plotly Viewer", layout="wide")
st.title("🧠 EEG Viewer (Plotly Interactive)")

# --- Load files ---
DATA_DIR = "data/eeg_csv"
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

if not csv_files:
    st.warning("No EEG CSV files found in `data/eeg_csv/`.")
    st.stop()

# --- Extract available subjects ---
subject_ids = sorted({f.split("_")[0].replace("sub-", "") for f in csv_files})

# --- UI controls ---
selected_subj = st.selectbox("👤 Select Subject:", subject_ids)
selected_cond = st.radio("🛌 Select Condition:", ["Normal Sleep (NS)", "Sleep Deprived (SD)"])
selected_task = st.radio("👁️ Select Task:", ["Eyes Open", "Eyes Closed"])

# --- Build filename ---
cond_map = {"Normal Sleep (NS)": "ses-1", "Sleep Deprived (SD)": "ses-2"}
task_map = {"Eyes Open": "eyesopen", "Eyes Closed": "eyesclosed"}

subj_str = f"sub-{selected_subj}"
session_str = cond_map[selected_cond]
task_str = task_map[selected_task]
filename = f"{subj_str}_{session_str}_{task_str}.csv"
file_path = os.path.join(DATA_DIR, filename)

# --- Load + plot ---
# If file not found locally, try downloading from Hugging Face
if not os.path.exists(file_path):
    with st.spinner(f"📡 Downloading {filename} from Hugging Face..."):
        try:
            downloaded = hf_hub_download(
                repo_id=HF_REPO,
                filename=filename,
                repo_type="dataset",
                local_dir=DATA_DIR,
                local_dir_use_symlinks=False
            )
            file_path = downloaded
        except Exception as e:
            st.error(f"Failed to retrieve `{filename}` from Hugging Face: {e}")
            st.stop()

df = pd.read_csv(file_path)
time_col = "Time"
eeg_channels = [col for col in df.columns if col != time_col]

selected_channels = st.multiselect(
    "🎚️ Select EEG channels to plot:", eeg_channels, default=eeg_channels[:5]
)

with st.expander("ℹ️ What do the EEG channels mean?"):
    if selected_channels:
        for ch in selected_channels:
            desc = CHANNEL_INFO.get(ch, "No description available")
            st.markdown(f"**{ch}**: {desc}")
    else:
        st.markdown("Select a channel above to see its meaning.")

if selected_channels:
    fig = go.Figure()
    for ch in selected_channels:
        fig.add_trace(go.Scatter(x=df[time_col], y=df[ch], mode="lines", name=ch))

    fig.update_layout(
        title=f"EEG Signal – {subj_str}, {session_str}, {task_str}",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (μV)",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No EEG channels selected.")
