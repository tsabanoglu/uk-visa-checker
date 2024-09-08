#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 12:50:32 2024

@author: tugbasabanoglu
"""

import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup



# create fnction to scrape the page and extract the latest CSV link
def get_latest_csv_url():
    page_url = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
    response = requests.get(page_url)
    
    # check if the page loaded successfully
    if response.status_code != 200:
        st.error("Failed to retrieve the page.")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # first CSV link that matches 'Worker_and_Temporary_Worker.csv'
    latest_link = None
    for link in soup.find_all('a', href=True):
        if 'Worker_and_Temporary_Worker.csv' in link['href']:
            latest_link = link['href']
            break

    if latest_link:
        # complete the URL if it is relative
        if not latest_link.startswith('https://'):
            latest_link = "https://www.gov.uk" + latest_link
        return latest_link
    else:
        st.error("Failed to find the latest CSV link.")
        return None

# caching data for one week 
@st.cache_data(ttl=604800)
def load_data():
    url = get_latest_csv_url()
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = pd.read_csv(url)
                return data
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
        else:
            st.error("Failed to load data from the URL.")
    return None

data = load_data()

# Streamlit web app
st.title('UK Visa Sponsorship Checker')

# explanation for the app
st.markdown("""
This app checks whether an organization offers visa sponsorship for workers. 
The app retrieves its data directly from the UK Government website, 
[Register of Licensed Sponsors for Workers](https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers).
""")

# user input for company name
company_to_check = st.text_input('Enter the company name you want to check:', '').strip()

# process input and search in the dataset
if company_to_check:
    if data is not None:
        # normalize the input (i.e. lower/upper case) and the dataset for case-insensitive comparison
        data['Organisation Name'] = data['Organisation Name'].str.lower().dropna()
        company_to_check_lower = company_to_check.lower()
        
        if data['Organisation Name'].str.contains(company_to_check_lower, case=False).any():
            st.success(f"{company_to_check} offers visa sponsorship.")
        else:
            st.warning(f"{company_to_check} does not appear to offer visa sponsorship.")
    else:
        st.error("Data not loaded. Please try again later.")
else:
    st.info("Please enter a company name to check.")