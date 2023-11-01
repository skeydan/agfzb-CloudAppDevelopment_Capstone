import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    apikey = kwargs.get("apikey")
    try:
        if apikey:
            params = dict()
            params["text"] = kwargs.get("text")
            params["version"] = kwargs.get("version")
            params["features"] = kwargs.get("features")
            params["return_analyzed_text"] = kwargs.get("return_analyzed_text")
            
            response = requests.get(url, data=params, auth=HTTPBasicAuth('apikey', apikey), headers={'Content-Type': 'application/json'})
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        
        # Check if the response contains valid JSON
        response.raise_for_status()  # This will raise an exception if the response status code is an HTTP error.
        json_data = response.json()
        return json_data
    except Exception as e:
        # Handle the exception and log or print an error message
        print(f"Error in get_request: {e}")
        return None


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    print(json_result)
    print("############################################")
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    print(results)
    print("############################################")
    return results

def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    print('json_result from line 54',json_result)

    if json_result:
        dealers = json_result   
        dealer_doc = dealers[0]
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], full_name=dealer_doc["full_name"],
                                
                                st=dealer_doc["st"], zip=dealer_doc["zip"],short_name=dealer_doc["short_name"])
    return dealer_obj

def analyze_review_sentiments(text):
    url = "NLU_URL"
    api_key = "NLU_API_KEY"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']    
    return(label)


def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    print(json_result, "96")
    if json_result:
        if isinstance(json_result, list):  # Check if json_result is a list
            reviews = json_result
        else:
            reviews = json_result["data"]["docs"]

        # Check if 'reviews' is a list of one dictionary
        if isinstance(reviews, list) and len(reviews) == 1 and isinstance(reviews[0], dict):
            reviews = reviews[0]

        for dealer_review in reviews:
            print("dealer_review--------------------", dealer_review)  # Print dealer_review
            if isinstance(dealer_review, str):  # Check if dealer_review is a string
                try:
                    dealer_review = json.loads(dealer_review)
                except json.JSONDecodeError:
                    continue  # Skip this iteration if the JSON decoding fails

            review_obj = DealerReview(
                dealership=dealer_review.get("dealership"),
                name=dealer_review.get("name"),
                purchase=dealer_review.get("purchase"),
                review=dealer_review.get("review"),
                purchase_date=dealer_review.get("purchase_date"),
                car_make=dealer_review.get("car_make"),
                car_model=dealer_review.get("car_model"),
                car_year=dealer_review.get("car_year"),
                sentiment='',
                id=dealer_review.get("id")
            )

            # sentiment = analyze_review_sentiments(review_obj.review)
            # print(sentiment)
            # review_obj.sentiment = sentiment
            results.append(review_obj)

    return results

    def post_request(url, json_payload, **kwargs):
        response = requests.post(url, params=kwargs, json=json_payload)
        return response

