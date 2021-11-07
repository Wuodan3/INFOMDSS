# Covid-19 Dashboard with predictive analytics
This program is the source code which creates a dashboard. The dashboard contains graphs on active cases and the stringency indexes for The Netherlands, Sweden, and Australia. The python program also features a predictive analytic aspect which uses Auto Regression on the positive case history of the forementioned countries. This result is a graph with the predicted new cases for the next 30 days.

## Prerequisites

Docker - Very useful tool to get the project running. Using Docker you won't have to install python packages or python itself to your system.

Browser - Either Chrome or Firefox will suffice

Patience - The dashboard takes a while to load, also changing graphs through the dropdown menu can take some time.

## Installation
The project includes a dockerfile and a docker-compose file. In order to run the container navigate to the downloaded folder in a terminal and run 'docker-compose up'.

You will see some text showing up in the commandprompt. Once you see ```Dash is running on http://0.0.0.0:8050/``` then the dashboard is running. To see the dashboard go to 127.0.0.1:8050 in either Chrome or Firefox to see and interact with the dashboard.

An alternative method is install the requirements using:
```python
pip install -r requirements.txt
```
Then running the python file, form the commandline. And then, just like the docker method, go to ```127.0.0.1:8050``` to view the dashboard.
## Usage
The dashboard uses Dash to display graphs this makes the graphs interactable. You can resize zoom and select and deselect variables, shown in the graphs, through the legend on the right hand side. 
