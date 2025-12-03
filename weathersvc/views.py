from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from weather_checker.models import Weather

from django.http import HttpResponse, HttpRequest
import requests
from weathersvc.models import  Weather
from datetime import datetime,timedelta

@csrf_exempt
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def weather_forecast(request):
    if request.method == 'POST':
        print('POST')
        return weather_details(request, False)
    return render(request, 'weather_forecast.html')

@csrf_exempt
def historical_weather(request):
    if request.method == 'POST':
        return queryDB(request)
    return render(request, 'historical_weather.html')

@csrf_exempt
def weather_details(request, historical):

    zipcode = request.POST.get('zipcode')

    result = requests.get( url_generator(zipcode, False))
    result = result.json()

    temperature = (result['main']['temp']-273)*5/9 + 32
    humidity = result['main']['humidity']
    windspeed = result['wind']['speed']*2.23
    dt = result['dt'] - 5*3600
    print(dt)
    updated_time = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')

    print(str(temperature) + ", " + str(humidity) + "," + str(windspeed))

    context = {}
    context['updated_time'] = updated_time
    context['zipcode'] = zipcode
    context['temperature'] = "%.1f"%temperature
    context['humidity'] = humidity
    context['windspeed'] = "%.1f"%windspeed

    weather_list = []
    url = url_generator(zipcode, True)
    print(url)
    forecast_result = requests.get(url_generator(zipcode, True)).json()

    for row in forecast_result['list']:
        dt = row['dt'] -5*3600
        time = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')
        temperature = "%.1f" % ((row['main']['temp']-273)*5/9 + 32)
        humidity = row['main']['humidity']
        windspeed = "%.1f" % (row['wind']['speed']*2.23)

        weather = create_and_save( time, temperature, humidity, windspeed, zipcode )
        weather_list.append(weather)

        context['weather_list'] = weather_list
        context['url'] = url

    return render(request, "details.html", context)

def queryDB(request):
    zipcode = request.POST.get('zipcode')
    date_string = request.POST.get('historical_date')
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    next_day = dt + timedelta(days=1)
    data = Weather.objects.filter(zipcode=zipcode).filter(updated_time__gt = dt).filter(updated_time__lt = next_day)
    weather_list = []
    for row in data:
        weather_list.append(row)
    context = {'weather_list': weather_list }
    context['zipcode'] = zipcode

    return render(request, 'details.html', context)

def create_and_save(time, temperature, humidity, windspeed, zipcode):
    # save it to db only if it doesn't exist
    weather = Weather(updated_time=time, temperature=temperature, humidity=humidity, windspeed=windspeed, zipcode= zipcode)
    exists = Weather.objects.filter(updated_time=time, zipcode = zipcode ).exists()
    if not exists:
        weather.save()
    return weather


# construct the full path URL for requests
def url_generator(zipcode, isForecast ):
    """
        Use openweathermap web service to query real weather data
        http://api.openweathermap.org/data/2.5/weather?zip=10533,us&APPID=2781183c04ce2d6c9f76cd423f747bd2
    """

    API_URL_BASE = 'http://api.openweathermap.org/data/2.5/'
    slug = ''
    if isForecast:
        slug = 'forecast'
    else:
        slug = 'weather'

    url = API_URL_BASE + slug + '?'
    appId = '2781183c04ce2d6c9f76cd423f747bd2'

    full_url = url + 'zip=' + zipcode + ',us&APPID=' + appId
    print('the url is ' + full_url)
    return full_url

