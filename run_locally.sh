
sed -i "s+cherry-picker.cluster.ai.wu.ac.at+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`:8000+g" ./webapp/static/index.js
sed -i "s+cherry-picker.cluster.ai.wu.ac.at+`ip -4 -o address | grep eth0 | awk '{print $4}' | awk -F"/" '{print $1}'`:8000+g" ./webapp/static/FilterContainer.js
sed -i "s+https+http+g" ./webapp/static/index.js
sed -i "s+https+http+g" ./webapp/static/FilterContainer.js

