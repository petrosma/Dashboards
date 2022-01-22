import streamlit as st

ma_col_list = ['open', 'high', 'low', 'close', 'hl/2', 'oc/2']

def initialize_states():
    if 'ema_period' not in st.session_state:
        st.session_state.ema_period = 25
    if 'sma_period' not in st.session_state:
        st.session_state.sma_period = 60
    if 'ao_slow_period' not in st.session_state:
        st.session_state.ao_slow_period = 34
    if 'ao_fast_period' not in st.session_state:
        st.session_state.ao_fast_period = 5
    if 'ma_col' not in st.session_state:
        st.session_state.ma_col = 'close'
    if 'rsi_period' not in st.session_state:
        st.session_state.rsi_period = 14