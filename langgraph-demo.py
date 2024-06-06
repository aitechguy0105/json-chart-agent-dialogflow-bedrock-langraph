import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from typing import List, Sequence
import time
from langgraph.graph import END, MessageGraph

import os
from dotenv import load_dotenv
import logging
import getpass
# Set up the system template with a variable for context
load_dotenv()

def _set_if_undefined(var: str) -> None:
    if os.environ.get(var):
        return
    os.environ[var] = getpass.getpass(var)
# Optional: Configure tracing to visualize and debug the agent
# _set_if_undefined("LANGCHAIN_API_KEY")
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "Reflection"


# _set_if_undefined("FIREWORKS_API_KEY")

quickbase_chart_example = """
user: Displays the number of works orders by status.
answer:
    {
        "chartType": "bar",
        "description": "Displays the number of works orders by status",
        "groupBy": {
            "field": "Works Order Status"
        },
        "name": "Works Orders by Status",
        "table": "Works Orders",
        "yAxes": [
            {
                "aggregateFunction": "count"
            }
        ]
    }
user: Displays the trend of works orders created over time
answer: 
    {
        "chartType": "line",
        "description": "Displays the trend of works orders created over time",
        "groupBy": {
            "field": "Start Date",
            "grouping": "month"
        },
        "name": "Works Orders Created Over Time",
        "table": "Works Orders",
        "yAxes": [
            {
                "aggregateFunction": "count"
            }
        ]
    }
user: Shows the percentage of works orders completed
answer:
    {
        "chartType": "pie",
        "description": "Shows the percentage of works orders completed",
        "groupBy": {
            "field": "Percentage complete"
        },
        "name": "Works Orders Completion Percentage",
        "table": "Works Orders",
        "yAxes": [
            {
                "aggregateFunction": "count"
            }
        ]
    }
"""
quickbase_query_example = """
User Request: 61 is ‘Sample Co’	
Answer: query=({'61'.EX.'Sample+Co'})
User Request: 5 contains Ragnar	
Asnwer: query=({'5'.CT.'Ragnar'})
User Request: 5 contains Ragnar and 7 contains Aquisitions
Asnwer:	query=({'5'.CT.'Ragnar Lodbrok'}AND{'7'.CT.'Acquisitions'})
User Request: 5 contains Ragnar or 7 contains Aquisitions
Asnwer: query=({'5'.CT.'Ragnar Lodbrok'}OR{'7'.CT.'Acquisitions'})
User Request: 5 IS NOT SAMPLE
Asnwer: query=({'5'.XEX.'Sample+Co'})
User Request: 5 STARTS WITH 'A'
Asnwer: query=({'5'.SW.'A'})
User Request: 5 DOES NOT STARTS WITH 'A'
Asnwer: query=({'5'.XSW.'A'})
User Request: 46 after 05-21-2024
Asnwer: query=({'46'.AF.'05-21-2024'})
User Request: 46 before 05-21-2024
Asnwer: query=({'46'.BF.'05-21-2024'})
"""
quickbase_rules = """
1. Building the query string
When you build a query, you must build at least one query string. A query string is composed of:
- a field ID (fid)
- an uppercase comparison operator (see the table below for a list of available operators).
    *Note: If you use a lowercase operator, you may encounter unexpected behavior. Use only uppercase operators.
- the value to be compared against

You should separate each of these query string components using a period and enclose the entire query string in curly braces, as shown below:
{'fid'.operator.'matching_value'}

Example:

<query>{'5'.CT.'Ragnar Lodbrok'}</query>

This example specifies that Quickbase should return all records where the “fid 5” field contains the value “Ragnar Lodbrok.”
2. Grouping multiple query strings
You can group several of query strings together, separating the query strings with the AND or OR operators, as shown here:

Example:

<query>{'5'.CT.'Ragnar Lodbrok'}AND{'7'.CT.'Acquisitions'}</query>

3. Queries with numeric values that include decimals
When you are using a query for a numeric field with a decimal, you will need to note your syntax.  
For example, {12.EX.5.6} would be the same as {12.EX.5}. You can query for decimal values by using apostrophes {12.EX.'5.6'}. 
Note that EX isn't the only filter that this applies to.

4. Query string comparison operators
Note: Query string comparison operators must be in uppercase.

First column is Comparison Operator, second column is description about comparison operator, and third column is application field: (Comparison Operator, Description, Applicable field types)
(CT,  Contains either a specific value or the value in another field of the same type.,  Do not use this operator with list-user fields; instead, use HAS.)
(XCT Does not contain either a specific value, or the value in another field of the same type. Do not use this operator with list-user fields; instead, use XHAS.)
(HAS, Contains a specific set of users. For each user you are trying to find, you must enter the user's ID, user name, or email address. You can also enter placeholder names. Be sure to surround placeholder names with double quotes.The query parameter must be surrounded by single quotes.Separate users in the list using a semi-colon. For example: <query>{'6'.HAS.'-8675309; -9873297'}</query>, Used with list-user fields only.)
(XHAS, Does not contain a specific set of users.  The query parameter must contain the user's ID, email address, or user name. You can also specify a placeholder name. Placeholder names must be enclosed in double quotes. The entire query parameter must be surrounded by single quotes. Separate users in the list using semi-colons. Note that a matching record must contain all users you specify. This query: <query>{'6".XHAS. '-8675309; -9873297'}</query> ...specifies that you want to see records that do not contain BOTH of these users. Therefore, the query will return records that contain either one or neither, but not both, of these users., Used with list-user fields only.)
(EX, Is When specifying values to query from List - User and Multi-select Text fields, enclose the entire query parameter in single quotes. Separate the values you're looking for using semi-colons. When you use a query like 10.ex. where 10 is a user field, ex is going to compare to the textual representation that the builder has configured on field props which is either full name, last name first, or username (which is email unless configured otherwise).,  Is equal to either a specific value, or the value in another field of the same type. See Filtering records using fields with multiple values for more information.)
(TV,  True Value (compares against the underlying foreign key or record ID stored in relationship fields). When you use tv, you are comparing against the unique value of the user which is either the hashed UID like 123456.abcd OR the email address OR the screen name., Also used for queries on User fields.)
(XTV, Not True Value (compares against the underlying foreign key or record ID stored in relationship fields)., Also used for queries on User fields.)
(XEX, Is not Is not equal to either a specific value, or the value in another field of the same field type., When specifying values to query from List - User and Multi-select Text fields, enclose the entire query parameter in single quotes. Separate the values you're looking for using semi-colons.)
(SW, Starts with, Starts with either a specific value or the value in another field of the same type.)
(XSW, Does not start with, Does not start with either a specific value or the value in another field of the same type.)
(BF, Is before, Is before either a specific value or the value in another field of the same type.)
(OBF, Is on or before a specific date, Is on or before either a specific date or the value in another date field)
(AF, Is after a specific date, Is after either a specific date or the value in another date field
(OAF, Is on or after a specific date, Is on or after either a specific date or the value in another date field)
(IR, Is in range., Use this operator with date fields, to determine whether a particular date falls within particular date range relative to the current date. Learn more about relative date ranges.)
(XIR, Is not in range., Use this operator with date fields, to determine whether a particular date falls within a particular date range relative to the current date. Learn more about relative date ranges.)
(LT, Is less than, Is less than either a specific value or the value in another field of the same type.)
(LTE, Is less than or equal to, Is less than or equal to either a specific value or the value in another field of the same type.)
(GT, Is greater than, Is greater than either a specific value or the value in another field of the same type.)
(GTE, Is greater than or equal to,Is greater than or equal to either a specific value or the value in another field of the same type.)

5. Handling Special Characters for a Query Field Values
If you are searching for a value that includes special characters, be sure to enclose the matching value in quotes. For example, if you are searching for this value:

"Joe B. Briggs"

...you should be sure to enclose the entire string in double quotes, as follows:

""Joe B. Briggs""

6. Querying on Dates and Times
You can query on dates (yyyy-MM-dd) or on times in milliseconds, but you cannot query on date-time values in the standard "yyyy-MM-dd hh:mm:ss" format.
"""
quickbase_query_system_template = """
You are a agent generating Quickbase query correponding to user request.
example user request and answer:
```
{example}
```
Here is rule for generating Quickbase query:
```
{context}
```
Double check your work.
"""
quickbase_chart_system_template = """
You are a chart agent generating chart in json format based on app information.
app information:
```
{context}
```
You should learn from these examples. 
What you should learn:
1. Output Schema
2. How to determine chartType from user request
3. How to determine table to answer user request.
4. How to determine field to group by, 
5. How to determine aggregate function, 
example user input and answer:
```
{example}
```

Here's additional information:
1. chartType: bar, line, pie
2. aggregateFunction: sum, average, count


Double check your work.
"""

