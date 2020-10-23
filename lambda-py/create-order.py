import json
import string
from datetime import date
from datetime import time
from datetime import datetime
#import boto3

def lambda_handler(event):

    ## TIME DECALARATIONS ##   
    def set_date():
        global today, date_time 
        today = date.today()
        date_time = str(datetime.now())

    ## ORDER DETAILS TO DICT ##
    def make_dict():
        global order_dict
        order_request = event["body"]
        replace_space = order_request.replace("+", " ")
        order_list = list(replace_space.split("&"))
        order_dict = dict(s.split('=') for s in order_list)
        for x in order_dict:
            if x == "cc-num" or x == "ucp-num" or x == "mbn-num" or x == "mbp-num" or x == "mbc-num" or x == "ckies-num":
                new_int = int(order_dict[x])
                order_dict[x] = new_int

    ## TOTAL BILLING ##
    def calc_bill():
        global total_bill
        total_bill = 0
        price_list = dict(ube_cheese=130,mb_nutella=120,mb_pb=110,mb_cheese=100,cookies=130,cc_garlic_2=100,cc_garlic_4=200)
        for x in order_dict:
            if x == "ucp-num": total_bill += (order_dict[x] * price_list["ube_cheese"])
            if x == "mbn-num": total_bill += (order_dict[x] * price_list["mb_nutella"])
            if x == "mbp-num": total_bill += (order_dict[x] * price_list["mb_pb"])
            if x == "mbc-num": total_bill += (order_dict[x] * price_list["mb_cheese"])
            if x == "cc-garlic-pcs" and order_dict[x] == "2": total_bill += (order_dict["cc-num"] * price_list["cc_garlic_2"])        
            if x == "cc-garlic-pcs" and order_dict[x] == "4": total_bill += (order_dict["cc-num"] * price_list["cc_garlic_4"])  
            if x == "ckies-num": total_bill += (order_dict[x] * price_list["cookies"])
    
    ## CREATE ORDER REFERENCE NUMBER ##
    def create_refnum():
        global ref_number
        ref_number = "REF"+str(today.day)+str(today.month)

    # # LOG ORDER TO DYNAMODB ##
    # def put_order():
    #     dynamodb = boto3.resource('dynamodb')
    #     table = dynamodb.Table('moms-creamy-orders')
    #     table.put_item(
    #         Item={
    #             'REFNUM': ref_number,
    #             'Name': order_dict["name"],
    #             'TotalBill': total_bill,
    #             'Confirmation':'notpaid',
    #             'OrderCreated': date_time
    #             }
    #     )

    set_date()
    make_dict()
    calc_bill()
    create_refnum()
#    put_order()

    ## RETURN MESSAGE ##
    return {
       'statusCode': 200,
       'headers':{'Access-Control-Allow-Origin':'http://momscreamy.com'},
       'body': json.dumps(f"Thanks for ordering {order_dict['name']}! Ref: {ref_number} Total Bill: {total_bill}")
   }




      

        
## CHECK AVAILABLE STOCKS ##








########################## SAMPLE INPUT & RETURN FROM HTML REQUEST ##########################

event = dict(body="name=momscreamy&ucp-num=1&mbn-num=0&mbp-num=0&mbc-num=0&cc-garlic-pcs=2&cc-num=1&ckies-num=0&dday-agreed=on")
print(lambda_handler(event)["body"])
print(order_dict)