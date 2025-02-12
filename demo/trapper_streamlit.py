from pathlib import Path

import streamlit as st
import pandas as pd
from PIL import Image
import os

# Sample DataFrame
df = pd.read_csv("/Users/christian/PycharmProjects/hnee/deepfaune_software/demo/prediction_comparison_trapper_photos_6.csv")
images_path = Path(
        "/Users/christian/data/camera_trapping/trapper_photos_6")

# Streamlit UI
# Session state for index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
st.title("Image Viewer with Predictions")

# Select image
# Navigation buttons
col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
with col_nav1:
    if st.button("Previous"):
        st.session_state.current_index = max(0, st.session_state.current_index - 1)
with col_nav2:
    if st.button("Next 1"):
        st.session_state.current_index = min(len(df) - 1, st.session_state.current_index + 1)
with col_nav3:
    if st.button("Next 5"):
        st.session_state.current_index = min(len(df) - 1, st.session_state.current_index + 5)

selected_row = df.loc[st.session_state.current_index]

# Load and display image (assuming images are in a folder named 'images/')
image_path = images_path / selected_row["image_name"]

col1, col2 = st.columns([1, 1])
with col1:
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption=selected_row["image_name"], use_container_width=True)
    else:
        st.warning(f"Image not found: {selected_row['image_name']}")

with col2:
    st.subheader("Prediction Details")
    st.write(f"**Media ID:** {selected_row['mediaID']}")
    st.write(f"**Prediction:** {selected_row['prediction']}")
    st.write(f"**Score:** {selected_row['score']:.2f}")
    st.write(f"**Common Name:** {selected_row['commonName']}")
    st.write(f"**Count:** {selected_row['count']}")