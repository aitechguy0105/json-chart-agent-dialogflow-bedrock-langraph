# Quickbase Chart and Query Generation

This project aims to create a tool that can generate custom charts and Quickbase queries based on user prompts. The tool utilizes the power of large language models, specifically LangChain and LangGraph, along with the OpenAI GPT-4o model, to understand user requests and generate the appropriate outputs.


## How to use

1. install python 3.10
2. `pip install -r requirements.txt`
3. `python langgraph-demo.py`
4. set `b_langgraph_agent = True` to see the results of langgraph


## Features

1. **Prompt-based Chart Generation**: Users can provide natural language prompts, and the tool will generate the corresponding Quickbase chart configuration with app schema.
2. **Prompt-based Query Generation**: Users can provide natural language prompts describing the desired data query, and the tool will generate the corresponding Quickbase query.
3. **Role-based Prompting**: The tool can tailor its responses based on the user's role (e.g., analyst, manager, executive) to provide more relevant and tailored outputs.
4. **Few-shot Learning**: The tool can leverage a small number of example prompts and outputs to quickly adapt to new user requests, improving its performance over time.
5. **Knowledge Scaling**: When the underlying knowledge base becomes larger, the tool can utilize the Retrieval Augmented Generation (RAG) architecture to efficiently retrieve and integrate relevant information into the generated outputs.

## Tech Stack

- **Python 3.10**: The programming language used for the project.
- **LangChain**: A framework for building applications with large language models.
- **LangGraph**: A tool for integrating knowledge graphs into language models.
- **OpenAI GPT-4o**: A powerful large language model used for generating charts and queries.

## Contributing

Contributions to this project are welcome. If you have any ideas, bug fixes, or feature enhancements, please feel free to submit a pull request or open an issue.