reflection_system_template = """
You are a chart json object checker which evaluates chart json generated by other is right or not to answer user question.
app information:
```
{context}
```
You should learn from these examples. 
What you should learn:
1. Output Schema
2. How to determine chartType from user request
3. How to determine table to answer user request.
4. How to determine field to group by, 
5. How to determine aggregate function, 
example user input and answer:
```
{example}
```

Here's additional information:
1. chartType: bar, line, pie
2. aggregateFunction: sum, average, count

Your Task:
1. Check if generated chart json information by other is correct or not.
 - Check if output schema is right.
2. Check if generated chart json information by other is correct answer to user request.
 - Please make attention to `table` property.
 - Please make attention to `groupBy` property.
 - Please make attention to `aggregateFunction`
Critical:
1. Please start your answer YES if generated chart json information is correct, then write your answer.
2. If not correct, please write the reason why the generated json information is not correct.
Double check your work.
"""
ciritial_example = """"
    For instance:
        - Part of Chart Json
        ```
            "groupBy": {
                "field": "XYZ2"
            },
        ```
        - Part of App Schema:
        ```
            {
                "name": "XYZ",
                "type": "NM"
            },
            ...
            ...
            ...
            {
                "name": "XYZ2",
                "type": "NM"
            },
        ...
        * In this case XYZ2 field in  chart json exist in app schema, So It is correct.
        * Do not judge to be  WRONG after first compare "XYZ2" in chart json and "XYZ" in app schema.
"""

