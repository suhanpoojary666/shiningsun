from django.shortcuts import render
import requests

def calculate_aqi(pm25):

#api doesnot provide the US EPA AQI hence its calculated using pm
  
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]

    for (c_low, c_high, aqi_low, aqi_high) in breakpoints:
        if c_low <= pm25 <= c_high:
            aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (pm25 - c_low) + aqi_low
            return round(aqi)

    return None


def index(request):
    location='Bengaluru' #default location is set to Bengaluru
    location=request.POST.get('location','Bengaluru')

    BASE_URL = 'http://api.weatherapi.com/v1/current.json'

    params = {  
        'key': '4c3eb9c9a70241409a3100318251004',
        'q': location,  
        'aqi': 'yes'        
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code ==200:

        all_data={} #this dict. will store all the data dict. and will be sent with render request
        currents={} #this dict. will store all the current weather data
        history={}  #this dict. will store all the weather history data(past 7 days)
        alerts={}   #this will store the weather alerts if any    

        current = response.json()  

        currents['area']=current['location']['name']
        currents['country']=current['location']['country']
        currents['temperature']=current['current']['temp_c']
        currents['condition']=current['current']['condition']['text']
        currents['aqi']=calculate_aqi(current['current']['air_quality']['pm2_5'])
        currents['icon']=current['current']['condition']['icon']
        currents['humidity']=current['current']['humidity']
        currents['wind']=current['current']['wind_kph']
        currents['uv']=current['current']['uv']


        #slicing the string with present date for weather history of past 7 days

        time=current['current']['last_updated'] #time in 'yyyy-mm-dd hh:mm:ss' format
        year=time[0:4]
        month=time[5:7]    #slicing it to 'yyyy','mm' and 'dd' format for fetching the history data 
        day=time[8:10]
        d=int(day)
        m=int(month)
        y=int(year)


        for i in range(8):

            d=int(d)
            m=int(m)    #converting it to 'int' type for arithmatic operation
            y=int(y)   
            
            # calculates 7 past dates without any conflicts like leap years previous month etc

            if m==1 or m==5 or m==7 or m==9 or m==11:
                x=30
            elif m==2 or m==4 or m==6 or m==8 or m==10 or m==12 :
                x=31
            else:
                if y%400==0:
                    x=29
                else:
                    x=28

            d=d-1
            if d==0:
                d=x
                m=m-1
                if m==0:
                    m=12
                    y=y-1

            d=str(d)
            m=str(m)    
            y=str(y)

            if len(d)==1:   #if day or month is single digit converting it to '0X' format to satisfy the dd-mm format
                d='0'+d
            if len(m)==1:
                m='0'+m

            HIS_URL = 'http://api.weatherapi.com/v1/history.json'

            params1 = {  
            'key': '4c3eb9c9a70241409a3100318251004',
            'q': location, 
            'dt': f"{y}-{m}-{d}", 
            'aqi': 'yes'      
            }

            response1 = requests.get(HIS_URL, params=params1)
            history_data = response1.json()
            
            history[i]={}   #stores the av_temp and weather for past 7 days each in a nested dictionary

            history[i]["av_temp"] = history_data['forecast']['forecastday'][0]['day']['avgtemp_c']
            history[i]["weather"] = history_data['forecast']['forecastday'][0]['day']['condition']['text'] 
            history[i]["icon"] = history_data['forecast']['forecastday'][0]['day']['condition']['icon']
            history[i]["date"]=f"{d}-{m}-{y}"


        #data about current weather

        ALR_URL = 'http://api.weatherapi.com/v1/forecast.json'

        params2={
            'key': '4c3eb9c9a70241409a3100318251004',
            'q': location, 
            'days': 3,
            'alerts': 'yes'        
        }

        response2=requests.get(ALR_URL,params=params2)
        alert_data=response2.json()
        
        if alert_data['alerts']['alert']:
                alert=alert_data['alerts']['alert'][0]
                alerts['headline']=alert['headline']
                alerts['severity']=alert['severity']
                alerts['areas']=alert['areas']
                alerts['effective']=alert['effective'][:10]
                alerts['expires']=alert['expires'][:10] #slicing the time to 'yyyy-mm-dd' format
                alerts['instruction']=alert['instruction']
                alerts['certainty']=alert['certainty']
                alerts['urgency']=alert['urgency']
                alerts['desc']=alert['desc']
                alerts['event']=alert['event']
                

        all_data={
            'current':currents,
            'history':history,
            'alert':alerts
        } 
        print(alert_data['alerts']['alert'])
        return render(request,'home.html',all_data)
        
    else:
        return render(request,'error.html',{'location':location})