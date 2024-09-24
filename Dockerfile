FROM python:3.6

RUN apt-get update \
    && apt-get install -y --no-install-recommends nano graphviz libgirepository1.0-dev iproute2 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

#RUN ./run_locally.sh

#RUN sed -i "s+cherry-picker.cluster.ai.wu.ac.at+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`:8000+g" ./webapp/static/index.js
#RUN sed -i "s+cherry-picker.cluster.ai.wu.ac.at+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`:8000+g" ./webapp/static/FilterContainer.js
#RUN sed -i "s+https+http+g" ./webapp/static/index.js
#RUN sed -i "s+https+http+g" ./webapp/static/FilterContainer.js

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
