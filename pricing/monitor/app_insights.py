from typing import List
from datetime import timedelta
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient, MetricAggregationType

APP_INSIGHTS_RESOURCE_ID = ""

def get_app_insight_metrics(creds: DefaultAzureCredential, resource_id: str) -> List[any]:
    """
    Retrieves the application insights metrics for a given resource.

    Args:
        creds (DefaultAzureCredential): The Azure credentials used for authentication.
        resource_id (str): The resource ID of the application insights instance.

    Returns:
        list: A list of application insights metrics for the last 30 days.
    """
    query_client = MetricsQueryClient(creds)

    # Query the metrics for the last 30 days
    return query_client.query_resource(
        resource_uri=resource_id,
        metric_names=["traces/count"],
        timespan=timedelta(days=30))

def get_app_insight_logs(creds: DefaultAzureCredential, resource_id: str) -> List[any]:
    """
    Retrieves application insight logs for the specified resource ID.

    Args:
        creds (DefaultAzureCredential): The Azure credentials used for authentication.
        resource_id (str): The ID of the resource to query logs for.

    Returns:
        List[str]: A list of log messages matching the specified criteria.
    """
    log_client = LogsQueryClient(creds)

    # Query the logs for the last 30 days
    return log_client.query_resource(
        resource_id=resource_id,
        query="""traces 
        | project message, timestamp, cloud_RoleName 
        | where timestamp > ago(30d) 
        | where message contains 'tokens'
        """,
        timespan=timedelta(days=30)
    )

def calculate_aoai_cost():
    """
    This script queries metrics and logs from Azure Application Insights and calculates 
    the cost of input and output tokens.
    """

    # Endpoint that's required for some Metric queries. 
    # Pattern is <region>.metrics.monitor.azure.com or <region>.monitoring.azure.com
    # For example, if your region is East US 2, the endpoint is eastus2.metrics.monitor.azure.com
    # metrics_endpoint = "https://eastus2.metrics.monitor.azure.com/"

    credential = DefaultAzureCredential()
    function_insights_resource_id = APP_INSIGHTS_RESOURCE_ID

    # Print the metrics
    try:
        for metric in get_app_insight_metrics(credential, function_insights_resource_id).metrics:
            print(metric.name)
            for time_series_element in metric.timeseries:
                for metric_value in time_series_element.data:
                    if metric_value.count != 0:
                        print(
                            "There are {} matched events at {}".format(
                                metric_value.count,
                                metric_value.timestamp
                            )
                        )
    
    except Exception as e:
        print(f"An error occurred: {e}")

    # Print the logs and extract the tokens into variables
    aggregate_input_tokens = 0
    aggregate_output_tokens = 0

    try:
        for log in get_app_insight_logs(credential, function_insights_resource_id).tables[0].rows:
            total_tokens = 0
            completion_tokens = 0
            prompt_tokens = 0

            # Extract numbers from the string
            numbers = [int(num) for num in log[0].split() if num.isdigit()]

            # Assign numbers to variables
            total_tokens = numbers[0]
            completion_tokens = numbers[1]
            prompt_tokens = numbers[2]

            # Aggregate the total tokens
            aggregate_input_tokens += prompt_tokens
            aggregate_output_tokens += completion_tokens

            print(f"Timestamp: {log[1]} | Total tokens: {total_tokens} | Completion tokens: {completion_tokens} | Prompt tokens: {prompt_tokens}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

    # Assuming GPT4-Turbo $0.01 input and $0.03 output per 1000 tokens
    print(f"""
    Total input tokens cost: ${aggregate_input_tokens/1000*0.01}
    Total output tokens cost: ${aggregate_output_tokens/1000*0.03}
    """)

def main():
    calculate_aoai_cost()

if __name__ == "__main__":
    main()
