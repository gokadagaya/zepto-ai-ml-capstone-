# Module 2 — Analytics Pipeline

## 1. Project Overview

This module performs exploratory data analysis and machine learning on the Titanic dataset.

The objective is to understand the factors associated with passenger survival, identify patterns in the data, visualize important relationships, and build machine learning models for classification and regression.

The analysis follows this workflow:

Load data → Clean data → Explore data → Visualize patterns → Preprocess features → Train models → Evaluate models → Tune the best model → Save the final pipeline


## 2. Dataset

The Titanic dataset is obtained using Seaborn's built-in Titanic dataset.

The dataset was loaded only once using:

`sns.load_dataset("titanic")`

Immediately after loading, the raw dataset was saved locally as:

`analytics/titanic.csv`

This file acts as the offline fallback dataset.

The modeling notebook does not download the Titanic dataset again. It reads the locally saved CSV file instead.


## 3. Project Structure

The analytics module is organized as follows:

analytics/

├── 01_eda.ipynb  
├── 02_modeling.ipynb  
├── titanic.csv  
├── titanic_cleaned.csv  
├── README.md  
│  
├── models/  
│   └── best_pipeline.joblib  
│  
└── outputs/  
    ├── charts/  
    ├── tables/  
    ├── eda_summary.txt  
    └── modeling_summary.txt  


## 4. Data Profiling

The initial dataset was inspected using:

- `df.shape`
- `df.info()`
- `df.describe()`
- column-level missing-value counts
- column-level missing-value percentages

The dataset contains passenger information such as passenger class, age, sex, family information, fare, embarkation details, and survival status.


## 5. Missing-Value Handling

Missing values were handled based on their percentage of the dataset.

### High missingness

The `deck` column contained a very high percentage of missing values. Instead of attempting to impute such a large proportion of missing observations, the column was removed.

### Medium missingness

The `age` column had a moderate amount of missing data. Missing age values were replaced using the median age.

Median imputation was selected because age can contain extreme values and the median is less sensitive to outliers than the mean.

### Low missingness

The `embarked` column had only a very small number of missing observations. These rows were removed according to the defined missing-value threshold.

`embark_town` was also removed because it provides information corresponding to the `embarked` variable and is therefore redundant for the analysis.

After cleaning, the dataset was checked again to confirm that no missing values remained.


## 6. Univariate Analysis

Univariate analysis was performed on `age` and `fare`.

The following visualizations were created:

- Age histogram
- Age box plot
- Fare histogram
- Fare box plot

The IQR method was used to identify potential outliers.

An observation was considered an outlier when it was below:

Q1 - 1.5 × IQR

or above:

Q3 + 1.5 × IQR

The number of detected outliers was calculated separately for age and fare.

The fare distribution was also analyzed using:

- Mean
- Median
- Mode
- Skewness

The distribution was interpreted using the relationship between the mean, median, and mode together with the histogram.


## 7. Bivariate Analysis

Survival rates were analyzed across:

- Sex
- Passenger class
- Sex and passenger class together

The results were saved in:

`outputs/tables/survival_by_sex_class.csv`

The analysis helps identify differences in survival outcomes between passenger groups.


## 8. Correlation Analysis

A correlation matrix was created using the following six numerical variables:

- `survived`
- `pclass`
- `age`
- `sibsp`
- `parch`
- `fare`

The correlation matrix was visualized using a heatmap.

The resulting files are:

`outputs/tables/correlation_matrix.csv`

and

`outputs/charts/correlation_heatmap.png`

The correlation values were used to identify the strongest positive and negative relationships between the selected variables.


## 9. Multivariate Analysis

Multiple variables were analyzed together to identify more meaningful patterns.

The following charts were created:

1. Survival rate by passenger class and sex
2. Age distribution by sex and survival
3. Fare distribution by passenger class and survival
4. Age, fare, passenger class, and survival scatter plot

These visualizations were selected because they examine interactions between multiple passenger characteristics rather than looking at variables independently.


## 10. Standardization

Standardization was demonstrated using `StandardScaler` on the `age` and `fare` variables.

After transformation, the standardized variables had means approximately equal to zero and population standard deviations approximately equal to one.

Standardization is also included inside the machine learning preprocessing pipeline for numerical features.


## 11. Machine Learning Objective

Two machine learning tasks were performed.

### Classification

The classification target is:

`survived`

The objective is to predict whether a passenger survived.

