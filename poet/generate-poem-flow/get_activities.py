from promptflow import tool
import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import StringIO

# Azure Blob Storage account details
connection_string = 'your_connection_string_here'
container_name = 'your_container_name_here'
blob_name = 'your_blob_name_here'

# Create a BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get the BlobClient
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Download the blob content as a string
blob_data = blob_client.download_blob().content_as_text()

# Convert the blob content to a pandas DataFrame
df = pd.read_csv(StringIO(blob_data))

@tool
def get_activities(city_name):
    result = df.loc[df.iloc[:, 0] == city_name, df.columns[1]].values
    if len(result) > 0:
        return result[0]
    else:
        return "No data retrieved for this city."