import pandas as pd

# Load 2020.csv file
df_2020 = pd.read_csv('2020.csv')

# Extract column names from 1 to 100 and create a list
col_names_2020 = df_2020.columns[1:101].tolist()

# Load 2021.csv file
df_2021 = pd.read_csv('2021.csv')

# Extract column names from 1 to 100 and create a list
col_names_2021 = df_2021.columns[1:101].tolist()

# Find common column names between 2020 and 2021
common_col_names = list(set(col_names_2020) & set(col_names_2021))

# Print the lists
print("2020.csv column names: ", col_names_2020)
print("2021.csv column names: ", col_names_2021)
print("Common column names: ", common_col_names)
