##### Data Prep for Covid Count of New Cases Data Modeling

# Libraries
import pandas as pd
import numpy as np
import datetime as dt

### Data Read In ###
# Data
covid_df = pd.read_csv('owid-covid-data.csv')

# Subset to useable data
covid_model_df = covid_df[covid_df['location'].isin(['United States','South Korea',\
                                                     'Sweden', 'Canada', 'India', 'United Kingdom'])]


print(covid_model_df.shape)

### Data Transformations ###
# Column list
print(covid_model_df.columns.to_list())

# Set date to datetime
covid_model_df['date'] = pd.to_datetime(covid_model_df['date'])

# Drop unecessary columns
# All smoothing columns were dropped to maintain original interpretations. 
# Any scaled values were removed (per million) since standardization will render it useless
covid_model_df.drop(columns = [ 'continent', 'location', 'new_cases_smoothed', 'new_deaths_smoothed',\
                                'total_cases_per_million','new_cases_per_million', 'new_cases_smoothed_per_million',\
                                'total_deaths_per_million','new_deaths_per_million',\
                                'new_deaths_smoothed_per_million', 'icu_patients_per_million',\
                                'hosp_patients_per_million', 'weekly_icu_admissions_per_million',\
                                'weekly_hosp_admissions_per_million','total_tests_per_thousand',\
                                'new_tests_per_thousand', 'new_tests_smoothed', 'new_tests_smoothed_per_thousand',\
                                'new_vaccinations_smoothed', 'total_vaccinations_per_hundred',\
                                'people_vaccinated_per_hundred','people_fully_vaccinated_per_hundred',\
                                'total_boosters_per_hundred','new_vaccinations_smoothed_per_million',\
                                'new_people_vaccinated_smoothed', 'new_people_vaccinated_smoothed_per_hundred',\
                                'excess_mortality_cumulative_absolute','excess_mortality_cumulative',\
                                'excess_mortality_cumulative_per_million',\
                                # Dropped due to no datapoints at some countries
                               'handwashing_facilities','weekly_icu_admissions', 'weekly_hosp_admissions'\
                              ], inplace = True)

# Create days since first covid case variable
# Find minimum days where field is not null - transform method does not work
min_covid_dt = covid_model_df[covid_model_df['total_cases'].isna() == False].groupby('iso_code')['date'].min()
min_covid_dt.rename('min_covid_dt', inplace = True)
     
# Merge minimum days on to main dataframe
covid_model_df = pd.merge(covid_model_df, min_covid_dt, how = 'left',right_index = True, left_on = 'iso_code')

# Calculate days covid present
covid_model_df['days_covid_present'] = (pd.to_datetime(covid_model_df['date']) - \
                                        pd.to_datetime(covid_model_df['min_covid_dt'])).dt.days

# Drop minimum covid date
covid_model_df.drop(columns = ['min_covid_dt'], inplace = True)

# Month of positive test
covid_model_df['month'] = covid_model_df['date'].dt.month

# Covid year of positive test - years since 2020
covid_model_df['year'] = (covid_model_df['date'].dt.year-2019)

# Remove current days new amount from total columns
covid_model_df['total_cases'] = covid_model_df['total_cases'] - covid_model_df['new_cases']
covid_model_df['total_deaths'] = covid_model_df['total_deaths'] - covid_model_df['new_deaths']
covid_model_df['total_tests'] = covid_model_df['total_tests'] - covid_model_df['new_tests']
covid_model_df['total_vaccinations'] = covid_model_df['total_vaccinations'] - covid_model_df['new_vaccinations']

print(covid_model_df.head())

# Imputate - groups with only nulls
print(covid_model_df.columns[covid_model_df.isna().any()].tolist())

# Total Test cleaning
# Total is sum of all previous days test amount
covid_model_df.loc[covid_model_df['iso_code'] == 'SWE','total_tests']\
    = covid_model_df[covid_model_df['iso_code'] == 'SWE'].sort_values('date')['new_tests'].cumsum()

# Booster cleaning
# No boosters have begun being given out in India
covid_model_df.loc[covid_model_df['iso_code'] == 'IND','total_boosters']= 0

