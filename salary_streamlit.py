import streamlit as st
import pandas as pd
import utils

##################################################################################################
# Data Pull
## Teleport API
url = "https://api.teleport.org/api"

# Get Continents
continents = utils.get_continents(base_url=url)

## Get Countries in Continents
countries = continents["continent_id"].\
    apply(func=lambda x: utils.get_countries(base_url=url, continent_id=x))
countries = pd.concat(list(countries))
countries.reset_index(inplace=True)
##################################################################################################

# Title
st.title("Salary Analysis App")

# Side panel
st.sidebar.selectbox(
    label="Pick a continent to analyze",
    options=continents.name,
    key="continent_name"
)

st.sidebar.select_slider(
    label="Filter to a random number of countries",
    options=range(5, 100, 1),
    key="top_countries"
)

st.sidebar.checkbox(
    label="Show raw data",
    key="show_raw"
)

st.sidebar.button(
    label="Pull Data",
    key="pull_data"
)

# Raw data
if st.session_state.show_raw:
    st.subheader("Continents")
    st.write(continents)
    st.subheader("Countries")
    st.write(countries)

if st.session_state.pull_data:
    # Data Manipulation with stream lit
    cont_id_list = (continents.loc[continents['name'].isin([st.session_state.continent_name]), 'continent_id'])
    country_codes = list(countries.loc[countries['continent_id'].isin(cont_id_list), "country_id"])[
                    :st.session_state.top_countries]

    # Raw salary data
    salary = [utils.get_salaries(base_url=url, country_id=x) for x in country_codes]
    salary_df = pd.concat(salary)
    salary_df = salary_df.sort_values(by="salary_75_percentile", ascending=False)
    salary_df = salary_df. \
        merge(countries, how="inner", on="country_id"). \
        merge(continents, how="inner", on="continent_id", suffixes=["_country", "_continent"])

    # Aggregated: Average job salary by title
    job_salary_avg = salary_df \
        .groupby("job_id") \
        .agg(Median_salary=("salary_50_percentile", "median")) \
        .reset_index()

    # Aggregated: Average job salary by country
    country_salary_avg = salary_df \
        .groupby("name_country") \
        .agg(Median_salary=("salary_50_percentile", "median")) \
        .reset_index()

    # Visuals
    st.bar_chart(
        data=job_salary_avg,
        x="job_id",
        y="Median_salary"
    )

    st.bar_chart(
        data=country_salary_avg,
        x="name_country",
        y="Median_salary"
    )

    # kde = px.histogram(
    #     data_frame=salary_df,
    #     x="salary_50_percentile",
    #     hover_data=salary_df.columns
    # )
    #
    # kde.update_layout(
    #     title="Salary Distribution",
    #     xaxis_title="Median Salary",
    #     yaxis_title="Count"
    # )
    #
    # st.plotly_chart(
    #     kde
    # )
