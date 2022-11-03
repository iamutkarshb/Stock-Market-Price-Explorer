import streamlit as st
import pandas as pd
import os, shutil, glob
from zipfile import ZipFile
import urllib.request
import requests

st.write("""
# Stock Market Web Application 
""")

st.sidebar.header('User Input')


def get_input():
    start_date = st.sidebar.text_input("Start date", "2020-01-22")
    end_date = st.sidebar.text_input("End date", "2020-01-30")
    stock_symbol = st.sidebar.text_input("Stock Symbol", "20MICRONS")
    return start_date, end_date, stock_symbol


def get_data(symbol, start, end):

    final_df = pd.read_csv('./final csv/bhavcopy_'+start+' -- '+end+'_data.csv')
    df = final_df[final_df['SYMBOL']==symbol]

    df = df.set_index(pd.DatetimeIndex(df['TIMESTAMP'].values))

    return df 

def download_csv_file(start_date,end_date):
    dates = pd.period_range(start_date, end_date,freq='D')
    
    for i in dates:
        newurl="https://www1.nseindia.com/content/historical/EQUITIES/"+i.strftime("%Y")+"/"+i.strftime("%b").upper()+"/cm"+i.strftime("%d%b%Y").upper()+"bhav.csv.zip"
        
        response = requests.get(newurl)
        print(newurl)
        if response.status_code != 200:
            continue
        urllib.request.urlretrieve(newurl, "./zip_file/cm"+i.strftime("%d%b%Y").upper()+"bhav.csv.zip")
        
        with ZipFile(".\zip_file\cm"+i.strftime("%d%b%Y").upper()+"bhav.csv.zip", 'r') as zObject:
            zObject.extractall(path=".\csv file")
        os.remove("./zip_file/cm"+i.strftime("%d%b%Y").upper()+"bhav.csv.zip")

def merge_csv_file(stock_symbol,start_date,end_date):
    file_list = glob.glob('./csv file/*.csv')
    final_df = pd.DataFrame()

    for csv_file in file_list:
        df = pd.read_csv(csv_file)
        csv_file_name = csv_file.split('\\')
        df.columns = df.columns.str.replace(' ', '')
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        df.set_index(['TIMESTAMP'], inplace=True)

        if 'Unnamed:13' in df.columns:
            df.drop(['Unnamed:13'], axis=1, inplace=True)

        df_trim = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

        new_df = df_trim[df_trim['SERIES'].isin(['EQ', 'BE', 'SM'])]
        final_df = final_df.append(new_df)
        os.remove(csv_file)

    final_df.sort_index(inplace=True)
    final_df.to_csv('./final csv/bhavcopy_'+start_date+' -- '+end_date+'_data.csv')

start, end, symbol = get_input()

download_csv_file(start,end)
merge_csv_file(symbol,start,end)

df = get_data(symbol, start, end)

company_name = symbol.upper()


st.header(company_name+" Close Price\n")
st.line_chart(df['CLOSE'])

st.header(company_name+" Open Price\n")
st.line_chart(df['OPEN'])

st.header('Data Statistics')
st.write(df.describe())
