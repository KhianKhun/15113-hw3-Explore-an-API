*******************************
*******       API       *******
*******************************
This project uses the US National Weather Service Web API (website: weather.gov) to retrieve weather forecasts and the current humidity. The application codes are mainly in file 'weather.py'. The application makes HTTP GET requests calling the /points/{latutude},{longitude} endpoint to get the required information. Forecast data is retrieved from the forecast endpoing and the current humidity is retrieved from the nearest weather station's last observation (two endpoints). All API responses are returned in JSON (GeoJSON) format and translated into python data. The US Weather Service Web API does not need an API key, but a valid User-Agent header is required in each searching application.




**************************************
*******       How to use?      *******
**************************************
1. Make sure you download package "request"
2. Clone the file to local
3. Print "py -m src.app" or "python -m src.app" to use in directory "15113-hw3-Explore-an-API"
4. Have fun




****************************************
*******       Introduction       *******
****************************************
This is an app simulating a US weather app. User in this app can select different time range(report future 3 days or 7days) and extra information (including wind direction/speed, weather conditions) to search. This app also support to search cities by typing, which includes about 700 city locations in relative large scale.