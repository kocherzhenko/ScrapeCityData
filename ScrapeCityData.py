import time
import random
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup


def remove_comas(numstr):
    numstr_list = numstr.split(',')
    numstr = ''
    for el in numstr_list:
        numstr += el

    return numstr


def main():

    # Read in state names and codes
    states = []
    state_strs = []
    ST = []
    f = open('States.txt','r')
    for line in f:
        states.append(line.split(',')[0])
        if len(states[-1].split()) == 1:
           state_str = states[-1].strip()
        elif len(states[-1].split()) == 2:
           state_str = states[-1].split()[0]+'-'+states[-1].split()[1]
        state_strs.append(state_str) 
        ST.append(line.split(',')[1])
#        print (state_str)
    f.close()
#    state_strs = state_strs[:4]

    # Get city/town names for each state
    cities_by_state = {}
    URL = "https://www.city-data.com/city/"
    for state_str in state_strs:
        print (state_str)
        cities = []
        flag = False
        # Keep trying until page is obtained
        while not flag:
            try:
                page = requests.get(URL+state_str+'.html')
                delay = random.randint(10,20)
                time.sleep(delay)
                flag = True
            except:
                flag = False
         
        delay = random.randint(10,20)
        time.sleep(delay)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find(id='cityTAB')
        city_els = results.find_all('tr', {"class" : "rB"})
        for el in city_els:
            city = ((str(el).split("<a href=")[1]).split(".html")[0])[1:]
#            print (city)
            cities.append(city)
        cities_by_state[state_str] = cities

    categories = ['Name','State','Latitude', 'Longitude', 'Zipcodes', 'Population', 'Population density', 'Males', 'Females', 'Median age', 'White', 'Black', 'Hispanic', 'Asian', 'Native American', 'Pacific Islander', 'Other race', '2 or more races', 'Never married', 'Now maried', 'Separated', 'Widowed', 'Divorced', 'High school', 'Bachelors', 'Graduate', 'Commute time', 'Cost of living index', 'Household income', 'Per capita income', 'Rent', 'Unemployment', 'Percent poverty', 'City-Data crime index', 'Police per 1000 residents', 'Highway spending']
    f = open('CityData.csv','w')
    for category in categories:
        f.write(category+',')

    for state in cities_by_state.keys():
        for city in cities_by_state[state]: #[:2]:
            f.write('\n')
            print (city)
            c_list = city.split('-')[:-1]
            city_only = '-'.join(c_list)
            f.write(city_only+',')
            f.write(state+',')
            session = HTMLSession()
            flag = False
            # Keep trying until page is obtained
            while not flag:
                try:
                    r = session.get(URL+city+'.html')
                    delay = random.randint(10,20)
                    time.sleep(delay)
                    flag = True
                except:
                    print ('Error')
                    flag = False

            delay = random.randint(10,20)
            time.sleep(delay)

# Geographic information
            try:
                coordinates = r.html.find('#coordinates', first=True)
                lat=(((coordinates.text).split(',')[0]).split(':')[1]).strip()
#                print ('Latitude', lat)
                lon=(((coordinates.text).split(',')[1]).split(':')[1]).strip()
#                print ('Longitude', lon)
            except:
                lat=''
                lon=''
            f.write(lat+',')
            f.write(lon+',')
            try:
                zipcodes = r.html.find('#zip-codes', first=True)
                zips=(((zipcodes.text).strip('.')).split(':')[1]).split(',')
                if '.' in zips[-1]:
                    zips[-1] = (zips[-1].split('.'))[0]
            except:
                zips=[]
            f.write(':'.join(zips)+',')
#            print ('Zipcodes', (((zipcodes.text).strip('.')).split(':')[1]).split(','))
# Demographics
            try:
                population = r.html.find('#city-population', first=True)
                pop = (((((population.text).split(':')[1]).split('(')[0]).strip('.')).strip()).split('.')[0]
                pop = remove_comas(pop)
            except:
                pop=''
            f.write(pop+',')
