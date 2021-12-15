# stochastic_1_final_project_covid_modeling
Data and workbooks related to stochastic process 1 coursework. Topic of final project is modeling new covid cases in 6 countries.

## Files
**Covid_EDA.ipynb**: Exploratory data analysis on covid daily count of new cases dataset

**data_prep.ipynb**: Initial data prep for model building. This output would be read into an R program for data modeling process

**owid-covid-data.csv.zip**: Zipped file that contains initial dataset downloaded from https://ourworldindata.org/covid-deaths

**covid_cases_prepped.csv**: Output of data_prep.ipynb Data is imputed, cleaned, shrunken, and encoded. This will be read in by modeling program.

**covid_count_model_and_evaluation.R**: Feature selection, model building, and model evalution of covid count data.
