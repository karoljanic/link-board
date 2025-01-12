import streamlit as st
import os

from pcb_board import PcbBoard


def input_layout(st: st) -> PcbBoard:
    st.subheader("Enter KiCad PCB file below")
    st.write("Paste project with all footprints and no connections.")

    uploaded_file = st.file_uploader("Upload a KiCad PCB file (*.kicad_pcb)", type=["kicad_pcb"])
    if uploaded_file is not None:
        temp_filename = os.path.join("/app", uploaded_file.name)
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            board = PcbBoard(uploaded_file.name)
            board.load_from_file(temp_filename)
            st.success("PCB loaded successfully!")

            return board
        except Exception as e:
            st.error(f"Error loading PCB: {e}")

    return None