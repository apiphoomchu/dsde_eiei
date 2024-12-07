## Steps to run this project

```py
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Prepare the data -> create "data" folder & Put the data inside "data" folder
mkdir data

# Please run startup.py first to generate the vectordb. beaware that it will take a while
python startup.py

# and then you can run the pipeline.py
python pipeline.py
```
