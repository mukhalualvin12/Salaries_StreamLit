import streamlit as st
import requests
import pandas as pd


# Get All continents
def get_data(your_url):
    try:
        response = requests.get(your_url)
        response_json = response.json()
        return response_json
    except Exception as e:
        print(f"This is the error from the url: {e}")


def get_continents(base_url):
    cont_url = "{url}/continents/".format(url=base_url)
    continents_json = get_data(cont_url)['_links']['continent:items']
    continents_df = pd.DataFrame(continents_json)
    continents_df["continent_id"] = continents_df["href"]. \
        str.replace(pat=cont_url, repl=""). \
        str.replace(pat="/", repl="")
    return continents_df

@st.cache_data
def get_countries(base_url, continent_id):
    country_url = "{url}/continents/{continent_id}/countries/".\
        format(url=base_url, continent_id=continent_id)
    country_json = get_data(country_url)['_links']['country:items']

    country_df = pd.DataFrame(country_json)
    country_df["country_id"] = country_df["href"]. \
        str.replace(pat="https://api.teleport.org/api/countries/", repl=""). \
        str.replace(pat="/", repl="")
    country_df["continent_id"] = continent_id

    return country_df

@st.cache_data
def get_salaries(base_url, country_id):
    salary_url = "{url}/countries/{country_id}/salaries".\
        format(url=base_url, country_id=country_id)
    salary_json = get_data(salary_url)['salaries']

    if len(salary_json) == 0:
        return pd.DataFrame() # return empty data frame

    print(f"Received data for {country_id}")

    salary_list = [pd.json_normalize(x) for x in salary_json]
    your_salary_df = pd.concat(salary_list)
    your_salary_df["country_id"] = country_id
    cols_corrected = ["job_id",
                      "title",
                      "salary_25_percentile",
                      "salary_50_percentile",
                      "salary_75_percentile",
                      "country_id"]
    your_salary_df.columns = cols_corrected
    return your_salary_df

##############################################################


