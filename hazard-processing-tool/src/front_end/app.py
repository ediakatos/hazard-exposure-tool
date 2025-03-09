"""Streamlit front end for the hazard processing tool with improved UI/UX."""

import streamlit as st
from datetime import datetime
import plotly.express as px

from src.back_end import prepare_hazard_mask, compute_hazard


def configure_page():
    st.set_page_config(page_title="Hazard Processing Tool", layout="wide")
    st.title("Hazard Processing Tool")
    st.markdown("This tool processes hazard data to create a hazard mask and compute hazard metrics.")


def sidebar_controls():
    st.sidebar.title("Hazard Tool Controls")
    st.sidebar.write("Configure hazard processing options below:")
    
    hazard_display_names = ["Coastal_Erosion", "Cyclone", "Deforestation", "Earthquake", "Flood", "Landslide"]
    hazard_mapping = {
        "Coastal_Erosion": "coastal_erosion",
        "Cyclone": "cyclone",
        "Deforestation": "deforestation",
        "Earthquake": "earthquake",
        "Flood": "flood",
        "Landslide": "landslide"
    }
    hazard_choice_display = st.sidebar.selectbox("Select Hazard Type", hazard_display_names)
    hazard_choice = hazard_mapping[hazard_choice_display]
    
    advanced_options = st.sidebar.checkbox("Show advanced options", value=False)
    
    return hazard_choice, advanced_options


def prepare_mask():
    # Cache the mask preparation result so it only runs once per session.
    if "mask_status" not in st.session_state:
        with st.spinner("Preparing hazard mask..."):
            st.session_state["mask_status"] = prepare_hazard_mask.main()
    st.info(st.session_state["mask_status"])


def analysis_tab(hazard_choice):
    st.header("Hazard Analysis")
    if st.button("Run Analysis"):
        with st.spinner(f"Running analysis for {hazard_choice}..."):
            result_df = compute_hazard.run_analysis(hazard_choice)
        st.success("Analysis complete!")
        st.dataframe(result_df, use_container_width=True)
        st.session_state['result_df'] = result_df
        st.session_state['hazard_choice'] = hazard_choice

    if 'result_df' in st.session_state and 'hazard_choice' in st.session_state:
        csv_bytes = st.session_state['result_df'].to_csv(index=False).encode('utf-8')
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{st.session_state['hazard_choice']}_analysis_{ts}.csv"
        st.download_button(label="📥 Download CSV", data=csv_bytes, file_name=filename, mime="text/csv")
    else:
        st.info("Run an analysis to enable CSV download.")


def visualization_tab():
    st.header("Data Visualization")
    if 'result_df' in st.session_state:
        df = st.session_state['result_df']
        st.subheader("Data Table")
        st.dataframe(df, use_container_width=True)
        if 'exposure' in df.columns:
            fig = px.bar(df, x=df.columns[0], y="exposure", title="Exposure by Admin Unit")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No 'exposure' data available for charting.")
    else:
        st.info("No analysis data available. Run an analysis from the 'Analysis' tab.")


def advanced_options_section():
    st.sidebar.markdown("### Advanced Options")
    if st.sidebar.button("Run Full Pipeline (Mask + Compute All Hazards)"):
        with st.spinner("Running full pipeline..."):
            st.session_state["mask_status"] = prepare_hazard_mask.main()
            compute_hazard.main()
        st.sidebar.success("Full pipeline executed!")


def main():
    configure_page()
    hazard_choice, adv_options = sidebar_controls()
    prepare_mask()

    tab_analysis, tab_visualization = st.tabs(["Analysis", "Visualisation"])
    with tab_analysis:
        analysis_tab(hazard_choice)
    with tab_visualization:
        visualization_tab()

    if adv_options:
        advanced_options_section()


if __name__ == "__main__":
    main()
