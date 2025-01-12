import streamlit as st

from pcb_board import PcbBoard
from planarity import Planarity
from graph import Graph

def builder_layout(board: PcbBoard, st: st) -> None:
    st.subheader("PCB Builder") 
    
    planar_subgraphs = Planarity.max_planar_subgraphs(board.get_components_graph())
    thickness = len(planar_subgraphs)

    st.write(f"Recommended layers number: {thickness}")

    col1, col2, _ = st.columns(3, gap="large", vertical_alignment="center")

    with col1:
        layers_number = st.slider(
            "Select layers number:",
            min_value=1,
            max_value=2*thickness,
            value=thickness, 
            step=1
        )

    with col2:
        separation = st.number_input(
            "Enter separation:",
            min_value=1.0,
            value=10.0,
            step=1.0,
            format="%.2f"
        )

    embedding = Planarity.find_layout_of_planar_graph(
        planar_subgraphs[0], 
        board.get_component_dimensions(), 
        separation,
        "drawing.svg"
    )

    for _ in range(2):
        st.write("")

    st.image("drawing.svg", use_container_width=True)

    for _ in range(3):
        st.write("")

    col1, col2 = st.columns(2, gap="large", vertical_alignment="center")

    board.update_component_positions(embedding)
    output_file = f"updated-{board.get_name()}.kicad_pcb"
    board.save_to_file(output_file)

    with col1:
        with open("drawing.svg", "rb") as file:
            st.download_button(
                "Download SVG",
                file,
                "drawing.svg",
                "image/svg+xml",
                use_container_width=True
            )

    with col2:
        with open(output_file, "rb") as file:
            st.download_button(
                "Download KiCad PCB",
                file,
                output_file,
                "text/plain",
                use_container_width=True
            )
