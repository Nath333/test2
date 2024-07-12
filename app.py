from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET
import logging

app = Flask(__name__)

# Configure basic logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def get_data():
    try:
        # Make a request to the API
        response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=45.7485&longitude=4.8467&current=temperature_2m,apparent_temperature,cloud_cover&hourly=temperature_2m,rain,cloud_cover,visibility&daily=sunrise,sunset&timezone=auto")
        data = response.json()

        # Log the response
        logging.debug(f"API response: {data}")

        # Check if the API call was successful
        if response.status_code != 200:
            raise ValueError("Failed to retrieve data")

        # Create a root XML element
        root = ET.Element("Data")

        # Add current weather data
        current_root = ET.SubElement(root, "CurrentWeather")
        for key, value in data['current'].items():
            child = ET.SubElement(current_root, key)
            child.text = str(value)

        # Add hourly data
        hourly_root = ET.SubElement(root, "HourlyWeather")
        for time, temp in zip(data['hourly']['time'], data['hourly']['temperature_2m']):
            hour = ET.SubElement(hourly_root, "Hour", time=time)
            ET.SubElement(hour, "Temperature").text = str(temp)
            # Safely access potentially missing data
            rain = data['hourly'].get('rain', [None] * len(data['hourly']['time']))
            cloud_cover = data['hourly'].get('cloud_cover', [None] * len(data['hourly']['time']))
            visibility = data['hourly'].get('visibility', [None] * len(data['hourly']['time']))
            ET.SubElement(hour, "Rain").text = str(rain)
            ET.SubElement(hour, "CloudCover").text = str(cloud_cover)
            ET.SubElement(hour, "Visibility").text = str(visibility)

        # Add sunrise and sunset times
        sun_cycle_root = ET.SubElement(root, "SunCycle")
        for date, sunrise, sunset in zip(data['daily']['time'], data['daily']['sunrise'], data['daily']['sunset']):
            day = ET.SubElement(sun_cycle_root, "Day", date=date)
            ET.SubElement(day, "Sunrise").text = sunrise
            ET.SubElement(day, "Sunset").text = sunset

        # Convert the XML tree to a string
        xml_str = ET.tostring(root, encoding='utf8', method='xml')
        return Response(xml_str, mimetype='text/xml')

    except Exception as e:
        # Log the error
        logging.error(f"Error retrieving data: {str(e)}")
        return Response(f"Error retrieving data: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(debug=True)
