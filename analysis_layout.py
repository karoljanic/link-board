import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

from pcb_board import PcbBoard


def analysis_layout(board: PcbBoard, st: st) -> None:
    st.subheader("PCB Analysis")

    col1, col2 = st.columns(2)
    with col1:
        pads = sorted(board.get_aggregated_pads().items(), key=lambda item: item[0])
        with st.expander("Components & Pads"):
            search_query = st.text_input("Search for a component:", "").lower()
            for key, value in [pad for pad in pads if search_query in pad[0].lower()]:
                st.write(f"**{key.capitalize()}**: {value}")
    with col2:
        nets = sorted(board.get_connections().items(), key=lambda item: item[0])
        with st.expander("Nets"):
            search_query = st.text_input("Search for a net:", "").lower()
            for key, value in [net for net in nets if search_query in net[0].lower()]:
                st.write(f"**{key.capitalize()}**: {value}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Components Graph")
        st.write(f"Nodes: {board.get_components_graph().get_vertices_number()}")
        st.write(f"Edges: {board.get_components_graph().get_edges_number()}")

    with col2:
        st.subheader("Pads Graph")
        st.write(f"Nodes: {board.get_pads_graph().get_vertices_number()}")
        st.write(f"Edges: {board.get_pads_graph().get_edges_number()}")

    for graph, col in [(board.get_components_graph(), col1), (board.get_pads_graph(), col2)]:
        nonzero_degrees = [degree for degree in graph.get_degrees() if degree > 0]

        degree_counts = np.bincount(nonzero_degrees)
        degree_counts_map = {degree: count for degree, count in enumerate(degree_counts) if degree > 0}

        nonzero_indices = degree_counts > 0
        k = np.arange(len(degree_counts))[nonzero_indices]
        degree_counts = degree_counts[nonzero_indices]
        cdf = np.cumsum(degree_counts[::-1])[::-1] / sum(degree_counts)

        log_k = np.log(k)
        log_cdf = np.log(cdf)
        slope, intercept, _, _, _ = linregress(log_k, log_cdf)
        lambda_estimate = -slope

        with col:
            st.write(f"Estimated Power-Law Exponent: {lambda_estimate+1:.2f}")

            fig = go.Figure()
            fig.add_trace(go.Bar(x=list(degree_counts_map.keys()), y=list(degree_counts_map.values())))
            fig.update_layout(title='Degree Histogram', xaxis_title='Degree', yaxis_title='Frequency', title_x=0.5, title_y=0.8)
            st.plotly_chart(fig)

            fig = go.Figure()
            fig.add_trace(go.Scatter
            (
                x=k,
                y=cdf,
                mode='markers',
                name='Degree CDF',
                marker=dict(color='deepskyblue')
            ))
            fig.add_trace(go.Scatter
            (
                x=k,
                y=np.exp(intercept) * k ** slope,
                mode='lines',
                name=f'Power-law fit: {lambda_estimate+1:.2f}',
                line=dict(color='deeppink')
            ))
            fig.update_xaxes(type='log')
            fig.update_yaxes(type='log')
            fig.update_layout(title='Degree CDF', xaxis_title='Degree', yaxis_title='CDF', title_x=0.5, title_y=0.8)
            fig.update_layout(legend=dict(xanchor="center", yanchor="top", x=0.5, y=-0.2))
            st.plotly_chart(fig)