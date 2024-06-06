import bedrock_agent
import json
import re
import time
# Function to parse and format response


if __name__ == '__main__':


    chart_request_list = [
        "Displays the number of works orders assigned to each vendor",
        "Displays the number of works orders assigned to each staff member",
        "Shows the percentage of works orders completed",
    ]
    query_request_list = [
        "61 is ‘Sample Co’",
        "5 contains Ragnar",
        "5 contains Ragnar and 7 contains Aquisitions"
        ]
    b_chart = True
    request_list = []
    if b_chart:
        request_list = chart_request_list
    else:
        request_list = query_request_list
    for request in request_list:
        # Record the start time
        start_time = time.time()
        event = {
            "sessionId": "MYSESSION",
            "question": request
        }
        response = bedrock_agent.lambda_handler(event, None)
        # Record the end time
        end_time = time.time()
        # Calculate the difference
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")


        try:
            # Parse the JSON string
            if response and 'body' in response and response['body']:
                response_data = json.loads(response['body'])

            else:
                print("Invalid or empty response received")
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            response_data = None 
        
        try:
            # Extract the response and trace data
            trace_data = response_data['trace_data']
            print(f'===============trace_data {trace_data}')
            
            b_save_json = False
            if b_chart and b_save_json:
                # Force all keys and text values into double quotes
                valid_json_str = re.sub("(\w+):", r'"\1":', trace_data) # add double quotes to keys
                valid_json_str = re.sub(": ([\w\s]+)([,\n])", r': "\1"\2', valid_json_str) # add double quotes to text values

                # Load it as JSON
                json_data = json.loads(valid_json_str)

                with open('trace_data.json', 'w') as f:
                    json.dump(json_data, f)
        except:
            all_data = "..." 
            the_response = "Apologies, but an error occurred. Please rerun the application" 