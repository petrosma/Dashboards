

import streamlit
import streamlit as st
from streamlit import cli as stcli
import sys
import functions


if __name__ == '__main__':
    if streamlit._is_running_with_streamlit:
        functions.run_dash()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    
    
