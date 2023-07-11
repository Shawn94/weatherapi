"""
This python code utilizes Weather API provided by data.go.kr
The API returns different parameters related to the weather, but we get only 
TEMPERATURE, SURFACE TEMPERATURE and RAINFALL(mm)

!!! This script is followed with cityName python file. Put both .py files
together. This is to identify location name in Korean language and provide 
city code for the weather API

Created by: Sheroz

"""
from cityName import CityFinder

import pandas as pd

import requests
import json
from urllib.parse import unquote
import time

from icecream import ic



class WeatherAPI():

    def __init__(self, df, key, url):
        self.key = key
        self.df = df
        self.url = url


    def locCode(self):
        
        city_api = city_api = 'OPENCAGE_API'
        city_code_df = pd.read_csv('citycode.csv')
        # 같은 날짜, 같은 세션의 gps 중심좌표
        middle_value = int(len(self.df)/2)
        pointer_coord = self.df.iloc[middle_value][['lat','lon']]

        city_locater = CityFinder(key=city_api, citycode_df=city_code_df, pointer= pointer_coord)

        # 중심좌표와 키 매개변수로 지점코드 또는 가까운 도시 리스트 출력, 지점코드 없을 경우
        # 중심좌표 기준 시/군 이름을 사용하여 리스트에 있는 거리상 시/군 선택
        cityCode, nearest_cities, orig_city = city_locater.locater()
        
        if cityCode == None and orig_city != None:
            # 가끔 gps 값이 잘못 되어 도시 이름이 외국 이름으로 정해짐
            if  all(0xAC00 <= ord(char) <= 0xD7A3 for char in orig_city):
                # 해당 시/군 리스트에 없는 경우 cityCode가 Nan 되어 리스트에서 제일 가까운 지역 거리 계산
                cls_city, distance = city_locater.closest_city(orig_city,nearest_cities)
                # 둘 중 하나가 항상 NaN 값으로 이어짐
                cityCode = city_code_df.loc[city_code_df['지점명'] == cls_city]['지점'].values[0]
        
        return cityCode
    
    def getParams(self):

        #시작날짜, 종료날짜 DTG 데이터로 정함
        #행수를 계산하기 위해 지정된 날짜/시간 범위의 총 시간
        startDt = pd.Timestamp(*self.df[['year','month','day','hour']].iloc[0].values)
        endDt = pd.Timestamp(*self.df[['year','month','day','hour']].iloc[-1].values)
        startHr = str(self.df['hour'].iloc[0])
        endHr = str(self.df['hour'].iloc[-1])

        t_delta = endDt - startDt #날짜로 일수 계산
        row = int(t_delta.total_seconds()/3600 + 2)

        #시간을 계산한 다음 날짜를 파라미터 형식으로 다시 바꿈
        startDt = startDt.strftime('%Y%m%d')
        endDt = endDt.strftime('%Y%m%d')

        weather_params = dict()
        weather_params['serviceKey'] =  unquote(self.key) #디코딩 된 키 값
        weather_params['pageNo'] = '1'
        weather_params['numOfRows'] = int(row) #행수 (날짜/시간 범위 내 출력 요청)
        weather_params['dataType'] = 'JSON' #출력 데이터 형식
        weather_params['dataCd'] = 'ASOS' 
        weather_params['dateCd'] = 'HR' #시간 단위로 출력
        weather_params['startDt'] = startDt #관측 데이터 시작 날짜
        weather_params['startHh'] = startHr if len(startHr) > 1 else '0' + startHr #관측 데이터 시작 시간
        weather_params['endDt'] = endDt #관측 데이터 종료 날짜
        weather_params['endHh'] = endHr if len(endHr) > 1 else '0'+ endHr #관측 데이터 종료 시간
        weather_params['stnIds'] = str(self.locCode()) #위치 지정 코드 (133: 대전, 108: 서울)
        df_weather = pd.DataFrame()
        
        NUM_RETRIES = 3
        for _ in range(NUM_RETRIES):

            try:
                # API 출력 값이 성공 시:
                resp = requests.get( self.url, params=weather_params, timeout=10)
                if resp.status_code in [200, 404]:
                    break
            # request 실패 Connection 확인 --> 재시도    
            except requests.exceptions.ConnectionError:
                    print('Connection error, trying to connect again')
                    pass
            # 재시도헸는데도 접속 이뤄지지 않았음 --> resp == None, 본 파일 skip
            except requests.exceptions.Timeout:
                    print('Connection failed after another trial')
                    pass
            resp = None
        # Connection 성공시    
        if resp is not None and resp.status_code == 200:
            # json 형식을 읽고 기온, 강수량, 지면온도 뽑기
            try:
                json_data = resp.content
                parsed_json = json.loads(json_data)
            #Decoding 에러 발생시 다음으로 넘어감    
            except json.JSONDecodeError as e:
                print('Error decoding JSON', e)
                return df_weather
            
            # API 정상 출력시  (API 데이터 있으면)
            if parsed_json['response']['header']['resultMsg'] == "NORMAL_SERVICE":

                time = list(map(lambda x: x['tm'],parsed_json['response']['body']['items']['item'])) #시간: tm (YYYY-MM-DD HH)
                tmp = list(map(lambda x: x['ta'],parsed_json['response']['body']['items']['item'])) #기온: ta (degree)
                rainfall = list(map(lambda x: x['rn'],parsed_json['response']['body']['items']['item'])) #강수량: rn (mm)
                surface_tmp = list(map(lambda x: x['ts'],parsed_json['response']['body']['items']['item'])) #지면온도: ts (degree)  
                # Dataframe 생성
                df_weather = pd.DataFrame({"date": time, "temperature": tmp, "rainfall": rainfall, "surface_tmp": surface_tmp})

                #빈 값들 0으로 바꾸고 나머지 float type 포멧
                df_weather['rainfall'] = df_weather.rainfall.replace('', 0).astype('float')
                
                return df_weather
        
        else: 
            return df_weather

        
