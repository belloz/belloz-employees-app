from django.shortcuts import render
from .forms import AddEmployee
from django.shortcuts import redirect
from .models import Employees
from django.db.models import Q
from datetime import datetime
# Login required
from django.contrib.auth.decorators import login_required
import requests
# Create your views here.


@login_required
def index(request):
    API_KEY = "ecf5c3a62cc31e420d6feab7977329e8"
    API_KEY2 = "f33f5bb7d81312b303c2c4c3df4ab2bb"  # just in case for second, quick request (reserve)
    url = "http://api.openweathermap.org/data/2.5/weather"  # /forecast endpoint is for couple days!
    CITY = "Toronto"
    CITY_ID = 6167865  # Toronto (IDs are more accurate...)

    payload = {"APPID": API_KEY, "id": CITY_ID}
    r = requests.get(url, params=payload)

    json_obj = r.json()

    # Call to json parameters (temp, wind, population, city name, etc):
    temp_kelvin = json_obj["main"]["temp"]  # Temp
    temp_celc = temp_kelvin - 273.15  # conversion from Kelvin to Celcius/Celsius
    temp_celc = "%.1f %sC" % (temp_celc, chr(176))  # show 1 digit after comma
    # weather cloudy, sunny etc:
    weather_type = json_obj["weather"][0]["main"]
    weather_type_desc = json_obj["weather"][0]["description"]
    weather_icon = json_obj["weather"][0]["icon"]

    wind = json_obj["wind"]["speed"]  # Wind Speed
    wind_deg = json_obj["wind"]["deg"]  # Wind Degree
    wind = "%.1f km/h" % wind

    humidity = json_obj["main"]["humidity"]

    dictionary = {
        'nbar': 'home',
        'CITY': CITY,
        'weather_type': weather_type,
        'temp_celc': temp_celc,
        'weather_type_desc': weather_type_desc,
        'wind': wind,
        'wind_deg': wind_deg,
        'humidity': humidity,
        'weather_icon': weather_icon,
    }

    return render(request, 'employees_app/index.html', dictionary)


@login_required
# Display Employees:
def employees(request):
    employees_list = Employees.objects.all().order_by('last_name')

    query = request.GET.get("q")
    if query:
        employees_list = employees_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

    return render(request, 'employees_app/employees.html', {'employees_list': employees_list, 'nbar': 'em', 'page_employees': "page_employees"})


@login_required
# Add Employee:
def add_employee(request):
    if request.method == "POST":
        form = AddEmployee(request.POST)
        if form.is_valid(): # this part makes trouble:
            form.save()
            return redirect('employees_app:employees')
        else:
            return redirect('employees_app:index')
    else:
        form = AddEmployee()
    return render(request, 'employees_app/add_employee.html', {'form': form, 'nbar': 'add_em'})


@login_required
# Edit Employee:
def edit_employee(request, id):
    employee = Employees.objects.get(id=id)
    if request.method == "POST":
        form = AddEmployee(request.POST, instance=employee)
        if form.is_valid():
            employee.save()
            return redirect('employees_app:employees')
    else:
        form = AddEmployee(instance=employee)
    return render(request, 'employees_app/edit_employee.html', {'form': form})


# Remove Employee:
# def remove_employee(request, id):
#    employee = Employees.objects.id(id=id)
#    employee.delete()
#    return redirect('employees_app:employees')




# 404 Error:
def error404(request):
    return render(request, 'employees_app/404.html', {})