quickbase_chart_system_message_prompt = SystemMessagePromptTemplate.from_template(quickbase_chart_system_template)
quickbase_query_system_message_prompt = SystemMessagePromptTemplate.from_template(quickbase_query_system_template)
reflection_message_prompt = SystemMessagePromptTemplate.from_template(reflection_system_template)
# Set up the human template with a variable for the request
human_template = """
{request}
"""
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

quickbase_chart_prompt = ChatPromptTemplate.from_messages([quickbase_chart_system_message_prompt, human_message_prompt])
quickbase_query_prompt = ChatPromptTemplate.from_messages([quickbase_query_system_message_prompt, human_message_prompt])

prompt_generate = ChatPromptTemplate.from_messages([quickbase_chart_system_message_prompt, MessagesPlaceholder(variable_name='messages')])
reflection_prompt = ChatPromptTemplate.from_messages([reflection_message_prompt, MessagesPlaceholder(variable_name="messages")])

# This is our only modification
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
)

quickbase_chart_chain = quickbase_chart_prompt | model
quickbase_query_chain = quickbase_query_prompt | model
generate = prompt_generate | model
reflect = reflection_prompt | model

if __name__ == '__main__':

    with open('app_schema.json', 'r') as file:
        app_json_obj = json.load(file)
    with open('chart.json', 'r') as file:
        chart_json_obj = json.load(file)
    app_json_str = json.dumps(app_json_obj)
    with open('app_mapped.json', 'w') as file:
        json.dump(app_json_obj, file)
    request_list = [
        "Displays the number of works orders assigned to each vendor",
        "Displays the number of works orders assigned to each staff member",
        "Shows the percentage of works orders completed",
    ]
    for request in request_list:
        # Record the start time
        start_time = time.time()
        response = quickbase_chart_chain.invoke({"context": app_json_str, "example": quickbase_chart_example, "request": request})
        # Record the end time
        end_time = time.time()
        # Calculate the difference
        execution_time = end_time - start_time

        print(f"Execution time: {execution_time} seconds")
        print("============= quickbase chart =============", response.content)

    if response.content.find('```') != -1:
        answer = response.content.split('```')[1]
        answer = answer[4:] if answer.startswith('json') else answer
        with open('output.json', 'w') as file:
            output_json_obj = json.loads(answer)
            json.dump(output_json_obj, file)
    
    response = quickbase_query_chain.invoke({"context": quickbase_rules, "example": quickbase_query_example, 
                                            #  "request": "4 contains fsdfdf and 7 contains ggggg or 46 after 05-21-2024 and 61 is 'Sample Co'"})
                                            "request": "6 Belongs to 'Tasks'"})
                                            
    print("=============== quickbase query ===========\n", response.content)
    
    # langgraph demo for chart json
    b_langgraph_agent = False

    if b_langgraph_agent:

        request = HumanMessage(
            content="Displays the number of works orders assigned to each staff member"
        )
        chart = ""
        for chunk in generate.stream({"context": app_json_str, "example": quickbase_chart_example, "messages": [request]}):
            print(chunk.content, end="")
            chart += chunk.content
            
        print("==========================generted chart json", chart)
        reflection = ""
        for chunk in reflect.stream({"context": app_json_str, "example": quickbase_chart_example, "critical_example": ciritial_example, "messages": [request, HumanMessage(content=chart)]}):
            print(chunk.content, end="")
            reflection += chunk.content
        print("==========================generted chart json reflection", reflection)


        
        def generation_node(state: Sequence[BaseMessage]):
            return generate.invoke({"context": app_json_str, "example": quickbase_chart_example, "messages": state})


        def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
            # Other messages we need to adjust
            cls_map = {"ai": HumanMessage, "human": AIMessage}
            # First message is the original user request. We hold it the same for all nodes
            translated = [messages[0]] + [
                cls_map[msg.type](content=msg.content) for msg in messages[1:]
            ]

            # print('=======================translated', translated)
            res = reflect.invoke({"context": app_json_str, "example": quickbase_chart_example, "messages": translated})
            # We treat the output of this as human feedback for the generator
            return HumanMessage(content=res.content)

        builder = MessageGraph()
        builder.add_node("generate", generation_node)
        builder.add_node("reflect", reflection_node)
        builder.set_entry_point("generate")


        def should_continue(state: List[BaseMessage]):
            if len(state) > 2:
                # End after 3 iterations
                return END
            return "reflect"


        builder.add_conditional_edges("generate", should_continue)
        builder.add_edge("reflect", "generate")
        graph = builder.compile()
        def run_graph():
            for event in graph.stream(
                [
                    HumanMessage(
                        content="Displays the number of works orders assigned to each staff member"
                    )
                ],
            ):
                print(event)
                print("----------------------")
            # print("=================event==================", event)
            # ChatPromptTemplate.from_messages(event[END]).pretty_print()
        run_graph()