# Sweden working under assumption it gave no boosters out. Data/research still pending
covid_model_df.loc[covid_model_df['iso_code'] == 'SWE','total_boosters'] = 0

# Fill in India excess mortality with daily average across countries, no data available
covid_model_df.loc[covid_model_df['iso_code'] == 'IND', ['excess_mortality']]\
= covid_model_df.groupby('date')['excess_mortality'].transform('mean')

# Impute - groups with some nulls
# Types of imputing
fill_0_cols = ['total_cases','new_cases', 'total_deaths', 'new_deaths','total_vaccinations','new_tests',\
               'positive_rate','tests_per_case','people_vaccinated','people_fully_vaccinated','total_boosters',\
               'new_vaccinations','total_tests']
mean_cols = ['reproduction_rate','icu_patients','hosp_patients','new_tests','positive_rate','tests_per_case',\
             'new_vaccinations','stringency_index', 'excess_mortality']
forward_fill_cols = ['total_tests','total_vaccinations','people_vaccinated','people_fully_vaccinated',\
                     'total_boosters']


# Columns that need to be turned to 0 if before first occurrence of a value
# This is run first so that columns can be filled with 0 before min and other methods after
for col in fill_0_cols:
    # Find minimum days where field is not null
    min_dt = covid_model_df[covid_model_df[col].isna() == False].groupby('iso_code')['date'].min()
    min_dt.rename('min_dt', inplace = True)
        
    # Merge minimum days on to main dataframe
    covid_model_df = pd.merge(covid_model_df, min_dt, how = 'left',right_index = True, left_on = 'iso_code')
   
    # Set any null row before minimum date to 0
    covid_model_df.loc[(covid_model_df[col].isna() == True) &\
                       (pd.to_datetime(covid_model_df['date']) < pd.to_datetime(covid_model_df['min_dt'])),col] = 0

    # Drop minimum date field
    covid_model_df.drop(columns=['min_dt'], inplace = True)

# Columns to be filled with mean
for col in mean_cols:
    covid_model_df[col] = covid_model_df.groupby('iso_code')[col].transform(lambda x: x.fillna(x.mean()))
    
# S. Korea and India were missing all hospital information. Filled in with overall mean
covid_model_df.loc[(covid_model_df['icu_patients'].isna() == True) &\
                   (covid_model_df['iso_code'].isin(['IND','KOR'])),'icu_patients']\
                = covid_model_df['icu_patients'].mean()
covid_model_df.loc[(covid_model_df['hosp_patients'].isna() == True) &\
                   (covid_model_df['iso_code'].isin(['IND','KOR'])),'hosp_patients']\
                = covid_model_df['hosp_patients'].mean()


# Columns to be filled with last valid value
for col in forward_fill_cols:
    covid_model_df[col] = covid_model_df.groupby('iso_code')[col].transform(lambda x: x.fillna(method = 'ffill'))

# Character columns fill with not present
covid_model_df['tests_units'].fillna('Missing Tests Units', inplace = True)

# Drop date column, no longer used
covid_model_df.drop(columns = ['date'], inplace = True)

# Encode features
# Tests units
dummies = pd.get_dummies(covid_model_df['tests_units'])
encoded_covid_model_df = pd.concat([covid_model_df, dummies], axis=1)
encoded_covid_model_df.drop(['tests_units'],inplace=True,axis=1)

# ISO code
dummies = pd.get_dummies(covid_model_df['iso_code'])
encoded_covid_model_df = pd.concat([encoded_covid_model_df, dummies], axis=1)
encoded_covid_model_df.drop(['iso_code'],inplace=True,axis=1)

print(encoded_covid_model_df.head(40))

# Correlation Heatmap
import seaborn as sb
import pandas as pd
corr1=encoded_covid_model_df.corr()
sb.heatmap(corr1, 
           xticklabels=corr1.columns,
           yticklabels=corr1.columns) 

### Output Data for Read In ###
encoded_covid_model_df.to_csv('covid_cases_prepped.csv')






