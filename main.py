import os
import requests
import json
import pytz
import datetime
import aiohttp
import asyncio
import time
from playsound import playsound



MUSIC_URL = os.path.join("music", "song1.mp3")
COWIN_API = "https://cdn-api.co-vin.in/api"
CONFIG_FILE = "config.json"

STATES_META = [{'state_id': 1, 'state_name': 'Andaman and Nicobar Islands'}, {'state_id': 2, 'state_name': 'Andhra Pradesh'}, {'state_id': 3, 'state_name': 'Arunachal Pradesh'}, {'state_id': 
4, 'state_name': 'Assam'}, {'state_id': 5, 'state_name': 'Bihar'}, {'state_id': 6, 'state_name': 'Chandigarh'}, {'state_id': 7, 'state_name': 'Chhattisgarh'}, {'state_id': 8, 'state_name': 'Dadra and Nagar Haveli'}, {'state_id': 37, 'state_name': 'Daman and Diu'}, {'state_id': 9, 'state_name': 'Delhi'}, {'state_id': 10, 'state_name': 'Goa'}, {'state_id': 11, 'state_name': 'Gujarat'}, {'state_id': 12, 'state_name': 'Haryana'}, {'state_id': 13, 'state_name': 'Himachal Pradesh'}, {'state_id': 14, 'state_name': 'Jammu and Kashmir'}, {'state_id': 15, 'state_name': 'Jharkhand'}, {'state_id': 16, 'state_name': 'Karnataka'}, {'state_id': 17, 'state_name': 'Kerala'}, {'state_id': 18, 'state_name': 'Ladakh'}, {'state_id': 19, 'state_name': 'Lakshadweep'}, {'state_id': 20, 'state_name': 'Madhya Pradesh'}, {'state_id': 21, 'state_name': 'Maharashtra'}, {'state_id': 22, 'state_name': 'Manipur'}, {'state_id': 23, 'state_name': 'Meghalaya'}, {'state_id': 24, 'state_name': 'Mizoram'}, {'state_id': 25, 'state_name': 'Nagaland'}, {'state_id': 26, 'state_name': 'Odisha'}, {'state_id': 27, 'state_name': 'Puducherry'}, {'state_id': 28, 'state_name': 'Punjab'}, {'state_id': 29, 'state_name': 'Rajasthan'}, {'state_id': 30, 'state_name': 'Sikkim'}, {'state_id': 31, 'state_name': 'Tamil Nadu'}, {'state_id': 32, 'state_name': 'Telangana'}, {'state_id': 33, 'state_name': 'Tripura'}, {'state_id': 34, 'state_name': 'Uttar Pradesh'}, {'state_id': 35, 'state_name': 'Uttarakhand'}, {'state_id': 36, 'state_name': 'West Bengal'}]
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

async def play_song():
    playsound(MUSIC_URL)

def read_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_state_meta():
    global STATES_META
    response = requests.get(
        COWIN_API + '/v2/admin/location/states',
        headers=HEADERS
    )
    STATES_META = response.json()["states"]

def get_state_ids(states):
    state_ids = []
    for state in STATES_META:
        if state["state_name"] in states:
            state_ids.append(state["state_id"])
    return state_ids

def get_district_ids(state_ids, states, districts):
    district_ids = []

    #Get districts for each state

    for state_id, state in zip(state_ids, states):
        response = requests.get(
            COWIN_API + f'/v2/admin/location/districts/{state_id}',
            headers = HEADERS
        )
        for district in response.json()["districts"]:
            if district["district_name"] in districts[state]:
                district_ids.append(district["district_id"])
    
    return district_ids

async def get_slots_district(session, district_id):
    IST = pytz.timezone('Asia/Kolkata')
    date = datetime.datetime.now(IST).strftime("%d-%m-%Y")
    async with session.get(COWIN_API + '/v2/appointment/sessions/public/calendarByDistrict', params={
        "district_id": district_id,
        "date": date
    }, headers=HEADERS) as response:
        response_json = await response.json()
        await asyncio.sleep(1)
        return response_json

async def get_slots_pincode(session, pincode):
    IST = pytz.timezone('Asia/Kolkata')
    date = datetime.datetime.now(IST).strftime("%d-%m-%Y")
    async with session.get(COWIN_API + '/v2/appointment/sessions/public/calendarByPin', params={
        "pincode": pincode,
        "date": date
    }, headers=HEADERS) as response:
        response_json = await response.json()
        await asyncio.sleep(1)
        return response_json

async def check_pins(session,pincodes):
    results = []
    pincode_responses = await asyncio.gather(*(get_slots_pincode(session, pincode) for pincode in pincodes))
    for response in pincode_responses:
        for center in response["centers"]:
            if center["fee_type"] == "Paid":
                for sesh in center["sessions"]:
                    if sesh["min_age_limit"] == 18 and sesh["available_capacity"] > 0:
                        results.append({
                            "Name": center["name"],
                            "District": center["district_name"],
                            "Pincode": center["pincode"],
                            "Date": sesh["date"],
                            "Vaccine": sesh["vaccine"],
                            "Dose1": sesh["available_capacity_dose1"],
                            "Dose2": sesh["available_capacity_dose2"]
                        })
    return results

async def check_districts(session, district_ids):
    results = []
    district_responses = await asyncio.gather(*(get_slots_district(session, district) for district in district_ids))
    for response in district_responses:
        for center in response["centers"]:
            if center["fee_type"] == "Paid":
                for sesh in center["sessions"]:
                    if sesh["min_age_limit"] == 18 and sesh["available_capacity"] > 0:
                        results.append({
                            "Name": center["name"],
                            "District": center["district_name"],
                            "Pincode": center["pincode"],
                            "Date": sesh["date"],
                            "Vaccine": sesh["vaccine"],
                            "Dose1": sesh["available_capacity_dose1"],
                            "Dose2": sesh["available_capacity_dose2"]
                        })
    return results

async def check_cowin(pincodes, district_ids):
    while True:
        results = []
        #Get client session
        async with aiohttp.ClientSession() as session:
            pins_and_districts = await asyncio.gather(check_pins(session, pincodes), check_districts(session, district_ids))
            results = pins_and_districts[0] + pins_and_districts[1]
        if len(results) > 0:
            print(results)
            await play_song()
        else:
            print("No slots buddy!")
        time.sleep(60)

if __name__ == "__main__":

    #Get the states and their ids
    #get_state_meta()

    #Read the configs
    configs = read_config()

    #Get states and districts from the config
    districts = configs["districts"]
    states = list(districts.keys())
    states.sort()

    #Get state_ids
    state_ids = get_state_ids(states)
    print(f"State IDs: {state_ids}")

    #Get district_ids
    district_ids = get_district_ids(state_ids, states, districts)
    print(f"District IDs: {district_ids}")

    #Get pincodes
    pincodes = configs["pincodes"]
    
    asyncio.run(check_cowin(pincodes, district_ids))



