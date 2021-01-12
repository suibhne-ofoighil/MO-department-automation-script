import pandas as pd

#read in the raw data
while True:
    try:
        user_in = input('Enter the source filename (without the csv extension):')
        #take this out ~ it made opening the file faster
        if len(user_in) < 1: 
            user_in = 'MO503_newdata'
        print('Recieved "{}"'.format(user_in))
        file = user_in + '.csv'
        print('Opening "{}"'.format(file))
        df = pd.read_csv(file, engine='python', skiprows = [1,2])
        break
    except:
        print('Error accessing source file. Try again.')

#read in the data structure
while True:
    try:
        user_in = input ('Enter data structure (with the xlsx extention):')
        #take this out ~ same reason as above
        if len(user_in) < 1: 
            user_in = 'Data structure MO503'
        print('Recieved "{}"'.format(user_in))
        file = user_in + '.xlsx'
        print('Opening "{}"'.format(file))
        data_structure = pd.read_excel(file)
        break
    except:
        print('Error accessing data structure file. Try again.')
        


#keep certain columns, eg. name, or UMID
df["Name"] = df["FirstName"] + " " + df["LastName"]
cols_to_keep = df[["Name","Email","MO503Section","UMID","Uniqname"]].copy()
cols_to_keep.rename(columns = {"Email" : "EmailAddress"}, inplace = True)


#keep track of index columns in data_structure xlsx --> to iterate later
name_index = data_structure.columns.get_loc('Rename')
decimal_index = data_structure.columns.get_loc('Decimals')
col_index = data_structure.columns.get_loc('Data')


#calculate the individual statistics, "df_1"
cols_for_calc = []
for index, row in data_structure.iterrows():
    lst = [k for k in row if not k != k]
    name = lst[name_index]
    decimal = lst[decimal_index]
    col_for_calc = lst[col_index:]
    cols_for_calc.append((name, decimal, col_for_calc))
cols_to_add = pd.DataFrame()
for name, decimal, cols in cols_for_calc:
    if 'mean' in name.lower():
        cols_to_add[name] = df[cols].T.mean().round(decimal)
    elif 'sd' in name.lower():
        cols_to_add[name] = df[cols].T.std().round(decimal)
    else:
        cols_to_add[name] = df[cols]

#concatonate 'kept columns' with individual statistics, "df_1"
df_1 = pd.concat([cols_to_keep, cols_to_add], axis = 1)


#get the data ready for calculating section statistics, "df_2"
df_2_stats = df_1.groupby(['MO503Section']).mean().round(1)
df_2_stats = df_2_stats.drop(['UMID', 'Uniqname'], axis = 1)


df_2 = pd.DataFrame()

#calculate section statistics, "df_2"
for col in df_2_stats:
    label = col[:-1] + '2'
    df_2[label] = pd.Series([df_2_stats.at[section_num, col] for section_num in df_1['MO503Section']])
    

df_3 = pd.DataFrame()

#calculate class-wide statistics, "df_3"
for col in cols_to_add:
    series = cols_to_add[col]
    mean = series.mean()
    label = col[:-1] + '3'
    df_3[label] = [mean for i in range(series.size)]
df_3 = df_3.round(1)


#create the final data frame by combining df_1, df_2, & df_3
final_df = pd.concat([df_1, df_2, df_3], axis = 1)


# export the final data frame to a csv
# MUST CREATE A NEW CSV FILE + EDIT SCRIPT \/ WITH CORRECT NAME
final_df.to_csv('MO503_newdata_finaloutput.csv', index=False)
