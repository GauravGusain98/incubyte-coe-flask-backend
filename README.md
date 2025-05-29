### How to install the application 
1. Install uv package manager - [Reference Link](https://docs.astral.sh/uv/getting-started/installation/)
    
    On Mac:
    ```sh
    brew install uv
    ```
2. Start and activate virtual env using uv - [Reference Link](https://fastapi.tiangolo.com/virtual-environments/#create-a-virtual-environment)
    ```sh
    uv venv
    source .venv/bin/activate
    ```
3. Install dependencies
    ```sh
    uv pip install -r requirements.txt
    ```
3. Copy the .env.example and create .env file
4. Update the values in .env file according to your configuration
5. Run migrations to create database table using thie command
    ```sh
    alembic upgrade head
    ```
5. Run the application

    Without Hot Reloading
    ```sh
    flask run
    ```

    With Hot Reloading
    ```sh
    python app.py
    ```
6. Test APIs using Swagger on the below URL
    ```sh
    http://127.0.0.1:5000/docs 
    ```

### Setup Automated Testing
1. Create test database in Postgres

2. Update the env variables in the .env.test file

3. Run all test cases using this command
    ```sh
    pytest
    ```

