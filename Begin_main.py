try:
    import json
    import os
    import geocoder
    import io
    import requests
    import sys
    import SupportingFunctions as SF
    import pandas as pd
    from pandas import json_normalize
except ImportError:
    print("ERROR ! Module Import Failed - " + os.path.basename(__file__), "Console")
    print(sys.exc_info())
    input("Press Enter to continue...")
    exit(99)


def main():
    # Action 1 :
    # QueryLocations()
    # Action 2 :
    QueryFourSquare()
    # Action 3 :
    #QueryEthnicGroup()
    print("Done !")


def QueryLocations():
    print(">>> Action 1 : QueryLocations")
    api = "getPlanningareaNames?"
    myurl = url + api + OneMapAuth
    SF.log_to_report(QueryLocations, "w", "Location ID, Location Name, Latitude, Longitude")
    for value in SF.Query(myurl):
        my_dict = dict(value)
        location = str(my_dict['pln_area_n'])
        lat, lon = SF.QueryLocationData(location, "Singapore")
        SF.log_to_report(QueryLocations, "a", str(my_dict['id']) + "," + location + "," + str(lat) + "," + str(lon))
        PlanningArea.append(my_dict['pln_area_n'])


# Action 2 : For the Available Valid Locations, Query the venues in and around the location using FourSquare API
def QueryFourSquare():
    print(">>> Action 2 : QueryFourSquare")
    CLIENT_ID = 'ARRNPU155D51DSX4JHDRNJLSAR3GS2JB0BZJX1N550ACFA5A'  # your Foursquare ID
    CLIENT_SECRET = 'OGUGTHQP15HJCC31I3QXXEK2FCAESKJV5HMCINXK023514EQ'  # your Foursquare Secret
    VERSION = '20191231'  # Foursquare API version
    radius = 500
    LIMIT = 100
    print(">>> Reading File Into Data Frame : " + QueryLocations)
    df = pd.read_csv(QueryLocations)
    FourSquare = []
    for index, row in df.iterrows():
        if "#" in str(df['Location ID'][index]):
            continue
        Location = df[' Location Name'][index]
        LatValue = df[' Latitude'][index]
        LonValue = df[' Longitude'][index]
        print('    $ Latitude and longitude values of {} are {}, {}.'.format(Location, LatValue, LonValue))
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            VERSION,
            LatValue,
            LonValue,
            radius,
            LIMIT)
        results = requests.get(url).json()

        if "There aren't a lot of results near you" in str(results["response"]):
            FourSquare.append("No")
            continue
        else:
            FourSquare.append("Yes")
            SF.jsonwrite(venues + "\\" + str(Location) + ".json", results)
            FSQ_DF = ProcessFourSquareData(results)
            FSQ_DF.to_csv(venues + "\\" + str(Location) + "_FSQ.csv")

    df["FourSquare"] = FourSquare


def ProcessFourSquareData(results):
    venues = results['response']['groups'][0]['items']
    nearby_venues = json_normalize(venues)  # flatten JSON
    filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
    nearby_venues = nearby_venues.loc[:, filtered_columns]
    nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)
    nearby_venues["groupby"] = nearby_venues.apply(get_category_group, axis=1)
    nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

    return nearby_venues


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']

    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


def get_category_group(row):
    try:
        categories = row['categories']
    except:
        categories = row['venue.categories']

    if len(categories) == 0:
        return None
    else:
        value = categories

    HOTEL_RESTAURANT = ["hotel", "hotels", "food", "restaurant", "restaurants", "dining", "dine", "cuisine", "salad", "soup", "breakfast", "lunch", "dinner", "Pizza", "buffet", ""]
    GYM = ["gym", "fitness"]
    COFFEE_TEA = ["coffee", "tea", "juice", "Cafeteria"]
    BARS = ["bar", "bistro", "Brewery"]
    CLUB = ["club", "nightclub"]

    if [ele for ele in HOTEL_RESTAURANT if (ele in str(value).lower())]:
        return "Restaurant"
    elif [ele for ele in GYM if (ele in str(value).lower())]:
        return "Gym"
    elif [ele for ele in COFFEE_TEA if (ele in str(value).lower())]:
        return "Coffee/Tea Shops"
    elif [ele for ele in BARS if (ele in str(value).lower())]:
        return "Bars"
    elif [ele for ele in CLUB if (ele in str(value).lower())]:
        return "Club"
    else:
        return value


# ******************************************************************************************************************** #
# MAIN CODE #
# ******************************************************************************************************************** #

PlanningArea = []
OneMapAuth = "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjQwNzEsInVzZXJfaWQiOjQwNzEsImVtYWlsIjoia2FydGhpa3Jpc2huYWFAZ21haWwuY29tIiwiZm9yZXZlciI6ZmFsc2UsImlzcyI6Imh0dHA6XC9cL29tMi5kZmUub25lbWFwLnNnXC9hcGlcL3YyXC91c2VyXC9zZXNzaW9uIiwiaWF0IjoxNTg0MjE4Mjg1LCJleHAiOjE1ODQ2NTAyODUsIm5iZiI6MTU4NDIxODI4NSwianRpIjoiOTAzNzE1MTQ4MDhkZTJhOTQzOTIzYjA3ZjU2NTM0OWQifQ.X7u58B6VzQ_jMlkySJ41ftQiZx3oKlxttjNWHkvspB8"
API_2 = "getSpokenAtHome?"
API_3 = "getEthnicGroup?"
Location = "&planningArea=Bedok"
Year = "&year=2019"
url = "https://developers.onemap.sg/privateapi/popapi/"

QueryLocations = os.getcwd() + "\QueryLocations.csv"
venues = os.getcwd() + "\\venues"

url_2 = url + API_2 + OneMapAuth + Location + Year
url_3 = url + API_3 + OneMapAuth + Location + Year



main()

