import requests
from bs4 import BeautifulSoup
import pandas as pd
from Login import payload
import timeit

start_time = timeit.default_timer()

village_number = []
village_name = []
player_name = []
x_coords = []
y_coords = []

village_number_alliance = []
player_name_alliance = []
alliance_name = []

loginurl = 'https://ts2.anglosphere.travian.com/login.php'
siteurl = 'https://ts2.anglosphere.travian.com/dorf1.php'
staturl_village = 'https://ts2.anglosphere.travian.com/statistics/village'
page_village = 'https://ts2.anglosphere.travian.com/statistics/village?page=1'
page_alliance = 'https://ts2.anglosphere.travian.com/statistics/player?page=1'

headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

# payload = {
#     'name':'username',
#     'password':'password'
# }

with requests.Session() as s:
    r = s.get(loginurl, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    payload['login'] = soup.find('input', attrs={'name':'login','type':'hidden'})['value']

    r = s.post(loginurl, data=payload, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    r_stat = s.get(page_village, headers=headers)
    soup_stat = BeautifulSoup(r_stat.content, 'html.parser')
    pageinator = soup_stat.find('div', class_='paginator')
    total_pages = pageinator.find_all('a',class_='number')
    total_pages = total_pages[-1].text

    
    #for player data
    for page in range(1,int(total_pages)+1):
        print('Starting page: '+str(page))
        r_stat = s.get('https://ts2.anglosphere.travian.com/statistics/village?page=' + str(page), headers=headers)
        soup_stat = BeautifulSoup(r_stat.content, 'html.parser')

        table = soup_stat.find('table', attrs={'id':'villages','class':'row_table_data'})
        #index = table.find_all('td',class_='ra')
        vils = table.find_all('td',class_='vil')
        players = table.find_all('td',class_='pla')
        xcoords = table.find_all('span',class_='coordinateX')
        ycoords = table.find_all('span',class_='coordinateY')
        # for i in index:
        #     num = i.text[:-1]
        #     num = float(num)
        #     village_number.append(num)
        for vil in vils:
            name = vil.a.text
            name = str(name)
            village_name.append(name)
        for player in players:
            name = player.a.text
            name = str(name)
            player_name.append(name)
        for coord in xcoords:
            x = coord.text
            x = x[2:]
            if x[0] == '−':
                if x[3].isdigit():
                    if x[4].isdigit():
                        x = x[0]+x[2:5]
                    else:
                        x = x[0]+x[2:4]
                else:
                    x = x[0]+x[2:3]
            else:
                if x[1].isdigit():
                    if x[2].isdigit():
                        x = x[0:3]
                    else:
                        x = x[0:2]
                else:
                    x = x[0]
            if x[0] == '−':
                x_list = list(x)
                x_list[0]='-'
                x=''.join(x_list)
            x = float(x)  
            x_coords.append(x)
        for coord in ycoords:
            y = coord.text
            y = y[1:]
            if y[0] == '−':
                if y[3].isdigit():
                    if y[4].isdigit():
                        y = y[0]+y[2:5]
                    else:
                        y = y[0]+y[2:4]
                else:
                    y = y[0]+y[2:3]
            else:
                if y[1].isdigit():
                    if y[2].isdigit():
                        y = y[0:3]
                    else:
                        y = y[0:2]
                else:
                    y = y[0]
            if y[0] == '−':
                y_list = list(y)
                y_list[0]='-'
                y=''.join(y_list)
            y = float(y)  
            y_coords.append(y)
        villages_df = pd.DataFrame(list(zip(village_name,player_name,x_coords,y_coords)),
                columns =['Village','Player','x-coord','y-coord'],)
        villages_df.to_excel('VillageData.xlsx',index=False,sheet_name='VillageData')

    #for alliance data 
    r_stat = s.get(page_alliance, headers=headers)
    soup_stat = BeautifulSoup(r_stat.content, 'html.parser')
    pageinator = soup_stat.find('div', class_='paginator')
    total_pages = pageinator.find_all('a',class_='number')
    total_pages = total_pages[-1].text

    for page in range(1,int(total_pages)+1):
        print('Starting page: '+str(page))
        r_stat = s.get('https://ts2.anglosphere.travian.com/statistics/player?page=' + str(page), headers=headers)
        soup_stat = BeautifulSoup(r_stat.content, 'html.parser')

        table = soup_stat.find('table', attrs={'id':'player','class':'row_table_data'})
        # index = table.find_all('td',class_='ra')
        players = table.find_all('td',class_='pla')
        alliances = table.find_all('td',class_='al')
        
        # for i in index:
        #     num = i.text[:-1]
        #     num = float(num)
        #     village_number_alliance.append(num)
        for player in players:
            name = player.a.text
            name = str(name)
            player_name_alliance.append(name)
        for alliance in alliances:
            try:
                name = alliance.a.text
                name = str(name)
            except:
                name = ''
            alliance_name.append(name)
        alliances_df = pd.DataFrame(list(zip(player_name_alliance,alliance_name)),
            columns=['Player','Alliance'])
        alliances_df.to_excel('AllianceData.xlsx',index=False,sheet_name='AllianceData')


# villages_df = pd.DataFrame(list(zip(village_name,player_name,x_coords,y_coords)),
#             columns =['Village','Player','x-coord','y-coord'])
# alliances_df = pd.DataFrame(list(zip(player_name_alliance,alliance_name)),
#             columns=['Player','Alliance'])
# print(villages_df)
# print(alliances_df)

Left_join = pd.merge(villages_df, alliances_df, on ='Player', how ='left')

stop_time = timeit.default_timer()
runtime = (stop_time-start_time)/60
print('Runtime in minutes: ' + str(runtime))


overwrite = input('Do you want to overwrite the copy of the most resently saved file?\nEnter "y" if you do and enter "n" if you do not\n')
if overwrite == 'y':
    villages_df.to_excel('VillageData_copy.xlsx',index=False,sheet_name='VillageData')
    alliances_df.to_excel('AllianceData_copy.xlsx',index=False,sheet_name='AllianceData')

Left_join.to_excel('AllData.xlsx',index=False)

