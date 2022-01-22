from re import S
from attr import NOTHING
import pandas as pd
import numpy as np
from pandas.io.parsers import read_csv
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from st_aggrid import AgGrid
from datetime import datetime as dt
from streamlit.legacy_caching.caching import cache
from constant import ma_col_list
from ta.momentum import rsi
import seaborn as sns


def read_data():
    df = read_csv('forex.csv')
    #df['time'] = df['time'].apply(lambda x:dt.strptime(x[0:10], '%Y-%m-%d'))
    df['time'] = pd.to_datetime(df['time'])
    #df['time'] = pd.to_datetime(df['time'], unit = 'D')
    df['oc/2'] = round((df['open'] + df['close'])*0.5, 4)
    df['hl/2'] = round((df['high'] + df['low'])*0.5, 4)
    return df

def sma(df: pd.DataFrame, window):
    colname = st.session_state.ma_col
    df['sma'] = round(df[colname].rolling(window).mean(), 4)
    return df

def ema(df: pd.DataFrame, window):
    colname = st.session_state.ma_col
    df['ema'] = round(df[colname].ewm(span = window, adjust=False).mean(), 4)
    return df

def ao(df: pd.DataFrame):
    df['ao'] = round(df['hl/2'].rolling(st.session_state.ao_fast_period).mean() - df['hl/2'].rolling(st.session_state.ao_slow_period).mean(), 4)
    return df

def plot_chart(df:pd.DataFrame):
    fig = go.Figure()
    fig = go.Figure()
    fig.add_candlestick(x=df['time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'], name='Candlestick')
    if 'sma' in df.columns.tolist():
        fig.add_scatter(x=df['time'], y=df['sma'], line_shape='spline', name='sma')
    if 'ema' in df.columns.tolist():
        fig.add_scatter(x=df['time'], y=df['ema'], line_shape='spline', name='ema')

    return fig

def rsi_calc(df, window):
    df['rsi'] = round(rsi(df['close'], window), 4)
    
    return df


def content():
    
    df = read_data()
    df = sma(df, st.session_state.sma_period)
    df = ema(df, st.session_state.ema_period)
    df = ao(df)
    df = rsi_calc(df, st.session_state.rsi_period)
    df.dropna('index', inplace=True)

    ind_settings = st.expander('Indicator Settings', expanded=True)
    with ind_settings:
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                st.session_state.ma_col = st.selectbox('Price used in MA Calc.', options = ma_col_list, index = ma_col_list.index(st.session_state.ma_col))
                st.session_state.ema_period = st.number_input('Exponential Moving Average Period:', min_value=2, max_value=999, value = st.session_state.ema_period)
                st.session_state.sma_period = st.number_input('Simple Moving Average Period:', min_value=2, max_value=999, value=st.session_state.sma_period)
        with col2:
            with st.container():
                st.session_state.ao_slow_period = st.number_input('AO Slow Period:', value=st.session_state.ao_slow_period, min_value=2, max_value=999)
                st.session_state.ao_fast_period = st.number_input('AO Fast Period:', value = st.session_state.ao_fast_period, min_value=2, max_value=999)
        with col3:
            with st.container():
                st.session_state.rsi_period = st.number_input('RSI Period:',value = st.session_state.rsi_period, min_value=2, max_value=999)

            
    
    chart_expander = st.expander('chart', expanded=True)
    with chart_expander:
        col1, col2 = st.columns(2)
        with col1:
            dt_from = st.date_input('From:', value = dt(year=2015, month=1, day = 1), help='Provided time range does not affect calculations. All calculation are done in whole range of data.')
        with col2:
            dt_to = st.date_input('To:', value = pd.to_datetime(df['time']).max())

        dp = df[(df['time'].dt.date > dt_from) & (df['time'].dt.date < dt_to)]
        fig = plot_chart(dp)
        st.plotly_chart(fig, use_container_width=True)
    
    heatmap_expander = st.expander('Heat Map', expanded=True)
    with heatmap_expander:
        correlation = df[['sma', 'ema', 'ao','rsi', st.session_state.ma_col]].corr()
        fig = px.imshow(correlation)
        st.plotly_chart(fig)
        st.download_button('Download Correlation Data', data = correlation.to_csv().encode('utf-8'), file_name='corr.csv', mime='text/csv')

    corrplot_expander = st.expander('Correlation Plot', expanded=True)
    with corrplot_expander:
        correlation = df[['sma', 'ema', 'ao', 'rsi', st.session_state.ma_col]]
        fig  = sns.pairplot(correlation)
        st.pyplot(fig)
        

    grid_expander = st.expander('Data Grid', expanded=True)
    with grid_expander:
        AgGrid(df)
        st.download_button('Download data', data = df.to_csv().encode('utf-8'), file_name='data.csv', mime='text/csv')


 

