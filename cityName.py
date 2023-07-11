"""
This python code finds the city name from given gps coordinates.
The city name is further used in weather API.
It also calculates the closest city located to the given gps, which is in the list of cities
in weather API

Created by: Sheroz

"""


from opencage.geocoder import OpenCageGeocode
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, asin


class CityFinder():

    def __init__(self, pointer, citycode_df, key):
        self.pointer = pointer
        self.citycode_df = citycode_df
        self.key = key


    
    def locater(self):
        
        geocoder = OpenCageGeocode(self.key)
        
        results = geocoder.reverse_geocode(self.pointer[0], self.pointer[1], language='kr')
        
        if results:
            # if  results[0]['components'].get('country_code') == 'KR':
            # 출력 데이터 시 <-> 군 구별
            if 'city' in results[0]['components'].keys(): 
                city = results[0]['components']['city']
            elif 'county' in results[0]['components'].keys():
                city = results[0]['components']['county']
            else: city = None

            # 특별시 or 지역명 예외처리
            if 'province' in results[0]['components'].keys():
                province = results[0]['components']['province']
            else: province = '특별시'

        else: city = None
        
        # if return city is in the weather api city, return its code
        # else return location province -> get the cities for the same province
        # and calculate the closest city to it. Use that city`s weather
        near_cities = []
        cityCode = None
        if city is not None:
            for _, row in self.citycode_df.iterrows():
                if row['지점명'] == city: 
                    cityCode = row['지점']

                elif row['지역'] == province: 
                    near_cities.append(row['지점명'])

        return cityCode, near_cities, city
        # else:
        #     return None, [], None

    # function to calculate distance between two GPS coordinates using Haversine formula
    def haversine(self,lat1, lon1, lat2, lon2):
        R = 6372.8  # Earth radius in kilometers

        d_lat = radians(lat2 - lat1)
        d_lon = radians(lon2 - lon1)

        lat1 = radians(lat1)
        lat2 = radians(lat2)

        a = sin(d_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(d_lon / 2)**2
        c = 2 * asin(sqrt(a))

        return R * c


    def closest_city(self,original_city, nearest_cities):

        # create a geolocator object
        geolocator = Nominatim(user_agent="fms")

        # get the GPS coordinates of the original city
        orig_location = geolocator.geocode(original_city, language="ko", timeout=10)
        # iterate over cities to calculate distances and find closest one
        closest_city = None
        min_distance = float('inf')  # initialize to infinity

        for city_name in nearest_cities:
            # get the GPS coordinates of the city
            city_location = geolocator.geocode(city_name, language="ko")
            if city_location == None:
                continue
            # calculate the distance between the original city and the current city
            distance = self.haversine(orig_location.latitude, orig_location.longitude, city_location.latitude, city_location.longitude)

            # update closest city and distance if this city is closer
            if distance < min_distance:
                closest_city = city_name
                min_distance = distance

        return closest_city, min_distance





# def run(df,pointer):
#     #기상청 API 시.군 지점코드 파일
#     df = pd.read_csv('API/citycode.csv')
#     # opencage API 키
#     key = 'fda2c1296f99477ea14c0ec085e12da6'
#     # GPS coordinates to find the name of the city
#     # in this case, we use middle point of the route

#     # 중심좌표와 키 매개변수로 지점코드 또는 가까운 도시 리스트 출력, 지점코드 없을 경우
#     # 중심좌표 기준 시/군 이름을 사용하여 리스트에 있는 거리상 시/군 선택
#     cityCode, nearest_cities, orig_city = locater(pointer,key)

#     # 해당 시/군 리스트에 없는 경우 cityCode가 Nan 되어 리스트에서 해당 지역의 제일 가까운 도시 계산함
#     cls_city = closest_city(orig_city,nearest_cities) if cityCode == None else None

#     # 둘 중 하나가 항상 NaN 값으로 이어짐
#     if cityCode == None: cityCode = df.loc[df['지점명'] == cls_city]['지점'].values[0]