#            print ('Population', pop)
            try:
                population_density = r.html.find('#population-density', first=True)
                pop_dens = ((population_density.text).split(':')[2]).split('people')[0].strip()
                pop_dens = remove_comas(pop_dens)
            except:
                pop_dens=''
            f.write(pop_dens+',')
#            print ('Population density', pop_dens)
            try:
                sexes = r.html.find('#population-by-sex', first=True)
                males = ((sexes.text).split(':')[1]).split('(')[0].strip()
                males = remove_comas(males)
                females = ((sexes.text).split(':')[2]).split('(')[0].strip()
                females = remove_comas(females)
            except:
                males = ''
                females = ''
            f.write(males+',')
#            print ('Males', males)
            f.write(females+',')
#            print ('Females', females)
            try:
                median_age = r.html.find('#median-age', first=True)
                age =  ((median_age.text).split(':')[1]).split('years')[0].strip()
            except:
                age = ''
            f.write(age+',')
#            print ('Median age', age)
            # Race
            races_dict = {}
            try:
                races = r.html.find('#races-graph', first=True)
                races_list = (races.html).split('<span')
                races_selected = races_list[1:]
                for el in races_selected:
                    if len(el.split('>')) == 3:
                        num = (el.split('>')[1]).split('<')[0]
                    else:
                        races_dict[ (el.split('>')[3]).split('<')[0] ] = remove_comas(num)
            except:
                continue
            if 'White alone' not in races_dict.keys():
                races_dict['White alone'] = ''
            if 'Black alone' not in races_dict.keys():
                races_dict['Black alone'] = ''
            if 'Hispanic' not in races_dict.keys():
                races_dict['Hispanic'] = ''
            if 'Asian alone' not in races_dict.keys():
                races_dict['Asian alone'] = ''
            if 'American Indian alone' not in races_dict.keys():
                races_dict['American Indian alone'] = ''
            if 'Native Hawaiian and Other Pacific Islander alone' not in races_dict.keys():
                races_dict['Native Hawaiian and Other Pacific Islander alone'] = ''
            if 'Other race alone' not in races_dict.keys():
                races_dict['Other race alone'] = ''
            if 'Two or more races' not in races_dict.keys():
                races_dict['Two or more races'] = ''
                
            f.write(races_dict['White alone']+',')
            f.write(races_dict['Black alone']+',')
            f.write(races_dict['Hispanic']+',')
            f.write(races_dict['Asian alone']+',')
            f.write(races_dict['American Indian alone']+',')
            f.write(races_dict['Native Hawaiian and Other Pacific Islander alone']+',')
            f.write(races_dict['Other race alone']+',')
            f.write(races_dict['Two or more races']+',')
#            for race in races_dict.keys():
#                print (race, races_dict[race])
            # Marital status
            marital_dict = {}
            try:
                marital_status = r.html.find('#marital-info', first=True)
                marital_list = (marital_status.text).split(':')[1:]
                marital_list_clean = []
                for n, el in enumerate(marital_list):
                    if n == 0:
                        marital_list_clean.append(el.strip())
                    elif n == len(marital_list)-1:
                        marital_list_clean.append((el.strip('%')).strip())
                    else:
                        marital_list_clean.append((el.split('%')[0]).strip())
                        marital_list_clean.append((el.split('%')[1]).strip())
                for n, el in enumerate(marital_list_clean):
                    if n % 2 == 0:
                        marital_dict[el] = marital_list_clean[n+1]
            except:
                continue
            if 'Never married' not in marital_dict.keys():
                marital_dict['Never married'] = ''
            if 'Now married' not in marital_dict.keys():
                marital_dict['Now married'] = ''
            if 'Separated' not in marital_dict.keys():
                marital_dict['Separated'] = ''
            if 'Widowed' not in marital_dict.keys():
                marital_dict['Widowed'] = ''
            if 'Divorced' not in marital_dict.keys():
                marital_dict['Divorced'] = ''
            f.write(marital_dict['Never married']+',')
            f.write(marital_dict['Now married']+',')
            f.write(marital_dict['Separated']+',')
            f.write(marital_dict['Widowed']+',')
            f.write(marital_dict['Divorced']+',')
