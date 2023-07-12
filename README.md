## WeatherAPI 공공데이터포털
Weather API usage is based on GPS data and a given date period. This is for the calculation of Road Surface temperature, the number of Dry/Wet days.
This API work only in Korea, as it is provided by Korean Government for local usage.

## Usage

1. Get your own API key on [**data.go.kr**](www.data.go.kr) <br>
	- The api is **기상청_지상(종관, ASOS) 시간자료** <br>
	- Basically, this API returns weather data based on request parameters
2. Response data is available only for cities, provinces in <u> **citycodes.csv** </u> locations
	- You need to know the location of in Korean for as request parameter
	- I used another API(*OpenCage*) to find the korean name of GPS location
	- Plus if the location does not exist in the citycode list, it will search for the closest city available in the <u> **citycodes.csv** </u>
	- When all request parameters are complete, it will return weather information for that specific location withing requested period
	- In my case, I only used **Temperature, Rainfall, Surface Temperature**
