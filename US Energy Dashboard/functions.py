import streamlit as st
import pandas as pd
import numpy as np
import requests as req
import json
from st_aggrid import AgGrid
from bokeh.plotting import figure
from datetime import datetime as dt

#api_key = 'YOUR_API_KEY'
api_key = '85c82cbc864a7ca06417533de759c5db'
view_option: st.sidebar.radio


@st.cache(show_spinner=False)
def get_data(api_key,id, type):
    url= f"http://api.eia.gov/{type}/?api_key={api_key}&{type}_id={id}"
    return req.get(url)

@st.cache(show_spinner=False)
def convert_df_tocsv(df:pd.DataFrame):
    return df.to_csv().encode('utf-8')

def convert_date(value: str):
    value = value.strip()
    if len(value) == 4:
        format = '%Y'
        return dt.strptime(value[0:4], format)
    if len(value) == 6:
        format = '%Y/%m'
        return dt.strptime(f'{value[0:4]}/{value[4:6]}', format)
    if len(value) == 8:
        format = '%Y/%m/%d'
        return dt.strptime(f'{value[0:4]}/{value[4:6]}/{value[6:9]}', format)

    
def plot_data(data0):
    global view_option
    if 'data' in data0['series'][0]:
        name = data0['series'][0]['name'] if 'name' in data0['series'][0] else ''
        units = data0['series'][0]['units'] if 'units' in data0['series'][0] else ''
        data = data0['series'][0]['data']
        cat_dict = {k:v for (k, v) in zip([item[0] for item in data],[item[1] for item in data])}
        df = pd.DataFrame(cat_dict.items(), columns=['Argument', 'Value'])
        df['Value'] = df['Value'].astype(float, errors = 'ignore')
        
        if df['Value'].count() == 0:
            st.error('There is no Data')
            return


        if view_option == 'Table':
            st.write(f'Name: {name} --- Units: {units}')
            AgGrid(df, width=100, )
            csv_file = convert_df_tocsv(df)
            dl_button = st.download_button('Download Data', csv_file,file_name='data.csv',mime='text/csv')
            
        else:
            df['Argument'] =  df['Argument'].apply(convert_date)
            axis_type = 'datetime' if df.dtypes['Argument'] == 'datetime64[ns]' else 'linear'
            p = figure(title=name, x_axis_type = axis_type,x_axis_label='Time', y_axis_label=units)
            p.line(df['Argument'], df['Value'], legend_label='Trend', line_width=2)
            st.bokeh_chart(p, use_container_width=True)
        


def select_box_gen(cat_id, type):
    response = get_data(api_key, cat_id, type)
    if response.status_code != 200:
        st.error(f'Some error happened in loading data. Code: {response.status_code}')
        return 

    data0 = json.loads(response.content)
    
    if 'series' in data0:
        plot_data(data0)
    if 'category' in data0:   
        if 'childcategories' in data0['category'] and len(data0['category']['childcategories'])>0:
            data = data0['category']['childcategories']
            type = 'category'
        if 'childseries' in data0['category'] and len(data0['category']['childseries']) > 0:
            data = data0['category']['childseries']
            type = 'series'
        cat_dict = {k:v for (k, v) in zip([item['name'] for item in data],[item[f'{type}_id'] for item in data])}
    
        if len(data) > 0:
            select_cat = st.sidebar.selectbox(f'Select {type.title()}:', cat_dict.keys())
            if select_cat:
                select_box_gen(cat_dict[select_cat], type)  





def run_dash():
    global view_option
    st.set_page_config(layout="wide")
    st.sidebar.header('US Energy Information')
    view_option = st.sidebar.radio('View Option', ['Table','Chart'],help = 'Change view mode')
    select_box_gen(371, 'category')



run_dash()
