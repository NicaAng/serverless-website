import json
import string
from datetime import date
from datetime import time
from datetime import datetime
import boto3

def lambda_handler(event,context):

    ## DECALARATIONS ##   
    def decl_var():
        global today, date_time, dynamodb, ord_table, inv_table
        today = date.today()
        date_time = str(datetime.now())
        dynamodb = boto3.resource('dynamodb')
        ord_table = dynamodb.Table('moms-creamy-orders')
        inv_table = dynamodb.Table('moms-creamy-inventory')

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
    
    ## GET NO. OF STOCKS FROM INVENTORY TABLE ##
    def get_stocks():
        global stock
        inventory = inv_table.get_item(
            Key={
            'DATE': str(today),
            'OPEN': 'yes'
            }
        )
        stock = inventory['Item']

    ## TOTAL BILLING ##
    def calc_bill():
        global total_bill, avail_fl
        avail_fl = "yes"
        total_bill = 0
        price_list = dict(ube_cheese=130,mb_nutella=120,mb_pb=110,mb_cheese=100,cookies=130,cc_garlic_2=100,cc_garlic_4=200)
        for x in order_dict:
            if x == "name" or x == "cc-num" or x == "dday-agreed" or x == "book-my-own":
                continue
            elif x == "cc-garlic-pcs":
                y = order_dict[x]
                if y == "2" and ((stock[x]["2"]-order_dict["cc-num"]) >= 0):
                    total_bill += (order_dict["cc-num"] * price_list["cc_garlic_2"])       
                if y == "4" and ((stock[x]["4"]-order_dict["cc-num"]) >= 0):
                    total_bill += (order_dict["cc-num"] * price_list["cc_garlic_4"]) 
            elif (stock[x]-order_dict[x]) >= 0:
                if x == "ucp-num": total_bill += (order_dict[x] * price_list["ube_cheese"])
                if x == "mbn-num": total_bill += (order_dict[x] * price_list["mb_nutella"])
                if x == "mbp-num": total_bill += (order_dict[x] * price_list["mb_pb"])
                if x == "mbc-num": total_bill += (order_dict[x] * price_list["mb_cheese"])
                if x == "ckies-num": total_bill += (order_dict[x] * price_list["cookies"])
            else:
                avail_fl = "no"
                break
    
    ## CREATE ORDER REFERENCE NUMBER ##
    def create_refnum():
        global ref_number
        ref_number = "REF"+str(today.day)+str(today.month)+str(stock["orders-today"]+1)

    ## LOG ORDER TO DYNAMODB ##
    def put_order():
        ord_table.put_item(
            Item={
                'REFNUM': ref_number,
                'Name': order_dict["name"],
                'TotalBill': total_bill,
                'Confirmation':'notpaid',
                'OrderCreated': date_time
                }
        )
    
    decl_var()
    make_dict()
    get_stocks()
    calc_bill()
    
    if avail_fl == "yes":
        create_refnum()
        put_order()
        msg = f"Thanks for ordering {order_dict['name']}! Ref: {ref_number} Total Bill: {total_bill}"
    else:
        msg = f"Hi {order_dict['name']}! We can't complete your order :( \
            We have limited stocks today. Please re-order :) \
            Ube Cheese pandesal: {stock['ucp-num']} \
            Milk bread - Nutella: {stock['mbn-num']} \
            Milk bread - Peanut Butter: {stock['mbp-num']} \
            Milk bread - cheese: {stock['mbc-num']} \
            Cream Cheese Garlic Bread (2pcs per pack): {stock['cc-garlic-pcs']['2']} \
            Cream Cheese Garlic Bread (4pcs per pack): {stock['cc-garlic-pcs']['4']} \
            Cookies: {stock['ckies-num']}" 

    ## RETURN MESSAGE ##
    return {
       'statusCode': 200,
       'headers':{'Access-Control-Allow-Origin':'http://momscreamy.com'},
       'body': json.dumps(msg)
    }


########################## SAMPLE INPUT & RETURN FROM HTML REQUEST ##########################

event = dict(body="name=momscreamy&ucp-num=1&mbn-num=0&mbp-num=0&mbc-num=0&cc-garlic-pcs=2&cc-num=1&ckies-num=0&dday-agreed=on")
print(lambda_handler(event)["body"])
print(order_dict)