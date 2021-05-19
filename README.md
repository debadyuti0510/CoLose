# CoLose

A simple python monitoring script that checks for 18-44 slot availability for vaccination in specific districts and/or pincodes.
When a slot is found, this script plays `music/song1.mp3` (replace that with your favorite song) and prints out the information on console as folows:

    [{'Name': 'Apollo Proton COVISHIELD', 'District': 'Chennai', 'Pincode': 600096, 'Date': '19-05-2021', 'Vaccine': 'COVISHIELD', 'Dose1': 0, 'Dose2': 19}, {'Name': 'Apollo Proton COVISHIELD', 'District': 'Chennai', 'Pincode': 600096, 'Date': '20-05-2021', 'Vaccine': 'COVISHIELD', 'Dose1': 0, 'Dose2': 25}]    

## Requirements
Creating a virtual environment is recommended.
This was developed on `Python 3.8`
Earlier versions may not work well with `asyncio` / `aiohttp`
### Install the requirements with pip
    pip install -r requirements.txt

## Customizing config
The config file contains two entries: `pincodes` and `districts`  
### Filter by pincode  
  

    "pincodes": [
        "700019",
        "700006"
    ]  

### Filter by district
  

    "districts": {
            "West Bengal": [
                "Kolkata",
                "North 24 Parganas"
            ],
            "Tamil Nadu": [
                "Chennai"
            ]
    }

## Run the monitoring script
    python main.py
