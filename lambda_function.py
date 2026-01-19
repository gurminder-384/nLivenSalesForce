
#TODO: Get time of day variable
#TODO: Move connection info to seperate rds_config file.
#TODO: Fix Event Date and Time Fields
#TODO: Check if closeDate needs to be converted to local timezone.


from simple_salesforce import Salesforce
from datetime import datetime, timezone
import logging
import os
import json
import pytz
import time
from uszipcode import ZipcodeSearchEngine

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    logger.info('Lambda handler called successful.')

    header_data = event['headers']
    header_key = header_data['Authorization'].split()[1]
    logger.info(header_key)
    logger.info(event)

    #if os.environ['SecretKey'] == header_key or os.environ['ShubertKey'] == header_key:
    if os.environ['SecretKey'] == header_key:
        payload = json.loads(event['body'])
        data = payload['data']
        webhook_type = payload['webhookType']

        # Initialize PersonEmail to empty string by default
        PersonEmail = ''
        # Initialize customer to None by default
        customer = None

        if data.get('customer') is not None:
          customer = data['customer']
          PersonEmail = '' if customer.get('email') is None else customer['email']
          
        if PersonEmail != '' and (data.get('salesChannel') in ['Web', 'PointOfSale', 'API', 'Outlet', 'GroupSales']):
            batch_date = datetime.today().strftime('%Y-%m-%d')
            local_tz = pytz.timezone('US/Eastern')
            search = ZipcodeSearchEngine()
            states = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'American Samoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'Northern Mariana Islands','MS': 'Mississippi','MT': 'Montana','NA': 'National','NC': 'North Carolina','ND': 'North Dakota','NE': 'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada','NY': 'New York','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'Puerto Rico','RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'Virgin Islands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'West Virginia','WY': 'Wyoming'}
            countries = {'AE':'United Arab Emirates', 'AF':'Afghanistan', 'AL':'Albania', 'AM':'Armenia', 'AR':'Argentina', 'AT':'Austria', 'AU':'Australia', 'AW':'Aruba', 'AX':'Aland Islands', 'BD':'Bangladesh', 'BE':'Belgium', 'BG':'Bulgaria', 'BM':'Bermuda', 'BN':'Brunei Darussalam', 'BR':'Brazil', 'BS':'Bahamas', 'BW':'Botswana', 'CA':'Canada', 'CG':'Congo', 'CH':'Switzerland', 'CI':"Cote d'Ivoire", 'CL':'Chile', 'CN':'China', 'CO':'Colombia', 'CR':'Costa Rica', 'CY':'Cyprus', 'CZ':'Czech Republic', 'DE':'Germany', 'DK':'Denmark', 'DO':'Dominican Republic', 'DZ':'Algeria', 'EC':'Ecuador', 'EE':'Estonia', 'EG':'Egypt', 'ES':'Spain', 'ET':'Ethiopia', 'FI':'Finland', 'FJ':'Fiji', 'FR':'France', 'GB':'United Kingdom', 'GE':'Georgia', 'GH':'Ghana', 'GI':'Gibraltar', 'GL':'Greenland', 'GR':'Greece', 'GT':'Guatemala', 'HN':'Honduras', 'HR':'Croatia', 'HT':'Haiti', 'HU':'Hungary', 'ID':'Indonesia', 'IE':'Ireland', 'IL':'Israel', 'IN':'India', 'IQ':'Iraq', 'IS':'Iceland', 'IT':'Italy', 'JM':'Jamaica', 'JO':'Jordan', 'JP':'Japan', 'KE':'Kenya', 'KR':'Korea, South', 'KW':'Kuwait', 'KY':'Cayman Islands', 'LB':'Lebanon', 'LI':'Liechtenstein', 'LK':'Sri Lanka', 'LR':'Liberia', 'LT':'Lithuania', 'LU':'Luxembourg', 'LV':'Latvia', 'LY':'Libya', 'MA':'Morocco', 'MM':'Myanmar', 'MN':'Mongolia', 'MO':'Macao', 'MT':'Malta', 'MX':'Mexico', 'MY':'Malaysia', 'NE':'Niger', 'NG':'Nigeria', 'NI':'Nicaragua', 'NL':'Netherlands', 'NO':'Norway', 'NZ':'New Zealand', 'PA':'Panama', 'PE':'Peru', 'PF':'French Polynesia', 'PH':'Philippines', 'PK':'Pakistan', 'PL':'Poland', 'PS':'Palestine', 'PT':'Portugal', 'PY':'Paraguay', 'QA':'Qatar', 'RO':'Romania', 'RS':'Serbia', 'RU':'Russia', 'SA':'Saudi Arabia', 'SE':'Sweden', 'SG':'Singapore', 'SI':'Slovenia', 'SK':'Slovakia', 'SV':'El Salvador', 'TH':'Thailand', 'TN':'Tunisia', 'TR':'Turkey', 'TT':'Trinidad and Tobago', 'UA':'Ukraine', 'US':'United States', 'UY':'Uruguay', 'UZ':'Uzbekistan', 'VE':'Venezuela', 'VN':'Viet Nam', 'ZA':'South Africa', 'GU':'Guam', 'HK':'Hong Kong', 'PR':'Puerto Rico', 'TW':'Taiwan'}

            try:
                #Sandbox
                #sf = Salesforce(username='sslabicki@nederlander.com.justinpart', password = 'Neder2021', security_token='5Mr15YY8pkclxMilCetvN8qa', sandbox = True, client_id='LambdaPy')
                #Production
                sf = Salesforce(username='kyle.bowerman@atrium.ai', password = 'Bozeman1972!', security_token='Sbfdp4OcsDGwV3662OfHUkLx', client_id='LambdaPy')
                logger.info('SUCCESS: Connection to Salesforce established.')
            except:
                logger.error("ERROR: Unexpected Error: Could not connect to Salesforce.")

            event = data.get('event')
            order_items = data.get('orderItems')
            venue = data.get('venue')
            logger.info(data)

            if(customer is not None):
                logger.info(customer['email'])
                logger.info(data['id'])
            
            if webhook_type == 'CustomerCreated':
                logger.info(data)
            
            if webhook_type == 'CustomerUpdated':
                logger.info(data)
             
            if webhook_type == 'OrderUpdated':
                Nliven_Order_Number__c = data['id']
                order_items = data['orderItems']

                order_items_query = sf.query_all(f"SELECT Nliven_Order_Number__c, Id, Order_Item_Type__c, Fee_Name__c, Section_Item__c, Row_Item__c, SeatID_Item__c, Name, Ticket__c FROM Order_Item__c WHERE Nliven_Order_Number__c = '{Nliven_Order_Number__c}'")
                order_items_list = list(order_items_query.items())

                Voided__c = data['orderStatus']

                if Voided__c == 'Cancelled':
                    Voided__c = True
                    Voided_Date__c = data['localLastUpdated']
                    logger.info(f"Order items list: {order_items_list}")
                    logger.info(f"Order items list: {order_items_list[2][1]}")
                    for i in order_items_list[2][1]:
                      try:
                        updated_order = sf.Opportunity.update(i['Ticket__c'], {'Voided__c': Voided__c, 'Voided_Date__c': Voided_Date__c})
                        logger.info("Voiding Opportunity for {Voided__c}")
                      except:
                        logger.exception('Error Voiding Opportunity.')
                      # try:
                      #   updated_order = sf.Opportunity.update(i['Ticket__c'], {'Voided__c' : Voided__c, 'Voided_Date__c' : Voided_Date__c})
                      #   logger.info("Voiding Opportunity for {Voided__c}")
                      # except:
                      #   logger.exception('Error Voiding Opportunity.')
                    #Could maybe do opportunity and wholesale order items updating here...just need to query all order items that are not voided.  Works!
                    all_items = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_Order_Number__c = '{Nliven_Order_Number__c}' AND Voided_Item__c = False")
                    logger.info(f"Order items list: {list(all_items.items())[2][1]}")
                    for i in list(all_items.items())[2][1]:
                      try:
                        updated_order = sf.Order_Item__c.update(i['Id'], {'Voided_Item__c' : True, 'Local_Voided_Date_Item__c' : Voided_Date__c})
                        logger.info('Voiding all Order Items.')
                      except:
                        logger.exception('Error Voiding Order Items.')

                else:
                    Voided__c = False
                    Voided_Date__c = ''
                    logger.info(f"Order items list: {order_items_list[2][1]}")
                    for i in order_items_list[2][1]:
                      try:
                        updated_order = sf.Opportunity.update(i['Ticket__c'], {'Voided__c' : Voided__c, 'Voided_Date__c' : Voided_Date__c})
                        logger.info("Voiding Opportunity for {Voided__c}")
                      except:
                        logger.exception('Error Voiding Opportunity.')


                tix = []

                for i in range(len(order_items)):
                    d = {k: v for k, v in order_items[i].items()} #if k != "childOrderItems"}
                    tix.append(d)
                    logger.info(d)


                voided_tix = 0

                for i in tix:
                    if i['orderItemType'] == 'Ticket':
                        ticket_query_condition = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_AWS_ID_Item__c = '{i['id']}'")
                        logger.info('TICKET CONDITION QUERY')
                        logger.info(ticket_query_condition)
                        # if(list(ticket_query_condition.items())[2][1][0]['Id'] in ('null', 'NULL', '', None)):
                        if(list(ticket_query_condition.items())[2][1] == []):
                            ticket_query = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_Order_Number__c = '{Nliven_Order_Number__c}' AND Section_Item__c = '{i['section']}' AND Row_Item__c = '{i['row']}' AND Nliven_Event_ID_Item__c = '{i['eventId']}' AND SeatID_Item__c = '{i['seatId']}' AND Order_Item_Type__c = '{i['orderItemType']}'")
                            logger.info(ticket_query)
                            ticket_id = list(ticket_query.items())[2][1][0]['Id'] #This gets the Id for the individual ticket.  We are going to loop through the list and update the void status.  Still need to figure out facility fee.
                        else:
                            ticket_id = list(ticket_query_condition.items())[2][1][0]['Id'] #This gets the Id for the individual ticket.  We are going to loop through the list and update the void status.  Still need to figure out facility fee.

                        
                        Voided_Item__c = i['voided']
                        Local_Voided_Date_Item__c = i['localVoidedDate']
                        #Use this to keep track of how many facility fees need to be voided
                        if Voided_Item__c == True:
                            voided_tix = voided_tix + 1
                        updated_ticket = sf.Order_Item__c.update(ticket_id, {'Voided_Item__c' : Voided_Item__c, 'Local_Voided_Date_Item__c' : Local_Voided_Date_Item__c})

                    elif i['orderItemType'] == 'Delivery':
                        delivery_query_condition = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_AWS_ID_Item__c = '{i['id']}'")
                        if(list(delivery_query_condition.items())[2][1] == []):
                            delivery_query = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_Order_Number__c = '{Nliven_Order_Number__c}' AND Order_Item_Type__c = '{i['orderItemType']}'")
                            logger.info(delivery_query)
                            delivery_id = list(delivery_query.items())[2][1][0]['Id']
                        else:
                            delivery_id = list(delivery_query_condition.items())[2][1][0]['Id']
                        logger.info(delivery_id)
                        updated_delivery = sf.Order_Item__c.update(delivery_id, {'Price_Item__c': i['price'], 'Full_Price_Item__c' : i['fullPrice']})

                    else:
                        child_order_items = [child for child in i['childOrderItems'] if child['orderItemType'] == "Fee" and (child['feeName']== 'Web Service Fee' or child['feeName']== 'Service Charge' or child['feeName']== 'Facility Fee' or child['feeName']== 'League Fee' or child['feeName']== 'Access Fee')]

                        for j in range(len(child_order_items)):
                            cd = {k: v for k, v in child_order_items[j].items() if k != "childOrderItems"}
                            logger.info(cd)

                            fee_query_condition = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_AWS_ID_Item__c = '{cd['id']}'")
                            if(list(fee_query_condition.items())[2][1] == []):
                                fee_query = sf.query_all(f"SELECT Id FROM Order_Item__c WHERE Nliven_Order_Number__c = '{Nliven_Order_Number__c}' AND Order_Item_Type__c = '{cd['orderItemType']}' AND Fee_Name__c IN ('Web Service Fee', 'Service Charge', 'Facility Fee', 'League Fee', 'Access Fee')")
                                logger.info(fee_query)
                                fee_id = list(fee_query.items())[2][1][0]['Id']
                            else:
                                fee_id = list(fee_query_condition.items())[2][1][0]['Id']

                            logger.info(fee_id)
                            updated_fee = sf.Order_Item__c.update(fee_id, {'Price_Item__c': cd['price'], 'Full_Price_Item__c' : cd['fullPrice']})


            #Order Creation Webhook
            if webhook_type == 'OrderCreated':
            
                # if header_key == '717a33f288354446a37e59779ff13115':
                #     Source_TRG__c = 'Telecharge'
                #     Telecharge__c = True
                #     telecharge_order = 1
                #     Broadway_com__c = False
                #     Broadway_Inbound__c = False
                #     Ticketmaster__c = False
                #     Audience_Rewards__c = False
                #     TKTS__c = False
                #     TodayTix__c = False
                #     Telecharge_Nliven_ID__c = 0 if customer is None else customer['id']
                #     Telecharge_Nliven_Account__c = None if customer is None else customer['registered']
                    
                if header_key == 'a101885999e448c296da817e595e2853':
                    Nliven_ID__c =  0 if customer is None else customer['id']
                    telecharge_order = 0
                    Broadway_com__c = False
                    Broadway_Inbound__c = False
                    Ticketmaster__c = False
                    Audience_Rewards__c = False
                    TKTS__c = False
                    TodayTix__c = False
                    EBG_Solutions__c = False
                    Nliven__c = False
                    Group_Sales__c = False
                    Nliven_Account__c = None if customer is None else customer['registered']
                    Nliven_Account_Created_Date__c = data['localCreated'] if customer['registered'] else None


                    Group_Sales_Partner__c = ''
                    
                    if data['salesChannel'] == 'PointOfSale':
                        Source_TRG__c =  'Box Office'
                        Box_Office__c = True
                    elif data['salesChannel'] == 'GroupSales':
                        Source_TRG__c = 'Group Sales'
                        Group_Sales__c = True
                        Group_Sales_Partner__c = data.get('partnerName')
                    else:
                        if data['partnerName'] == 'Broadway.com':
                            Source_TRG__c = 'Broadway.com'
                            Broadway_com__c = True
                        elif data['partnerName'] == 'Broadway Inbound':
                            Source_TRG__c = 'Broadway Inbound'
                            Broadway_Inbound__c = True
                        elif data['partnerName'] == 'Ticketmaster':
                            Source_TRG__c = 'Ticketmaster'
                            Ticketmaster__c = True
                        elif data['partnerName'] == 'Audience Rewards':
                            Source_TRG__c = 'Audience Rewards'
                            Audience_Rewards__c = True
                        elif data['partnerName'] == 'TKTS':
                            Source_TRG__c = 'TKTS'
                            TKTS__c = True
                        elif data['partnerName'] == 'TodayTix':
                            Source_TRG__c = 'TodayTix'
                            TodayTix__c = True
                        elif data['partnerName'] == 'Telecharge':
                            Source_TRG__c = 'Telecharge'
                            Telecharge__c = True
                        elif data['partnerName'] == 'EBG Solutions':
                            Source_TRG__c = 'EBG Solutions'
                            EBG_Solutions__c = True
                        else:
                            Source_TRG__c = 'Nliven'
                            Nliven__c = True

                #Account Fields
                PersonEmail = '' if customer is None else customer['email']
                FirstName = '' if customer is None else customer['firstName'].title()
                LastName = 'Null' if customer is None or customer.get('lastName') in ('', None) else customer.get('lastName').title()
                LastNameUpdt =''
                FullName = FirstName + ' ' + LastName
                Day_Phone__c = '' if customer is None else customer['phone']
                PersonTitle = '' if customer is None else customer['title']
                audience_rewards = data.get('audienceRewards')
                Audience_Rewards_Account_Number__c = None if audience_rewards in ('', None) else audience_rewards


                if customer and 'customerTags' in customer:
                   customer_tag_exist = any(item['customerTag']['name'] == 'AR Opt-In' for item in customer['customerTags'])
                   if customer_tag_exist:
                     AR_Opt_In__c = True
                     AR_Opt_In_Date__c = datetime.today().strftime('%Y-%m-%d')

                PersonMailingStreet = data['billToAddress1']
                Mailing_Address_2__c = data['billToAddress2']
                Address_1__c = data['billToAddress1']
                Address_2__c = data['billToAddress2']
                PersonMailingCity = data['billToCity']

                # PersonMailingZipCode = data['billToPostalCode']
                Zip__c = data['billToPostalCode'][:5] if data['billToPostalCode'] else ''
                Zip_Code_Lookup__c = ''
                PersonMailingPostalCode = data['billToPostalCode']
                PersonMailingCountryCode = data['billToCountryCode'].upper() if data['billToCountryCode'] else ''
                Country_Code__c = data['billToCountryCode'].upper() if data['billToCountryCode'] else ''
                #Address_1__c = ''
                #Address_2__c = ''Zip__c = data['billToPostalCode'][:5]
                #PersonMailingStreet = ''

                if Country_Code__c == 'US':

                    Country__c = countries[Country_Code__c]
                    PersonMailingCountry = countries[Country_Code__c]                                       
                    
                    try:
                        StateAbbrev__c = search.by_zipcode(Zip__c).State
                        PersonMailingStateCode = search.by_zipcode(Zip__c).State
                        City__c = search.by_zipcode(Zip__c).City
                        PersonMailingCity = search.by_zipcode(Zip__c).City

                        print('Querying Zip_Code__c')
                        Zip_Code_Lookup_ResultSet = sf.query_all(f"SELECT Id FROM Zip_Code__c WHERE Name = '{Zip__c}'")
                        lookup_resultSet_items = list(Zip_Code_Lookup_ResultSet.items())
                        lookup_resultSet_items_dictionary = dict(lookup_resultSet_items)

                        if lookup_resultSet_items_dictionary['totalSize'] == 0:
                            Zip_Code_Lookup__c = ''
                        else:
                            records = lookup_resultSet_items_dictionary['records']
                            print(records)
                            lookup_item = dict(records[0])
                            Zip_Code_Lookup__c = lookup_item['Id']
                            print(Zip_Code_Lookup__c)
                    except:
                        StateAbbrev__c = ''
                        PersonMailingStateCode = ''
                        City__c = ''
                        PersonMailingCity = ''  
                        Zip_Code_Lookup__c = ''

                    try:
                        State__c = states[StateAbbrev__c]
                        PersonMailingState = states[StateAbbrev__c]
                    except:
                        State__c = ''
                        PersonMailingState = ''
                else:
                    try:
                        Country__c = countries[Country_Code__c]
                        PersonMailingCountry = countries[Country_Code__c]
                        StateAbbrev__c = ''
                        PersonMailingStateCode = ''
                        City__c = ''
                        PersonMailingCity = ''
                        State__c = ''
                        PersonMailingState = ''
                        if Country_Code__c and Country_Code__c != 'US':
                          Zip_Code_Lookup__c = 'a1mTV000000pdVZ'
                    except:
                        Country__c = ''
                        PersonMailingCountry = ''
                        StateAbbrev__c = ''
                        PersonMailingStateCode = ''
                        City__c = ''
                        PersonMailingCity = ''
                        State__c = ''
                        PersonMailingState = ''
                        if Country_Code__c and Country_Code__c != 'US':
                          Zip_Code_Lookup__c = 'a1mTV000000pdVZ'
                
                #try: 
                 #   if len(data['billToState']) > 2:
                  #      PersonMailingStateCode = None
                   # else:
                    #    PersonMailingStateCode = data['billToState']
                #except:
                 #   PersonMailingStateCode = None

                logger.info('Country, StateAbbrev, State')
                logger.info(PersonMailingCountry)
                logger.info(StateAbbrev__c)
                logger.info(PersonMailingState)
                logger.info(f"Zip_Code_Lookup__c value for the Customer : {Zip_Code_Lookup__c}")
                logger.info(f"Nliven_Account_Created_Date__c value: {Nliven_Account_Created_Date__c}")

                #Opportunity Fields
                Amount_with_Fees__c = data['total']
                Number_of_Tickets__c = data['ticketQty']
                DELIVERY_METHOD__c = data['deliveryMethodName']
                CloseDate = data['localCreated'][:10]
                Order_Date__c = data['localCreated'][:10]
                Payment_Submethod__c = data['paymentMethodName']
                Canceled__c = data['orderStatus']
                Nliven_Order_Number__c = data['id']
                Nliven_Event_ID__c = data['eventId']
                
                
                Event_Date_Mater__c = event['localDate'][:10]
                if data['primarySystemOrderID'] != None:
                    TM_Account__c = data['primarySystemOrderID'].split('/')[0]
                else:
                    TM_Account__c = None


                if Canceled__c == 'Cancelled':
                    Canceled__c = True
                else:
                    Canceled__c = False

                #Show__c needs to be an ID number from show object that we get later.
                Show__c = event['name']
                #Venue_Nliven = venue['name']
                Performance_Name__c = event['alternateName']
                Event_Code__c = event['externalEventId']

                if venue['name'] == 'Palace Theatre':
                    Venue_Nliven = 'Palace Theatre'
                    Market__c = 'New York'
                elif venue['name'] == 'Hollywood Pantages Theatre':
                    Venue_Nliven = 'Hollywood Pantages Theatre'
                    Market__c = 'Los Angeles'
                else:
                    Venue_Nliven = venue['name']
                    Market__c = 'New York'
                #logger.info(Venue_Nliven)
                # if Venue_Nliven == 'Palace Theatre'
                #     Venue_Nliven = 'Palace Theatre New York'

                #Workaround for unsystematic show name for lion king.
                if event['name'] == 'The Lion King (NY)':
                    Show_master__c = 'The Lion King (New York, NY)'
                elif event['name'] == 'Mel Brooks':
                    Show_master__c = 'Mel Brooks on Broadway'
                elif event['name'] == 'Aladdin (New York, NY)':
                    Show_master__c = 'Aladdin'
                elif event['name'] == 'Aladdin - The Musical':
                    Show_master__c = 'Aladdin'
                elif event['name'] == 'MJ':
                    Show_master__c = 'MJ (NY)'
                elif event['name'] == 'Wicked - Behind The Emerald Curtain':
                    Show_master__c = 'Wicked - Behind The Emerald Curtain (NY)'
                elif event['name'] == 'TINA: The Tina Turner Musical (NY)':
                    Show_master__c = 'TINA - The Tina Turner Musical (NY)'
                else:
                    Show_master__c = event['name'].replace("'","\\'")


                local_hour = int(event['localDate'].split('T')[1].split(':')[0])
                if local_hour < 12:
                    Time_of_Day_master__c = 'Morning'
                elif local_hour < 17:
                    Time_of_Day_master__c = 'Matinee'
                else:
                    Time_of_Day_master__c = 'Evening'

                # Event_date_with_time__c = '5/10/2018 11:22 AM'
                # Event_Date__c = '5/10/2018 11:22 AM'

                #Puts events 5 additional hours behind.
                #Event_date_with_time__c = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo = timezone.utc).astimezone(local_tz).strftime('%Y-%m-%dT%H:%M:%SZ')
                #This is not doing anything at this point....
                Event_date_with_time__c = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
                Event_Date__c = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo = timezone.utc).astimezone(local_tz).strftime('%m/%d/%Y %I:%M %p')
                Event_time__c = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo = timezone.utc).astimezone(local_tz).strftime('%-I:%M %p')
                
                #Temporary - Needs to be replaced once correct format is discovered
                #Event_date_with_time__c = '2018-01-01T01:01:01Z' 

                logger.info(Audience_Rewards_Account_Number__c)
                logger.info(Event_date_with_time__c)

                #record_list = ['Address_1__c', 'PersonMailingCity', 'PersonMailingStateCode', 'State__c', 'PersonMailingZipCode', 'Zip__c', 'PersonMailingCountryCode', 'Country']

                Primary_Key = PersonEmail.upper()
                logger.info(Primary_Key)

                #Begin process of inserting/updating Account
                #Determine if this an insert or an update
                #possible_query = sf.query_all(f"SELECT Id, FirstName, LastName, PersonEmail, Last_Order_Date__c, Total_Tickets_Purchased__c, LastModifiedDate FROM Account WHERE PersonEmail = '{PersonEmail}'")
                possible_query = sf.query_all(f"SELECT Id, FirstName, LastName, PersonEmail, Last_Order_Date__c, Total_Tickets_Purchased__c, LastModifiedDate, PersonHasOptedOutOfEmail, AR_Opt_In__c, AR_Opt_In_Date__c,Broadway_com__c, Broadway_Inbound__c, Ticketmaster__c, Audience_Rewards__c, TKTS__c, TodayTix__c, EBG_Solutions__c, Nliven__c, Audience_Rewards_Account_Number__c, Nliven_Account_Created_Date__c, Group_Sales__c FROM Account WHERE PersonEmail = '{PersonEmail}'")
                
                # create new list of countries here
                countriesList_OptOutOfEmail = ['Austria', 'Belgium', 'Bulgaria', 'Canada', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark',  'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Other', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']
                PersonHasOptedOutOfEmail = False
                AR_Opt_In__c = False
                AR_Opt_In_Date__c = None
                
                possible_items = list(possible_query.items())

                logger.info(possible_items)

                #If totalSize = 0, then we can insert the record.  Otherwise, we need to find the right account id to update.
                if possible_items[0][1] > 0:
                    logger.info('Emails Matched. Selecting Account...')
                    possible_accounts = list(possible_items[2][1:][0])

                    #Find relevant values for comparison
                    last_order_dates = []
                    total_tickets_purchased = []
                    last_modified = []

                    for i in possible_accounts:
                        last_order_dates.append(i['Last_Order_Date__c'])
                        total_tickets_purchased.append(i['Total_Tickets_Purchased__c'])
                        last_modified.append(i['LastModifiedDate'])
                        PersonHasOptedOutOfEmail = i['PersonHasOptedOutOfEmail']
                        AR_Opt_In__c = i['AR_Opt_In__c']
                        AR_Opt_In_Date__c = i['AR_Opt_In_Date__c']
                        Broadway_com__c = Broadway_com__c if Broadway_com__c else i['Broadway_com__c']
                        Broadway_Inbound__c = Broadway_Inbound__c if Broadway_Inbound__c else i['Broadway_Inbound__c']
                        Ticketmaster__c = Ticketmaster__c if Ticketmaster__c else i['Ticketmaster__c']
                        Audience_Rewards__c = Audience_Rewards__c if Audience_Rewards__c else i['Audience_Rewards__c']
                        TKTS__c = TKTS__c if TKTS__c else i['TKTS__c']
                        TodayTix__c = TodayTix__c if TodayTix__c else i['TodayTix__c']
                        EBG_Solutions__c = EBG_Solutions__c if EBG_Solutions__c else i['EBG_Solutions__c']
                        Group_Sales__c = Group_Sales__c if Group_Sales__c else i['Group_Sales__c']
                        Audience_Rewards_Account_Number__c = Audience_Rewards_Account_Number__c or i['Audience_Rewards_Account_Number__c']
                        Nliven_Account_Created_Date__c= i['Nliven_Account_Created_Date__c'] or Nliven_Account_Created_Date__c
                        LastNameUpdt= i['LastName'] if LastName=='Null' else LastName
                        #Nliven__c = i['Nliven__c']

                    ##Temporarily subs in old date if no orders are associated with the sf account being examined.
                    last_order_dates = ['1999-99-99' if v is None else v for v in last_order_dates]

                    #Get the index of the winner and update.
                    last_order_winners = [i for i, x in enumerate(last_order_dates) if x == max(last_order_dates)]    #Returns a list with the index of the max value(s)

                    #If only one max is found, store that index
                    if len(last_order_winners) == 1:
                        winner_index = last_order_winners[0]
                    #Otherwise, do the same for total tickets purchased
                    else:
                        tickets_winners = [i for i, x in enumerate(total_tickets_purchased) if x == max(total_tickets_purchased)]
                        if len(tickets_winners) == 1:
                            winner_index = tickets_winners[0]
                        #If tied on both, pick which was last modified.  If somehow these two values are tied, it will choose whichever is first in the list (alphabetical by id?)
                        else:
                            last_modified_winners = [i for i, x in enumerate(last_modified) if x == max(last_modified)]
                            winner_index = last_modified_winners[0]
                    
                    #This is the account that will be updated.
                    account_to_be_updated = possible_accounts[winner_index]

                    salesforce_id = {}
                    salesforce_id.update({account_to_be_updated['PersonEmail'].upper() : account_to_be_updated['Id']})

                    logger.info(salesforce_id)
                    account_number = salesforce_id[Primary_Key]
                    logger.info(account_number)

                    #Get AR number. Only update if blank.

                    #Returns an ordered dictionary with account info that we will need to check for blank info.  Might not need this if all fields are required.
                    account = sf.Account.get(account_number)
                    logger.info(account)

                    PersonHasOptedOutOfEmail_Update = True if PersonMailingCountry in countriesList_OptOutOfEmail else PersonHasOptedOutOfEmail

                    if customer and 'customerTags' in customer:
                      customer_tag_exist = any(item['customerTag']['name'] == 'AR Opt-In' for item in customer['customerTags'])
                      logger.info('AR Opt-In customer tag exist:')
                      logger.info(customer_tag_exist)
                      if customer_tag_exist:
                        AR_Opt_In__c = True
                        AR_Opt_In_Date__c = datetime.today().strftime('%Y-%m-%d')

                    try:
                         logger.info('Audience Rewards Account Number:')
                         logger.info(Audience_Rewards_Account_Number__c)
                         #Need to confirm address data being recorded properly.
                         if Audience_Rewards_Account_Number__c is not None and Audience_Rewards_Account_Number__c != "":
                            logger.info('Audience Rewards Account Number and Telecharge order in true condition')
                            logger.info(Audience_Rewards_Account_Number__c)
                            logger.info(telecharge_order)
                            logger.info('Updated Account Last Name %s', LastNameUpdt)
                            if telecharge_order == 0 and not Group_Sales__c:
                                updated_account = sf.Account.update(account_number, {'PersonEmail' : PersonEmail, 'FirstName' : FirstName, 'LastName' : LastNameUpdt, 'PersonTitle' : PersonTitle, 
                                                                                'Zip__c' : Zip__c, 'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 'City__c' : City__c, 'PersonMailingCity' : PersonMailingCity, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c, 'Mailing_Address_2__c' : Mailing_Address_2__c, 'PersonMailingStreet' : PersonMailingStreet,
                                                                                'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 'PersonMailingCountry' : PersonMailingCountry, 'PersonMailingCountryCode' : PersonMailingCountryCode, 'PersonMailingStateCode' : PersonMailingStateCode, 'PersonMailingState' : PersonMailingState,
                                                                                'Batch_file_date__c' : batch_date, 'Nliven__c' : Nliven__c, 'Nliven_ID__c' : Nliven_ID__c, 'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c, 'PersonMailingPostalCode' : PersonMailingPostalCode, 'Zip_Code_Lookup__c' : Zip_Code_Lookup__c, 
                                                                                'Nliven_Account__c' : Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Update, 'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c, 
                                                                                'Broadway_com__c' : Broadway_com__c, 'Broadway_Inbound__c' : Broadway_Inbound__c, 'EBG_Solutions__c' : EBG_Solutions__c, 'Ticketmaster__c' : Ticketmaster__c, 'Audience_Rewards__c' : Audience_Rewards__c, 'TKTS__c' : TKTS__c, 'TodayTix__c' : TodayTix__c, 'Nliven_Account_Created_Date__c' : Nliven_Account_Created_Date__c})
                                logger.info('Updated account %s and Telecharge order %d', updated_account, telecharge_order)
                            elif telecharge_order == 0 and Group_Sales__c:
                                updated_account = sf.Account.update(account_number, {'PersonEmail' : PersonEmail, 'PersonTitle' : PersonTitle, 
                                                                                    'Zip__c' : Zip__c, 'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 
                                                                                    'City__c' : City__c, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c,
                                                                                    'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 
                                                                                    'Batch_file_date__c' : batch_date, 'Nliven__c' : Nliven__c, 'Nliven_ID__c' : Nliven_ID__c, 
                                                                                    'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c,
                                                                                    'Nliven_Account__c' : Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Update, 
                                                                                    'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c, 
                                                                                    'Broadway_com__c' : Broadway_com__c, 'Broadway_Inbound__c' : Broadway_Inbound__c,  'Group_Sales__c' : Group_Sales__c,
                                                                                    'Ticketmaster__c' : Ticketmaster__c, 'Audience_Rewards__c' : Audience_Rewards__c, 'TKTS__c' : TKTS__c, 'EBG_Solutions__c' : EBG_Solutions__c,
                                                                                    'TodayTix__c' : TodayTix__c, 'Nliven_Account_Created_Date__c' : Nliven_Account_Created_Date__c})
                                logger.info('Group_Sales__c %s and Updated account %s and Telecharge order %d', Group_Sales__c, updated_account, telecharge_order)
                         else:
                            logger.info('Audience Rewards Account Number and Telecharge order in false condition')
                            logger.info(Audience_Rewards_Account_Number__c)
                            logger.info(telecharge_order)
                            logger.info('Updated Account Last Name %s', LastNameUpdt)
                            if telecharge_order == 0 and not Group_Sales__c:
                                updated_account = sf.Account.update(account_number, {'PersonEmail' : PersonEmail, 'FirstName' : FirstName, 'LastName' : LastNameUpdt, 'PersonTitle' : PersonTitle, 
                                                                                'Zip__c' : Zip__c, 'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 'City__c' : City__c, 'PersonMailingCity' : PersonMailingCity, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c, 'Mailing_Address_2__c' : Mailing_Address_2__c, 'PersonMailingStreet' : PersonMailingStreet,
                                                                                'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 'PersonMailingCountry' : PersonMailingCountry, 'PersonMailingCountryCode' : PersonMailingCountryCode, 'PersonMailingStateCode' : PersonMailingStateCode, 'PersonMailingState' : PersonMailingState,
                                                                                'Batch_file_date__c' : batch_date, 'Nliven__c' : Nliven__c, 'Nliven_ID__c' : Nliven_ID__c, 'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c, 'PersonMailingPostalCode' : PersonMailingPostalCode, 'Zip_Code_Lookup__c' : Zip_Code_Lookup__c, 
                                                                                'Nliven_Account__c' : Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Update, 'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c,
                                                                                'Broadway_com__c' : Broadway_com__c, 'Broadway_Inbound__c' : Broadway_Inbound__c,'EBG_Solutions__c' : EBG_Solutions__c, 'Ticketmaster__c' : Ticketmaster__c, 'Audience_Rewards__c' : Audience_Rewards__c, 'TKTS__c' : TKTS__c, 'TodayTix__c' : TodayTix__c, 'Nliven_Account_Created_Date__c' : Nliven_Account_Created_Date__c})
                                logger.info('Updated account %s and Telecharge order %d', updated_account, telecharge_order)
                            elif telecharge_order == 0 and Group_Sales__c:
                                updated_account = sf.Account.update(account_number, {'PersonEmail' : PersonEmail, 'PersonTitle' : PersonTitle, 
                                                                                    'Zip__c' : Zip__c, 'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 
                                                                                    'City__c' : City__c, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c,
                                                                                    'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 
                                                                                    'Batch_file_date__c' : batch_date, 'Nliven__c' : Nliven__c, 'Nliven_ID__c' : Nliven_ID__c, 
                                                                                    'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c,
                                                                                    'Nliven_Account__c' : Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Update, 
                                                                                    'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c,  'Group_Sales__c' : Group_Sales__c,
                                                                                    'Broadway_com__c' : Broadway_com__c, 'Broadway_Inbound__c' : Broadway_Inbound__c, 'EBG_Solutions__c' : EBG_Solutions__c, 
                                                                                    'Ticketmaster__c' : Ticketmaster__c, 'Audience_Rewards__c' : Audience_Rewards__c, 'TKTS__c' : TKTS__c, 
                                                                                    'TodayTix__c' : TodayTix__c, 'Nliven_Account_Created_Date__c' : Nliven_Account_Created_Date__c})
                                logger.info('Group_Sales__c %s and Updated account %s and Telecharge order %d', Group_Sales__c, updated_account, telecharge_order)
                         #Check if AR number exists.  If not, update.
                         for k, v in list(account.items()):
                            if k == 'Audience_Rewards_Account_Number__c' and (Audience_Rewards_Account_Number__c is not None and Audience_Rewards_Account_Number__c != ""):
                                AR_number = v
                                if AR_number == None:
                                    sf.Account.update(account_number, {'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c})
                        #This has the opt-ins always being turned on.
                        # updated_account = sf.Account.update(account_number, {'PersonEmail' : PersonEmail, 'FirstName' : FirstName, 'LastName' : LastName, 'Day_Phone__c' : Day_Phone__c, 'PersonTitle' : PersonTitle, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c,
                        # 'PersonMailingCity' : PersonMailingCity, 'State__c' : State__c, 'Zip__c' : Zip__c, 'Country__c' : Country__c,
                        # 'Batch_file_date__c' : batch_date, 'Subscription_Broadway_Direct_Newsletter__c' : True, 'Subscription_Ticket_Offers__c' : True})
                                logger.info('Updated Account.')
                    except:
                        logger.exception("Error updating account.")

                    if updated_account != 204:      #204 is the status code if an update is successful
                        logger.error(f"Error updating account.  {updated_account['errors']}")

                else:
                    logger.info('Creating Account...')
                    logger.info('AR Opt-In info in the creating account...')
                    logger.info(AR_Opt_In__c)
                    logger.info(AR_Opt_In_Date__c)

                    if customer and 'customerTags' in customer:
                      customer_tag_exist = any(item['customerTag']['name'] == 'AR Opt-In' for item in customer['customerTags'])
                      logger.info('AR Opt-In customer tag exist in Create Account:')
                      logger.info(customer_tag_exist)
                      if customer_tag_exist:
                        AR_Opt_In__c = True
                        AR_Opt_In_Date__c = datetime.today().strftime('%Y-%m-%d')

                    logger.info(AR_Opt_In__c)
                    logger.info(AR_Opt_In_Date__c)

                    PersonHasOptedOutOfEmail_Insert = True if PersonMailingCountry in countriesList_OptOutOfEmail else False
                    created_account = None
                    try:
                        if telecharge_order == 0:
                            logger.info(LastName)
                            created_account = sf.Account.create({'PersonEmail' : PersonEmail, 'FirstName' : FirstName, 'LastName' : LastName, 'Day_Phone__c' : Day_Phone__c, 'PersonTitle' : PersonTitle,
                            'Zip__c' : Zip__c, 'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 'PersonMailingCountry' : PersonMailingCountry, 'PersonMailingCountryCode' : PersonMailingCountryCode, 'PersonMailingStateCode' : PersonMailingStateCode, 'PersonMailingState' : PersonMailingState,
                            'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 'City__c' : City__c, 'PersonMailingCity' : PersonMailingCity, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c, 'Mailing_Address_2__c' : Mailing_Address_2__c,'PersonMailingStreet' : PersonMailingStreet, 'PersonMailingPostalCode' : PersonMailingPostalCode,
                            'Zip_Code_Lookup__c' : Zip_Code_Lookup__c, 'Batch_file_date__c' : batch_date, 'Subscription_Broadway_Direct_Newsletter__c' : False, 'Subscription_Ticket_Offers__c' : False, 
                            'Nliven__c' : Nliven__c, 'Nliven_ID__c' : Nliven_ID__c, 'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c, 'Nliven_Account__c' : Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Insert, 'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c, 'Group_Sales__c' : Group_Sales__c,
                            'Broadway_com__c' : Broadway_com__c, 'Broadway_Inbound__c' : Broadway_Inbound__c, 'EBG_Solutions__c' : EBG_Solutions__c, 'Ticketmaster__c' : Ticketmaster__c, 'Audience_Rewards__c' : Audience_Rewards__c, 'TKTS__c' : TKTS__c, 'TodayTix__c' : TodayTix__c, 'Nliven_Account_Created_Date__c' : Nliven_Account_Created_Date__c})
                            logger.info('Created Account (Nliven).')
                            logger.info(created_account)
                            logger.info(json.dumps(created_account))
                        # elif telecharge_order == 1 and 'Aladdin' not in Show_master__c:
                            # created_account = sf.Account.create({'PersonEmail' : PersonEmail, 'FirstName' : FirstName, 'LastName' : LastName, 'Day_Phone__c' : Day_Phone__c, 'PersonTitle' : PersonTitle,
                            # 'Zip__c' : Zip__c, 'Country__c' : Country__c, 'Country_Code__c' : Country_Code__c, 'PersonMailingCountry' : PersonMailingCountry, 'PersonMailingCountryCode' : PersonMailingCountryCode, 'PersonMailingStateCode' : PersonMailingStateCode, 'PersonMailingState' : PersonMailingState,
                            # 'State__c' : State__c, 'StateAbbrev__c' : StateAbbrev__c, 'City__c' : City__c, 'PersonMailingCity' : PersonMailingCity, 'Address_1__c' : Address_1__c, 'Address_2__c' : Address_2__c, 'Mailing_Address_2__c' : Mailing_Address_2__c,'PersonMailingStreet' : PersonMailingStreet, 'PersonMailingPostalCode' : PersonMailingPostalCode,
                            # 'Zip_Code_Lookup__c' : Zip_Code_Lookup__c, 'Batch_file_date__c' : batch_date, 'Subscription_Broadway_Direct_Newsletter__c' : False, 'Subscription_Ticket_Offers__c' : False, 
                            # 'Telecharge__c' : Telecharge__c, 'Telecharge_Nliven_ID__c' : Telecharge_Nliven_ID__c, 'Audience_Rewards_Account_Number__c' : Audience_Rewards_Account_Number__c, 'Telecharge_Nliven_Account__c' : Telecharge_Nliven_Account__c, 'PersonHasOptedOutOfEmail' : PersonHasOptedOutOfEmail_Insert, 'AR_Opt_In__c' : AR_Opt_In__c, 'AR_Opt_In_Date__c' : AR_Opt_In_Date__c})
                            # logger.info('Created Account (Telecharge).')
                            # logger.info(created_account)
                    except:
                        logger.exception("Error creating account in Step 1.")

                    if created_account is not None and created_account['success'] != True:
                        logger.info(created_account)
                        logger.error(f"Error creating account in Step 2.  Success != True.  {created_account['errors']}")
                    elif 'id' in created_account and created_account['id'] is not None:
                        account_number = created_account['id']


                #Find correct Venue ID
                venue_query = sf.query_all(f"SELECT Id, Name FROM Venue__c WHERE Name = '{Venue_Nliven}' ORDER BY LastModifiedDate desc LIMIT 1")
                venue_id_sf = venue_query['records'][0]['Id']
                logger.info(venue_id_sf)


                #Prep for inserting Opportunity
                show_query = sf.query_all(f"SELECT Id, Name, Show_Venue__c FROM Show__c WHERE Name = '{Show_master__c}' AND Market__c = '{Market__c}' AND Show_Venue__c = '{venue_id_sf}'")
                logger.info(show_query)
                show_id = show_query['records'][0]['Id']
                venue_id = show_query['records'][0]['Show_Venue__c']
                venue = sf.Venue__c.get(venue_id)
                venue_name = venue['Name']
                will_call_first_name = data['firstName'].title()
                will_call_last_name = data['lastName'].title()
                will_call_name = will_call_first_name + ' ' + will_call_last_name
                OrderName = venue_name + ' ' + will_call_name
                logger.info(venue_name)


                #This block of code will find the summed price of the tickets.  This will keep the 'Amount' field at the Opportunity level consistent with TM.
                Amount = 0

                for i in range(len(order_items)):
                    d = {k: v for k, v in order_items[i].items() if k != "childOrderItems"}
                    if d['orderItemType'] == 'Ticket':
                        Amount += d['price']

                logger.info(Amount)

                #Temporary SF solution to add qualifiers to opportunity objects
                Qualifiers__c = ''

                for i in order_items:
                    if(i['orderItemType'] == 'Ticket'):
                        Qualifiers__c = i['promoCode']
                        break


                #Removed Event Date (deleted in SF 5/2/19)
                #Tickets need to be inserted whether account exists or not.
                #Need to have accountId, closedate, amount, stagename, Name, Event_date__c, and Show_master__c as required fields right now.
                #Show__c is the show object id.  
                opportunity_items = sf.query_all(f"SELECT Id FROM Opportunity WHERE Nliven_Order_Number__c ='{Nliven_Order_Number__c}'")
                logger.info("existing opportunities.")
                logger.info(opportunity_items)
                logger.info(f"promoCode: {Qualifiers__c}")
                if len(opportunity_items['records']) == 0:

                    if telecharge_order == 0 or 'Aladdin' not in Show_master__c:
                        try:
                          if Qualifiers__c != 'JLOTTO' or Qualifiers__c != 'LOTTO': 
                            created_opportunity = sf.Opportunity.create({'AccountId' : account_number, 'CloseDate' : CloseDate, 'Amount' : Amount, 'Amount_with_Fees__c' : Amount_with_Fees__c, 'StageName' : 'Closed Won', 
                                'First_Name__c' : will_call_first_name, 'Last_Name__c' : will_call_last_name, 'Name' : OrderName, 'Show_master__c' : Show_master__c, 'Event_Date_Mater__c' : Event_Date_Mater__c, 'TM_Account__c' : TM_Account__c,
                                'Show__c' : show_id, 'Number_of_Tickets__c' : Number_of_Tickets__c, 'DELIVERY_METHOD__c' : DELIVERY_METHOD__c, 'Order_Date__c' : Order_Date__c, 'Payment_Submethod__c' : Payment_Submethod__c, 'Canceled__c' : Canceled__c,
                                'Performance_Name__c' : Performance_Name__c, 'Event_Code__c' : Event_Code__c, 'Nliven_Order_Number__c' : Nliven_Order_Number__c, 'Source_TRG__c' : Source_TRG__c, 'Market__c' : Market__c, 'Event_time__c' : Event_time__c, 'Group_Sales_Partner__c' : Group_Sales_Partner__c,
                                'Venue__c' : venue_id, 'Venue_Name__c' : venue_name, 'Event_date_with_time__c' : event['date'], 'Batch_file_date__c' : batch_date, 'Time_of_Day_master__c' : Time_of_Day_master__c, 'Qualifiers__c' : Qualifiers__c, 'Nliven_Event_ID__c' : Nliven_Event_ID__c})
                            logger.info('Opportunity Created')
                        except:
                            logger.exception('Error creating Opportunity.')
                            print('Error Creating Opp')

                    #Create Order Items.
                    try:
                        logger.info('Creating Order Items.')

                        all_fees = []
                        fees = []
                        tix = []
            
                        for i in range(len(order_items)):
                          if order_items[i]['promoCode'] != 'JLOTTO' or order_items[i]['promoCode'] != 'LOTTO':
                            d = {k: v for k, v in order_items[i].items()} #if k != "childOrderItems"}
                            d['Name'] = venue_name + ' ' + d['orderItemType'] + ' ' + will_call_last_name
                            d['NlivenOrderNumber'] = Nliven_Order_Number__c
                            tix.append(d)
                            logger.info(d)
                            logger.info(f"order_items: {d}")
                            logger.info(f"Promo_Code_Item: {d['promoCode']}")
                            if d['orderItemType'] == 'Delivery':
                                d['deliveryMethod'] = DELIVERY_METHOD__c
                            else:
                                d['deliveryMethod'] = ''
                            sf.Order_Item__c.create({'Ticket__c' : created_opportunity['id'], 'Nliven_AWS_ID_Item__c': d['id'], 'Name' : d['Name'], 'Order_Item_Type__c' : d['orderItemType'], 'Fee_Name__c' : d['feeName'], 'Delivery_Method_Item__c' : d['deliveryMethod'],
                                'Section_Item__c' : d['section'], 'Row_Item__c' : d['row'], 'SeatID_Item__c' : d['seatId'], 'Price_Item__c' : d['price'], 'Full_Price_Item__c' : d['fullPrice'],
                                'ADA_Type_Item__c' : d['adaType'], 'Retail_Price_Item__c' : d['retailPrice'], 'Price_Level_Name_Item__c' : d['priceLevelName'], 'Price_Table_Name_Item__c' : d['priceTableName'],
                                'Ticket_Type_Item__c' : d['priceTypeName'], 'Product_Name_Item__c' : d['productName'], 'Group_Code_Item__c' : d['groupCode'], 'Promo_Code_Item__c' : d['promoCode'], 'Voided_Item__c' : d['voided'], 'Nliven_Order_Number__c' : d['NlivenOrderNumber'], 'Nliven_Event_ID_Item__c' : data['eventId']})


                            ctix = []

                            logger.info('Child Order Item:')
                            logger.info(d['childOrderItems'])
                            child_order_items = [child for child in d['childOrderItems'] if child['orderItemType'] == "Fee" and (child['feeName']== 'Web Service Fee' or child['feeName']== 'Service Charge' or child['feeName']== 'Facility Fee' or child['feeName']== 'League Fee' or child['feeName']== 'Access Fee')]

                            for j in range(len(child_order_items)):
                                cd = {k: v for k, v in child_order_items[j].items()} #if k != "childOrderItems"}
                                cd['Name'] = venue_name + ' ' + d['orderItemType'] + ' ' + will_call_last_name
                                cd['NlivenOrderNumber'] = Nliven_Order_Number__c
                                ctix.append(cd)
                                logger.info(cd)
                                cd['deliveryMethod'] = ''
                                logger.info('Fee Name:')
                                logger.info(cd['feeName'])
                                sf.Order_Item__c.create({'Ticket__c' : created_opportunity['id'], 'Nliven_AWS_ID_Item__c': cd['id'], 'Name' : cd['Name'], 'Order_Item_Type__c' : cd['orderItemType'], 'Fee_Name__c' : cd['feeName'], 'Delivery_Method_Item__c' : cd['deliveryMethod'],
                                    'Section_Item__c' : cd['section'], 'Row_Item__c' : cd['row'], 'SeatID_Item__c' : cd['seatId'], 'Price_Item__c' : cd['price'], 'Full_Price_Item__c' : cd['fullPrice'],
                                    'ADA_Type_Item__c' : cd['adaType'], 'Retail_Price_Item__c' : cd['retailPrice'], 'Price_Level_Name_Item__c' : cd['priceLevelName'], 'Price_Table_Name_Item__c' : cd['priceTableName'],
                                    'Ticket_Type_Item__c' : cd['priceTypeName'], 'Product_Name_Item__c' : d['productName'], 'Group_Code_Item__c' : cd['groupCode'], 'Promo_Code_Item__c' : cd['promoCode'], 'Voided_Item__c' : cd['voided'], 'Nliven_Order_Number__c' : cd['NlivenOrderNumber'], 'Nliven_Event_ID_Item__c' : data['eventId']})
                                
                            logger.info(ctix)
                            logger.info(f"child_order_items: {ctix}")
                            logger.info('Created Child Order Items.') 


                        logger.info(tix)
                        logger.info('Created Order Items.')
                    except:
                        logger.exception('Error creating Order Items.')
                        print('Error Creating Order Items.')


        return respond(None)
    elif os.environ['ShubertKey'] == header_key:
        logger.info('SUCCESS: Deprecated Shubert key detected, ignoring webhook.')
        return respond(None)
    else:
        logger.error('ERROR: Authorization Failure.  Check Secret Key.')
