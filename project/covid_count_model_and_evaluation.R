# Packages
install.packages('spaMM', dependencies = TRUE)
install.packages('Rcpp', dependencies = TRUE)

# Libraries
library(MASS)
library(spaMM)
library(olsrr)
library(boot)

# Read in data and remove index
df_covid_cases = read.csv("~/Documents/school/Stochastics/project/covid_cases_prepped.csv")
df_covid_cases = df_covid_cases[-c(1)]

# Check data
head(df_covid_cases)
df_cor = cor(df_covid_cases)
print(df_cor)

# Removing country names -> REMOVE AND MOVE TO PYTHON CODE?
# Country that would make this region specific rather than a general model to fit the pandemic
df_covid_cases_general = df_covid_cases[,-which(names(df_covid_cases) %in% c("CAN",'USA','GBR','IND','KOR','SWE'))]

# Checking dispersion
new_sample_var <- var(df_covid_cases_general$new_cases)
new_sample_mean <- mean(df_covid_cases_general$new_cases)
new_sample_sd <- sd(df_covid_cases_general$new_cases)
disp <- new_sample_var/new_sample_mean
paste(c('Sample Dispersion:', disp,'Sample Variance:',new_sample_var,'Sample Mean:',new_sample_mean))

# Linear model
linear_model <- lm(new_cases ~ ., data = df_covid_cases_general)
summary(linear_model)
# Stepwise regression
linear_model_step <- ols_step_both_p(linear_model, pent=.1, prem=.1)
linear_model_step$model$coefficients
summary(linear_model_step$model)

# LM RESIDUAL ANALYSIS
# QQ plot
st_res_lm_step=rstudent(linear_model_step$model)
qqnorm(st_res_lm_step,
       ylab="Expected Normal Residual",
       xlab="Studentized Residuals",
       main="Linear Model Normal Probability Plot")
qqline(st_res_lm_step)

# Res vs Predicted
plot(predict(linear_model_step$model),st_res_lm_step, 
     main="Linear Model Residual vs Predicted Response",
     xlab="Predicted Response",
     ylab="Residual")
abline(h=0)

# Visualize linear model
plot(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)],
     predict(linear_model_step$model), 
     main="Linear Model Predicted and True Covid Counts",
     xlab="Days Covid Present",
     ylab="Count of New Cases")
points(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)], 
       df_covid_cases_general$new_cases[order(df_covid_cases_general$days_covid_present)], 
       col = 'red', 
       pch=16)


# Poisson GLM
poi_glm <- glm(abs(new_cases) ~ ., 
               data = df_covid_cases_general, 
               family = "poisson")
summary(poi_glm)

# Testing difference between deviance and null deviance
test_stat = with(poi_glm, null.deviance - deviance)
dof = with(poi_glm, df.null - df.residual)
p = pchisq(test_stat, dof, lower.tail = FALSE)

print(p)

# Stepwise regression
poi_glm_step <- stepAIC(poi_glm)
summary(poi_glm_step)

# Compute deviance residuals 
glm.diag.plots(poi_glm_step)

# Visualize Poisson Model
plot(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)],exp(predict(poi_glm_step)), 
     main="Poisson GLM Predicted and True Covid Counts",
     xlab="Days Covid Present",
     ylab="Count of Covid Cases",
     col='red')
points(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)], 
       df_covid_cases_general$new_cases[order(df_covid_cases_general$days_covid_present)], 
       col = 'black')

# Negative Binomial GLM
# Estimate theta (dispersion) parameter for Negative Binomial
theta_est <- (new_sample_mean^2)/(new_sample_var-new_sample_mean)
theta_est

# Run model
nb_glm <- glm(abs(new_cases) ~ ., 
              data = df_covid_cases_general, 
              family = negative.binomial(theta = theta_est, link = "log"))
summary(nb_glm)

# Testing difference between deviance and null deviance
test_stat = with(nb_glm, null.deviance - deviance)
dof = with(nb_glm, df.null - df.residual)
p = pchisq(test_stat, dof, lower.tail = FALSE)

print(p)

# Stepwise regression
nb_glm_step <- stepAIC(nb_glm)
summary(nb_glm_step)

# Compute deviance residuals 
glm.diag.plots(nb_glm_step)

# Visualize NB Model
plot(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)],exp(predict(nb_glm_step)), 
     main="Negative Binomial GLM Predicted and True Covid Counts",
     xlab="Days Covid Present",
     ylab="Count of Covid Cases",
     col='red')
points(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)], 
       df_covid_cases_general$new_cases[order(df_covid_cases_general$days_covid_present)], 
       col = 'black')

# COMPoisson Regression
# Estimating nu by relation on pg. 946
nu_est <- new_sample_mean/new_sample_var

# Run model
com_poi_glm <- glm(abs(new_cases) ~ ., data = df_covid_cases_general, family = COMPoisson(nu=new_sample_var))
summary(com_poi_glm)

# Stepwise regression
#com_poi_glm_step <- stepAIC(com_poi_glm)
step_df = df_covid_cases_general[,which(names(df_covid_cases_general) %in% c(names(poi_glm_step$coefficients),'new_cases'))]
com_poi_glm_step <-glm(abs(new_cases) ~ ., data = step_df, family = COMPoisson(nu=.7))
summary(com_poi_glm_step)

# Compute deviance residuals 
glm.diag.plots(com_poi_glm_step)

# Visualize COMPoisson Model
plot(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)],exp(predict(com_poi_glm_step)), 
     main="COM Poisson GLM Predicted and True Covid Counts",
     xlab="Days Covid Present",
     ylab="Count of Covid Cases",
     col='red')
points(df_covid_cases_general$days_covid_present[order(df_covid_cases_general$days_covid_present)], 
       df_covid_cases_general$new_cases[order(df_covid_cases_general$days_covid_present)], 
       col = 'black')


# Model comparisons
# AIC
lm_aic <- AIC(linear_model_step$model)
poi_aic <- AIC(poi_glm_step)
nb_aic <- AIC(nb_glm_step)
cpoi_aic <- AIC(com_poi_glm_step)
# MSE
model_summ <- summary(linear_model_step$model)
lm_mse <- mean(model_summ$residuals^2)
poi_mse <- mean(poi_glm_step$residuals^2)
nb_mse <- mean(nb_glm_step$residuals^2)
cpoi_mse <- mean(com_poi_glm_step$residuals^2)
