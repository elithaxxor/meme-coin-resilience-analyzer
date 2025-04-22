import streamlit as st

def mobile_container():
    """A responsive container for mobile layouts."""
    return st.container()

def mobile_spacer(height=12):
    st.markdown(f"<div style='height:{height}px;'></div>", unsafe_allow_html=True)

def mobile_header(text):
    st.markdown(f"<h2 style='font-size:1.4em'>{text}</h2>", unsafe_allow_html=True)

def mobile_button(label, **kwargs):
    return st.button(label, **kwargs)
