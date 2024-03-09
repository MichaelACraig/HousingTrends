# Small script to append ip to the port for proxy access
import pandas as pd

# Read the csv file
df = pd.read_csv('Free_Proxy_List.csv')

# Append the ip to the port
df['ip_port'] = df['ip'] + ':' + df['port'].astype(str)

# Save the new dataframe to a new csv file
df['ip_port'].to_csv('List.csv', index=False)
