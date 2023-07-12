"""
main.py to acquire raw weather data for each Vehicle

"""



import pandas as pd
import numpy as np
import os

from tqdm import tqdm
from icecream import ic

from weatherAPI import WeatherAPI



def getData():

    daejeon_folder = 'Y://00_Rawdata/Field_Data_3second/Pilot_Fleet_Daejeon_Taxies10_Phase1'
    pohang_folder = 'Y://00_Rawdata/Field_Data_3second/Pilot_Fleet_Pohang_Smart_Phase2'
    jeju_folder = 'Y://00_Rawdata/Field_Data_3second/Pilot_Fleet_JEJU_wKAIST_Phase1'
    santafe_folder = 'Y://00_Rawdata/Field_Data_3second/Pilot_Filed_Daejeon_Santafe_Phase1/N097_Daejeon_Santafe_1/이성우(9_16)'

    fleet_path = {'Daejeon': daejeon_folder, 'Pohang':pohang_folder, 'Jeju': jeju_folder, 'Road': santafe_folder}
    vehicles = {'Daejeon':['N106', 'N111', 'N112', 'N118', 'N119', 'N125', 'N133', 'N137', 'N142', 'N150'],
            'Pohang':['N082','N085','N086','N088','N090'],
            'Jeju':['N144','N145','N146','N147'],
            'Road':['N097']}
    
    df_list = []
    for fleet, vehicle in vehicles.items():
        path = fleet_path[fleet]
        for veh in vehicle:
            for root, dirs, files in os.walk(path):
                    if veh in root:
                        for file in files:
                            if file.endswith('recalib.csv') or fleet == 'Road':
                                timestamp = ('-').join(file.split('&')[1].split('-')[:6])
                                df = pd.DataFrame({'Fleet':[fleet], 'Vehicle':[veh], 'timestamp':[timestamp] ,'root':[root], 'file':[file]})
                                print(fleet,veh,timestamp,root,file)
                                df_list.append(df)

    dataset = pd.concat(df_list)

    KEY = 'YOUR_API_KEY'
    WEATHER_URL = 'http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'

    save_to = 'Y://99_Code_Library/Sheroz/02.Weather API/data'
    if not os.path.exists(save_to):
        os.makedirs(save_to)


    vehicle_group = dataset.groupby('Vehicle')
    for vehicle, veh_group in vehicle_group:
        df_list = []
        for idx, row in veh_group.reset_index(drop=True).iterrows():

            path2file = os.path.join(row.root, row.file)
            df = pd.read_csv(path2file)
            df = df[['year','month','day','hour','min','sec','lat','lon']]
            df.dropna(axis=1, inplace=True)
            df = df[(df[['lat','lon']] != 0).all(axis=1)].reset_index(drop=True)
            # GPS 값 모두 다 0일 시 skip
            if not df.empty:
                #weatherAPI 파일 불러 파라미터 뽑음 (온도, 노면온도, 강수량)
                weatherAPI = WeatherAPI(df,KEY, WEATHER_URL)
                weather_df = weatherAPI.getParams()
                #날씨 파라미터 빈 값으로 출력 시 skip
                if weather_df is not None and not weather_df.empty:
                    print(row['Fleet'], row['Vehicle'], row['file'], idx, '/', len(veh_group))
                    df_list.append(weather_df)
                    
        df = pd.concat(df_list)
        df.to_csv(save_to + f'/{vehicle}_weather.csv', index=False)
        print(f'{vehicle} saved to {save_to}')   



if __name__== "__main__":
    getData()