### Regression

The regression target is:

`fare`

The objective is to predict passenger fare using the remaining selected passenger characteristics.


## 12. Feature Selection

For classification, the following features were used:

### Numerical features

- `pclass`
- `age`
- `sibsp`
- `parch`
- `fare`

### Categorical features

- `sex`
- `embarked`

The `survived` column was used only as the target.

Columns such as `alive` were excluded because they contain information directly representing the survival outcome and could cause target leakage.

Other redundant Titanic representation columns were also excluded from the modeling feature set.


## 13. Train/Test Split

The classification dataset was divided into training and testing sets using an 80/20 split.

A fixed `random_state=42` was used to make the results reproducible.

Stratification was applied using the target variable so that the proportion of survivors and non-survivors remained approximately consistent between the training and testing datasets.


## 14. Preprocessing Pipeline

A `ColumnTransformer` was used to handle numerical and categorical features separately.

### Numerical preprocessing

The numerical preprocessing pipeline consists of:

1. Median imputation
2. StandardScaler

### Categorical preprocessing

The categorical preprocessing pipeline consists of:

1. Most-frequent-value imputation
2. OneHotEncoder

`handle_unknown="ignore"` was used with the encoder so that unseen categories in the test data do not cause errors.

All preprocessing steps were included inside the machine learning Pipeline to prevent data leakage.


## 15. Classification Models

Three baseline classification models were trained:

### Logistic Regression

Logistic Regression was used as a simple linear classification baseline.

### Decision Tree

A Decision Tree classifier was trained to capture non-linear relationships between features.

### Random Forest

A Random Forest classifier was trained using multiple decision trees to improve predictive performance and robustness.


## 16. Classification Evaluation

The classification models were evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

The results were saved in:

`outputs/tables/classification_model_comparison.csv`

The final comparison was saved in:

`outputs/tables/final_classification_comparison.csv`


## 17. Class Imbalance Analysis

The target distribution was checked before model evaluation.

A baseline Random Forest model was compared with a class-weighted Random Forest using:

`class_weight="balanced"`

This comparison was used to determine whether accounting for the class distribution affected classification performance, particularly recall, F1 score, and ROC-AUC.


## 18. Hyperparameter Tuning

GridSearchCV was used to tune the Random Forest model.

The parameters considered included:

- Number of trees (`n_estimators`)
- Maximum tree depth (`max_depth`)
- Minimum samples required for a split (`min_samples_split`)
- Class weighting (`class_weight`)

Five-fold cross-validation was used.

ROC-AUC was used as the GridSearchCV scoring metric.

The best parameters and cross-validation results were saved for reference in:

`outputs/tables/random_forest_gridsearch_results.csv`


## 19. Regression

Linear Regression was used to predict `fare`.

The `fare` column was removed from the input features and used as the regression target.

The regression model was evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R²

The results were saved in:

`outputs/tables/regression_results.csv`


## 20. Residual Analysis

Residuals were calculated as:

Actual Fare - Predicted Fare

A residual plot was created to check the distribution of prediction errors.

The chart was saved as:

`outputs/charts/fare_residuals.png`

The residual analysis was used to assess whether the Linear Regression model showed systematic prediction errors.


## 21. Final Model

The best Random Forest pipeline identified through GridSearchCV was saved using `joblib`.

The saved model is:

`models/best_pipeline.joblib`

The saved object contains both the preprocessing steps and the trained model, allowing the complete workflow to be reused without manually repeating the preprocessing.


## 22. Output Files

### Charts

The `outputs/charts/` directory contains:

- `age_histogram.png`
- `age_boxplot.png`
- `fare_histogram.png`
- `fare_boxplot.png`
- `correlation_heatmap.png`
- `survival_sex_class.png`
- `age_sex_survival.png`
- `fare_class_survival.png`
- `age_fare_class_survival.png`
- `fare_residuals.png`

### Tables

The `outputs/tables/` directory contains:

- `survival_by_sex_class.csv`
- `correlation_matrix.csv`
- `classification_model_comparison.csv`
- `random_forest_gridsearch_results.csv`
- `final_classification_comparison.csv`
- `regression_results.csv`

Additional summaries are stored in:

- `eda_summary.txt`
- `modeling_summary.txt`


## 23. Installation

From the project root, install the required Python packages:

```bash
pip install pandas seaborn matplotlib scikit-learn imbalanced-learn joblib