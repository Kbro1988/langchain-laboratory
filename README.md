# Langchain Laboratory

Langchain Laboratory is an open-source application built using [Streamlit](https://docs.streamlit.io/) to provide developers and those interested in building Language Model (LLM) applications with [LangChain](https://python.langchain.com/docs/get_started/introduction.html).

## Features

- **Document Embedding**: The application provides a dashboard that allows users to upload PDF (.pdf) files, Mircosoft Word (.docx) files, and plain text (.txt) files. It creates embeddings of these documents and uploads the embeddings to a Chroma Vector Store.

- **Conversational Memory**: The application also provides a feature for conversational memory.

## Project Status

This project is a work in progress and contributions are encouraged. For more information, please contact [barweiss@cisco.com](mailto:barweiss@cisco.com).

## Licensing

This project is open source through MIT licensing.

## Compatibility

At this time, this application is only designed to work with the OpenAI GPT-3.5-turbo and GPT-4 LLMs. However, in order to showcase the LangChain modularity and extensibility, we plan to add the ability to allow this tool to be used with any LLM in the future.

## Getting Started

This application was developed with a Python 3.11 environment. Follow the steps below to install and run the application:

1. **Prerequisites**: Ensure that Python 3.11 or greater is installed on your system.

2. **Clone the project** - Use the command: `git clone https://github.com/barweiss45/langchain-laboratory.git` to clone the project and `cd langchain-laboratory` to navigate to the project directory.

3. **Set up a virtual environment** - Set up your virtual environment with your favorite Python Virtual Environment Software. For example, you can use `venv` or `virtualenv`.

4. **Install the necessary libraries** - Run `pip install -r requirements.txt` to install the necessary libraries.

5. **Add your OpenAI API key** - Add a `.env` file to the main directory that contains your OpenAI API key. The key should be stored with the name `OPENAI_KEY_API`.

6. **Run the application** -  Execute the command `streamlit run Home.py`. Your browser should open to `http://localhost:8501`.

Please note that we will be containerizing this application in the next day or so, which will simplify installation and usage.

## Docker Installation

If you prefer to use Docker, follow the steps below:

1. **Prerequisites**: Ensure that Docker is installed on your system. If not, visit [Docker](https://docs.docker.com/engine/install/) for installation instructions. You can verify the installation by running `docker --version`.

2. **Clone the project**: Use the command `git clone https://github.com/barweiss45/langchain-laboratory.git` to clone the project. Next be sure you have moded to the new langchain-laboratory directory, use the command `cd langchain-laboratory`.

3. **Create symbolic links**: Create two symbolic links to point back to the Docker folder for the `Dockerfile` and `docker-compose.yml` file. Use the following commands:

    ```bash
    ln -s docker/Dockerfile Dockerfile
    ln -s docker/docker-compose.yml docker-compose.yml
    ```

4. **Build the container**: Run `docker compose up -d`. Please note that the build may take up to 3 to 4 minutes.

5. **Verify the status**: You can verify the status of the container with the Docker command `docker compose ps`.

After the container is up and running, you can connect to the application via `http://localhost:8501`.

## Contributing

This is a new project and we're still working on setting up a comprehensive guide for contributions. In the meantime, if you're interested in contributing or have any questions, please feel free to contact [barweiss@cisco.com](mailto:barweiss@cisco.com). We appreciate your interest and patience.

## License

This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE) for more details.
