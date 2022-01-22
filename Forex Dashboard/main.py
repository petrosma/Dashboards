from numpy.ma.core import count, mean
import streamlit
import streamlit as st
from streamlit import cli as stcli
import sys
import functions
import constant


if __name__ == '__main__':
    if streamlit._is_running_with_streamlit:
        constant.initialize_states()
        st.set_page_config(layout='wide')
        functions.content()

    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())