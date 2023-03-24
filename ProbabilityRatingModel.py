
from cmath import sqrt
from dis import dis

def linear(review_count, rating):
    """
    Function takes in review and rating as inputs, and computes a consolidated rating value based on the confidence of the rating achieved by the number of reviews availability
    This uses a LINEAR probability model.
    """

    if review_count <= 100:
        return (0.7+0.003*review_count)*rating
    else:
        return rating

def exponential(review_count, rating):
    """
    Function takes in review and rating as inputs, and computes a consolidated rating value based on the confidence of the rating achieved by the number of reviews availability
    This uses an EXPONENTIAL probability model.
    """
    
    return abs(review_count/(sqrt((1/0.09)*(review_count**2)+10000)) + 0.7)*rating

def weighted(rating, rating_pref, price, price_pref, distance, distance_pref):
    """
    Function takes in order of preference of user for price, distance and rating and returns the combined weighted score
    """
    #to convert price and distance to a score out of 10, to match ratings
    price_conversion_factor = 10/4
    distance_conversion_factor = 10/5

    if distance < 250:
        distance_score = 5
    elif distance < 500:
        distance_score = 4
    elif distance < 1000:
        distance_score = 3
    elif distance < 2000:
        distance_score = 2
    else: distance_score = 1

    weight_dict = {
        1: 0.5,
        2: 0.3,
        3: 0.2
    }

    price_conversion_dict = {
        1: 4,
        2: 3,
        3: 2,
        4: 1,
        None: 2.5
    }

    if not rating:
        rating = 5

    return weight_dict[rating_pref]*rating + weight_dict[price_pref]*price_conversion_dict[price]*price_conversion_factor + weight_dict[distance_pref]*distance_score*distance_conversion_factor
