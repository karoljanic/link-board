import streamlit as st

from analysis_layout import analysis_layout
from builder_layout import builder_layout
from input_layout import input_layout

def main():
    st.set_page_config(
        page_title="LinkBoard",
        page_icon=":rocket:",
        layout="wide",
    )
    
    st.title("KiCad PCB Layout Builder")

    for _ in range(3):
        st.write("")

    board = input_layout(st)

    if board is not None:
        for _ in range(3):
            st.write("")

        tab1, tab2 = st.tabs(["Structure Analysis", "Layout Builder"])

        with tab1:
            try:
                analysis_layout(board, st)
            except Exception as e:
                st.error(f"Error analyzing PCB: {e}")

        with tab2:
            try:
                builder_layout(board, st)
            except Exception as e:
                st.error(f'Error building PCB: {e}')
    else:
        st.error("Please upload a file.")


# Run the app
if __name__ == "__main__":
    main()