#            for status in marital_dict.keys():
#                print (status, marital_dict[status])
            # Education
            education_dict = {}
            try:
                education = r.html.find('#education-info', first=True)
                education_list = (education.text).split(':')[1:]
                if 'minutes' in education_list[-1]:
                    commute_time = (education_list[-1].strip('minutes')).strip()
                    education_list = education_list[:-1]
                else:
                    commute_time = ''
                education_list.pop(0)
                education_list_clean = []
                for el in education_list:
                    education_list_clean.append(el.split('%')[0].strip())
                if len(education_list_clean) > 3:
                    education_list_clean = education_list_clean[:3]
                education_dict["High school"] = education_list_clean[0]
                education_dict["Bachelors"] = education_list_clean[1]
                education_dict["Graduate"] = education_list_clean[2]
            except:
                commute_time = ''
                if "High school" not in education_dict.keys():
                    education_dict["High school"] = ''
                if "Bachelors" not in education_dict.keys():
                    education_dict["Bachelors"] = ''
                if "Graduate" not in education_dict.keys():
                    education_dict["Graduate"] = ''
            for level in education_dict.keys():
                f.write(education_dict[level]+',')
            f.write(commute_time+',')
            
# Wealth
            try:
                cost_of_living = r.html.find('#cost-of-living-index', first=True)
                col = (((cost_of_living.text).split(':')[1]).split('(')[0]).strip()
            except:
                col = ''
            f.write(col+',')
#            print ('Cost of living index', col)
            try:
                median_income = r.html.find('#median-income', first=True)
                temp = (((median_income.text).split('Estimated median household income in')[1]).split()[1]).strip()[1:]
                household_income = remove_comas(temp)
                temp = (((median_income.text).split('Estimated per capita income in')[1]).split()[1]).strip()[1:]
                per_capita_income = remove_comas(temp)
            except:
                household_income = ''
                per_capita_income = ''
            f.write(household_income+',')
#            print ('Household income', household_income)
            f.write(per_capita_income+',')
#            print ('Per capita income', per_capita_income)
            try:
                median_rent = r.html.find('#median-rent', first=True)
                rent = remove_comas(((median_rent.text).split('$')[1]).strip('.'))
            except:
                rent = ''
            f.write(rent+',')
#            print ('Rent', rent)
            try:
                unemployment = r.html.find('#unemployment', first=True)
                unemp = ((unemployment.text).split('Here:')[1]).split('%')[0].strip()
            except:
                unemp = ''
            f.write(unemp+',')
#            print ('Unemployment', unemp)
            try:
                poverty_level = r.html.find('#poverty-level', first=True)
                poverty = (((poverty_level.text).split(':')[1]).split('%')[0]).strip()
            except:
                poverty = ''
            f.write(poverty+',')
#            print ('Percent poverty', poverty)

# Crime and police
            try:
                crime = r.html.find('#crime', first=True)
                crime_rate = (((((crime.html).split('City-Data.com crime index')[1]).split('</tfoot>')[0]).split('<td>')[-1])).split('<')[0]
                crime_rate = remove_comas(crime_rate)
            except:
                crime_rate = ''
            f.write(crime_rate+',')
#            print ("City-Data.com crime index", crime_rate)
            try:
                police = r.html.find('#police', first=True)
                police_per_1k = (((police.text).split('residents here:')[1]).split()[0]).strip()
            except:
                police_per_1k = ''
            f.write(police_per_1k+',')
#            print ("Police officers per 1000 residents", police_per_1k)

# Highway spending
            try:
                expenditures = r.html.find('#govFinancesE', first=True)
                highway_spending = (((expenditures.text).split('Regular Highways:')[1]).split('(')[0]).strip()[1:]
                highway_spending = remove_comas(highway_spending)
            except:
                highway_spending = ''
            f.write(highway_spending+',')
#            print ('Highway spending', highway_spending)

    f.close()
            

if __name__ == "__main__":
    main()
