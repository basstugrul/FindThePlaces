import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("GOOGLE_PLACES_API_KEY")

def get_nearby_places(api_key, location, radius=20000, keywords=None, max_results=None):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    if keywords is None:
        keywords = input("Type the places you want to list (Example: Coffee Shop,Pharmacy): ").split(',')
    
    places = []

    for keyword in keywords:
        params = {
            'location': location,
            'radius': radius,
            'keyword': keyword,
            'types': 'stores',
            'key': api_key,
        }

        while True:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                places_data = response.json().get('results', [])
                places.extend(places_data)
                next_page_token = response.json().get('next_page_token')
                
                # Waiting time, so it doesn't send any invalid requests.
                time.sleep(2)

                if not next_page_token or (max_results and len(places) >= max_results):
                    break

                params['pagetoken'] = next_page_token
            else:
                print("Hata kodu:", response.status_code)
                print("Hata mesajı:", response.text)
                break

    return places

def get_place_details(api_key, place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
    'place_id': place_id,
    'key': api_key,
    'fields': 'name,vicinity,website,formatted_phone_number'
}


    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        place_details = response.json().get('result', {})
        return place_details
    else:
        print("Hata kodu:", response.status_code)
        print("Hata mesajı:", response.text)
        return None

def write_to_excel(data, file_path='places_data.xlsx'):
    selected_columns = ['name', 'vicinity', 'website', 'phone_number']
    places_with_contact_info = []

    for place in data:
        place_details = get_place_details(api_key, place.get('place_id'))
        contact_info = {
            'name': place.get('name', ''),
            'vicinity': place.get('vicinity', ''),
            'website': place.get('website', ''),
            'phone_number': place_details.get('formatted_phone_number', '')
        }
        places_with_contact_info.append(contact_info)

    df = pd.DataFrame(places_with_contact_info)[selected_columns]
    df.to_excel(file_path, index=False)
    print(f"Files have been printed to '{file_path}' successfully.")

if __name__ == "__main__":
    location = input("Type in the coordinates of the area (Example: 38.7223,35.4853): ")  # Coordinates of the area you want to seach
    radius = 20000  # as meter(20000 is max)  
    max_results = None #Give it a limit if you want to
    keywords = input("Type the places you want to list (Example: Coffee Shop,Pharmacy): ").split(',')
    places_data = get_nearby_places(api_key, location, radius, keywords, max_results=max_results)
    write_to_excel(places_data)
