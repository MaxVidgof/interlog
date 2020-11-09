FROM python:3.6

FROM python:3.6

RUN apt-get update \
    && apt-get install -y --no-install-recommends nano graphviz libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR .
COPY . .
RUN pip install -r requirements.txt

#RUN sed -i "s+10.139.167.139+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`+g" ./webapp/static/index.js
#RUN sed -i "s+10.139.167.139+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`+g" ./webapp/static/FilterContainer.js

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
