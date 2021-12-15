##### Exploratory Data Analysis for Covid Count of New Cases Data Modeling

# Libraries
import pandas as pd 
import matplotlib.pyplot as plt

# Data input
covid_df = pd.read_csv('owid-covid-data.csv')

#######
# EDA #
#######

# Rows and variable count
print('Rows: ', covid_df.shape[0])
print('Columns: ', covid_df.shape[1])

print(covid_df.head())

# List of all columns
print(covid_df.columns.to_list())

# Date range
print(covid_df['date'].agg([min,max]))

## Location Investigations
# Top 5 countries with data
print(covid_df['location'].value_counts().sort_index().nlargest(5))

# Top 5 locations by 
print(covid_df.groupby(['location'], as_index = False)['new_cases']\
                .agg(sum).sort_values(by = 'new_cases')\
                .nlargest(5, columns = 'new_cases'))

# Continents prevalence
print(test_df['continent'].value_counts())

# Unique countries
print('Total Unique Countries: ', covid_df['location'].nunique())
print(covid_df['location'].unique())

# North American countries - Could use just the similar area
print(covid_df[covid_df['continent'] == 'North America']['location'].value_counts())

# Investigating what income based location fields look like
print(test_df[test_df['location']=='Upper middle income'].head())

# US specific investigation
us_df = covid_df[covid_df['location'] == 'United States']

print(us_df[us_df['date'] >='2020-03-01'].head(10))

# Value counts for just USA
# Shows certain columns are same value repeated
for col in us_df.columns:
    print(col)
    print(us_df[col].value_counts())

# Total Case and NaN progression
print(us_df.sort_values(by='date').head(20))

# Removing unecessary columns
covid_shrunk_df = covid_df[['iso_code',\
 'date',\
 #'total_cases'(MAYBE?),\
 'new_cases',\
 #'total_deaths'(MAYBE? SUBTRACT NEW DEATHS),\
 #'new_deaths'(MAYBE?),\
 'reproduction_rate',\
 'icu_patients',\
 'hosp_patients',\
 'weekly_icu_admissions',\
 'weekly_hosp_admissions',\
 'new_tests',\
 #'total_tests'(MAYBE? - HIGH TESTS COULD MEAN MORE LIKELY TO FIND),\
 'positive_rate',\
 'tests_per_case',\
 'tests_units',\
 'total_vaccinations',\
 'people_vaccinated',\
 'people_fully_vaccinated',\
 'total_boosters',\
 'new_vaccinations',\
 'stringency_index',\
 'population',\
 'population_density',\
 'median_age',\
 'aged_65_older',\
 'aged_70_older',\
 'gdp_per_capita',\
 'extreme_poverty',\
 'cardiovasc_death_rate',\
 'diabetes_prevalence',\
 'female_smokers',\
 'male_smokers',\
 'handwashing_facilities',\
 'hospital_beds_per_thousand',\
 'life_expectancy',\
 'human_development_index',\
 'excess_mortality']]

print(covid_shrunk_df.head(40))

print(covid_shrunk_df['iso_code'].value_counts())

# Only countries with over 600 rows of data
covid_shrunk_df[covid_shrunk_df['iso_code'].isin(covid_shrunk_df['iso_code'].value_counts().reset_index(name="count").query("count > 600")["index"])]

# World only
print(covid_df[covid_df['location'] == 'World'].head(50))

# Minimum Date where total cases over 1
min_dates = covid_df[covid_df['total_cases']>0.0].groupby('location')['date'].min()

print(min_dates)

# Max Date where total cases unreported
# This is effectively last date before had first case since it is cumulative
max_missing_dates = covid_df[covid_df['total_cases'].isna()].groupby('location')['date'].max()

print(max_missing_dates)

# Base stats on new cases
covid_df['new_cases'].describe()

# Countries with first reported cases in the data
# Top countries sorted by average daily new cases
df2=covid_df[covid_df['location'].isin(\
                                   covid_df[(covid_df['total_cases'].isna()) | (covid_df['total_cases']==1)]\
                                   ['location'].unique())\
        ].groupby('location')['new_cases'].mean().sort_values(ascending = False)

df2.head(30)

covid_df[covid_df['new_cases'] < 0.0]['location'].unique()

covid_df[covid_df['new_cases'] > 0.0]['new_cases'].describe()

print(covid_df[covid_df['location'] == 'South Korea'].sort_values(by='date'))

print(covid_df[covid_df['location'] == 'United Kingdom'].sort_values(by = 'date'))

# Columns to drop investigation
covid_df[covid_df['excess_mortality'].isna()==False][['iso_code','date','excess_mortality_cumulative_absolute',
 'excess_mortality_cumulative',
 'excess_mortality',
 'excess_mortality_cumulative_per_million']].sort_values(by=['iso_code','date'])

# Plot of new cases over time
covid_df.groupby('date')['new_cases'].sum().plot()

# Plot for each country in chosen model dataframe
for country in ['CAN', 'IND', 'KOR', 'SWE', 'GBR', 'USA']:
    plt.title(f'Daily New Cases for {country}')
    covid_df[covid_df['iso_code'] == country].groupby('date')['new_cases'].sum().plot()
    plt.show()








