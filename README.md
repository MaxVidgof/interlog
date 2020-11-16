# InterLog

InterLog is an interactive tool for delta-log analysis. It takes an event log in XES format and allows to split it into two complementary logs based on three filters: the time filter, the variants filter and the activities filter.  You can specify multiple ranges for all the three filters.

# Usage

You can use the tool as a Docker container or just run it locally. Please follow the instructions below for more details.

### Docker

In order to use InterLog in a Docker container, do the following:

1. Clone this repository and `cd` into it
2. Open the `Dockerfile` and uncomment line 14 to make it
```
RUN ./run_locally.sh
```
3. Build the Docker container by running 
```
docker build -t interlog .
``` 
This process takes approximately 5 minutes
4. Start the container by running 
```
docker run -p 8000:8000 interlog
```
5. Go to `http://<your_docker_container_ip>:8080` in your browser

 ### Locally on a linux machine
 
 In order to install and run InterLog locally, do the following: 
1. Clone this repository and `cd` into it
2. Check the name of your network adapter. It is `eth0` by default for a wired connection
3. Open `run_locally.sh` and replace `eth0` in lines 1 and 2 with your network device if it is different
4. Execute `run_locally.sh` by typing 
```
./run_locally.sh
```
5. Make sure your `python` command points to Python 3 and your `pip` command points to PIP3. If it is not the case, execute:
```bash
alias python=python3
alias pip=pip3
```
6. Install the requirements by running 
```
pip install -r requirements.txt
``` 
or, if you are using Anaconda, 
```
conda install -r requirements.txt
```
7. Start the script by typing 
```
python manage.py runserver 0.0.0.0:8000
```
8. Go to `http://<your_ip_address>:8000`. Make sure you use your IP address assigned to the network device you selected, and not just `localhost`
