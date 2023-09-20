import asyncio
import json
import random
import hashlib
import uuid
import copy
import redis
import os

from flight.additions.additions import Helper, AdditionsTicket

HOST = os.environ.get('CACHE_HOST')
PORT = os.environ.get('CACHE_PORT')

redis_client = redis.Redis(host=HOST, port=PORT)

async def search_converter(offers, guid, name, currency, route_count, request_id):
    if currency['curFrom'] == currency['curTo']:
        val = 1
    else:
        val = await Helper.currency_converter(currency['curFrom'], currency['curTo'])
    full_offers = []
    if route_count == True:
        dataList = offers['Body']['AppData']['Shop:Mixvel_AirShoppingRS']['Response']['DataLists']
        offersGroup = offers['Body']['AppData']['Shop:Mixvel_AirShoppingRS']['Response']['OffersGroup']
        srch = json.loads(redis_client.get(f"{request_id}_search"))
        availableOffers = await sort_offers(offersGroup['CarrierOffers']['Offer'])
        # print(len(availableOffers))
        for offerSorted in availableOffers:
            offer = offerSorted['offer']
            offerItemList = []
            client_id = str(uuid.uuid4())
            offerTmp = {
                "offer_id": client_id,
                "price_info": {
                    "price": round(float(offer['TotalPrice']['TotalAmount']['#text'])*val, 2),
                    "fee_amount": 0,
                    "commission_amount": 0
                },
                "upsell": True,
                "booking": True,
                "price_details": [],
                "baggages_info": [],
                "fares_info": [],
                "routes": [],
                "provider": {
                    "provider_id": guid,
                    "name": name
                }
            }

            offerItem = offer['OfferItem'] if await check_type(offer['OfferItem']) == 'list' else []

            if offerItem == []:
                offerItem.append(offer['OfferItem'])

            for ofItm in offerItem:
                if await check_type(ofItm['FareDetail']['PaxRefID']) == 'string':
                    offerItemList.append({
                        'offerItemId': ofItm['OfferItemID'],
                        'paxRefId': ofItm['FareDetail']['PaxRefID']
                    })
                else:
                    for paxRefId in ofItm['FareDetail']['PaxRefID']:
                        offerItemList.append({
                            'offerItemId': ofItm['OfferItemID'],
                            'paxRefId': paxRefId
                        })

            for item in offerItem:
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'ADT' in narsa:
                        price_tmp = {
                            "passenger_type": "ADT",
                            "currency": currency['curTo'],
                            "quantity": srch['adt'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['adt'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['adt'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['adt'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'ADT' in narsa:
                        price_tmp = {
                            "passenger_type": "ADT",
                            "currency": currency['curTo'],
                            "quantity": srch['adt'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['adt'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['adt'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['adt'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'CNN' in narsa:
                        price_tmp = {
                            "passenger_type": "CHD",
                            "currency": currency['curTo'],
                            "quantity": srch['chd'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['chd'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['chd'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['chd'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'CNN' in narsa:
                        price_tmp = {
                            "passenger_type": "CHD",
                            "currency": currency['curTo'],
                            "quantity": srch['chd'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['chd'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['chd'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['chd'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
            
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'INF' in narsa:
                        price_tmp = {
                            "passenger_type": "INF",
                            "currency": currency['curTo'],
                            "quantity": srch['inf'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['inf'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['inf'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['inf'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'INF' in narsa:
                        price_tmp = {
                            "passenger_type": "INF",
                            "currency": currency['curTo'],
                            "quantity": srch['inf'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['inf'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['inf'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['inf'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'INS' in narsa:
                        price_tmp = {
                            "passenger_type": "INS",
                            "currency": currency['curTo'],
                            "quantity": srch['ins'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['ins'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['ins'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['ins'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'INS' in narsa:
                        price_tmp = {
                            "passenger_type": "INS",
                            "currency": currency['curTo'],
                            "quantity": srch['ins'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['ins'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['ins'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['ins'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
            
            offerTmp['baggages_info'] = await asyncio.create_task(get_baggages_info(offer['BaggageAllowance'], dataList))
            offerTmp['fares_info'] = await asyncio.create_task(get_fares_info(offerItem, dataList))
            
            routeTmp = {
                "route_index": 0,
                "direction"  : "",
                "stops"      : "",
                "segments"   : []
            }

            fareComponent = offerItem[0]['FareDetail']['FareComponent'] if await check_type(offerItem[0]['FareDetail']['FareComponent']) == 'list' else []

            if fareComponent == []:
                fareComponent.append(offerItem[0]['FareDetail']['FareComponent'])

            fareCode = fareComponent[0]['FareBasisCode']
            bookingClass = fareComponent[0]['RBD']['RBD_Code']
            segmentClass = fareComponent[0]['CabinType']['CabinTypeCode']
            holdBaggage = None
            carryOn = None
            baggages = offer['BaggageAllowance'] if await check_type(offer['BaggageAllowance']) == 'list' else [offer['BaggageAllowance']]
            bagList = dataList['BaggageAllowanceList']['BaggageAllowance'] if await check_type(dataList['BaggageAllowanceList']['BaggageAllowance']) == 'list' else [dataList['BaggageAllowanceList']['BaggageAllowance']]
            for bag in baggages:
                for bagId in bagList:
                    if bag['BaggageAllowanceRefID'] == bagId['BaggageAllowanceID']:
                        if bagId['TypeCode'] == 'CarryOn':
                            carryOn = f"{bagId['WeightAllowance']['MaximumWeightMeasure']['#text']} {bagId['WeightAllowance']['MaximumWeightMeasure']['UnitCode']}"
                        else:
                            holdBaggage = f"{bagId['PieceAllowance']['TotalQty']} PC"
            journeyId = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']
            next = False
            for ids in offerItem:
                if journeyId != ids['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']:
                    next = True
                    break
            if next:
                continue
            seg_ind = 0
            segList = dataList['PaxJourneyList']['PaxJourney'] if await check_type(dataList['PaxJourneyList']['PaxJourney']) == 'list' else [dataList['PaxJourneyList']['PaxJourney']]
            for seg in segList:
                if journeyId == seg['PaxJourneyID']:
                    segments = []
                    if await check_type(seg['PaxSegmentRefID']) == 'string':
                        segments.append(seg['PaxSegmentRefID'])
                    elif await check_type(seg['PaxSegmentRefID']) == 'list':
                        segments = seg['PaxSegmentRefID']
                    for segment in segments:
                        paxSegments = dataList['PaxSegmentList']['PaxSegment'] if await check_type(dataList['PaxSegmentList']['PaxSegment']) == 'list' else [dataList['PaxSegmentList']['PaxSegment']]
                        for paxSeg in paxSegments:
                            if paxSeg['PaxSegmentID'] == segment:
                                mySeg = await make_segment(paxSeg, fareCode, segmentClass, bookingClass, holdBaggage, carryOn)
                                mySeg['segment_index'] = seg_ind
                                seg_ind += 1
                                routeTmp['segments'].append(mySeg)
            routeTmp['stops'] = len(routeTmp['segments']) - 1
            routeTmp['direction'] = f"{routeTmp['segments'][0]['departure_airport']}-{routeTmp['segments'][-1]['arrival_airport']}"
            offerTmp['routes'].append(routeTmp)
            # fullOffer = AdditionsTicket(
            #     ticket=offerTmp,
            #     buy_id=client_id,
            #     other={
            #         'offerId': offer['OfferID'],
            #         'fareFamilies': offerSorted['fare_families'],
            #         'dataList': dataList,
            #         'offerItemList': offerItemList,
            #         'price': offer['TotalPrice']['TotalAmount']['#text'],
            #         'currency': offer['TotalPrice']['TotalAmount']['CurCode']
            #     },
            #     gds_id=0,
            #     sp_name=name
            # )
            full_offers.append(offerTmp)
    else:
        dataList = offers['Body']['AppData']['Shop:Mixvel_AirShoppingRS']['Response']['DataLists']
        offersGroup = offers['Body']['AppData']['Shop:Mixvel_AirShoppingRS']['Response']['OffersGroup']
        srch = json.loads(redis_client.get(f"{request_id}_search"))
        availableOffers = await sort_offers(offersGroup['CarrierOffers']['Offer'])
        # print(len(availableOffers))
        for offerSorted in availableOffers:
            offer = offerSorted['offer'] 
            offerItemList = []           
            client_id = str(uuid.uuid4())
            offerTmp = {
                "offer_id": client_id,
                "price_info": {
                    "price": round(float(offer['TotalPrice']['TotalAmount']['#text'])*val, 2),
                    "fee_amount": 0,
                    "commission_amount": 0
                },
                "upsell": True,
                "booking": True,
                "price_details": [],
                "baggages_info": [],
                "fares_info": [],
                "routes": [],
                "provider": {
                    "provider_id": guid,
                    "name": name
                }
            }

            offerItem = offer['OfferItem'] if await check_type(offer['OfferItem']) == 'list' else []

            if offerItem == []:
                offerItem.append(offer['OfferItem'])

            for ofItm in offerItem:
                if await check_type(ofItm['FareDetail']['PaxRefID']) == 'string':
                    offerItemList.append({
                        'offerItemId': ofItm['OfferItemID'],
                        'paxRefId': ofItm['FareDetail']['PaxRefID']
                    })
                else:
                    for paxRefId in ofItm['FareDetail']['PaxRefID']:
                        offerItemList.append({
                            'offerItemId': ofItm['OfferItemID'],
                            'paxRefId': paxRefId
                        })

            for item in offerItem:
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'ADT' in narsa:
                        price_tmp = {
                            "passenger_type": "ADT",
                            "currency": currency['curTo'],
                            "quantity": srch['adt'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['adt'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['adt'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['adt'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'ADT' in narsa:
                        price_tmp = {
                            "passenger_type": "ADT",
                            "currency": currency['curTo'],
                            "quantity": srch['adt'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['adt'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['adt'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['adt'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'CNN' in narsa:
                        price_tmp = {
                            "passenger_type": "CHD",
                            "currency": currency['curTo'],
                            "quantity": srch['chd'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['chd'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['chd'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['chd'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'CNN' in narsa:
                        price_tmp = {
                            "passenger_type": "CHD",
                            "currency": currency['curTo'],
                            "quantity": srch['chd'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['chd'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['chd'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['chd'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'INF' in narsa:
                        price_tmp = {
                            "passenger_type": "INF",
                            "currency": currency['curTo'],
                            "quantity": srch['inf'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['inf'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['inf'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['inf'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'INF' in narsa:
                        price_tmp = {
                            "passenger_type": "INF",
                            "currency": currency['curTo'],
                            "quantity": srch['inf'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['inf'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['inf'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['inf'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                    narsa = ""
                    pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                    for paxrefid in pxid:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                            narsa = paxrefid['PTC']
                    if 'INS' in narsa:
                        price_tmp = {
                            "passenger_type": "INS",
                            "currency": currency['curTo'],
                            "quantity": srch['ins'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['ins'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['ins'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['ins'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
                elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == item['FareDetail']['PaxRefID'][0]:
                            narsa = paxrefid['PTC']
                    if 'INS' in narsa:
                        price_tmp = {
                            "passenger_type": "INS",
                            "currency": currency['curTo'],
                            "quantity": srch['ins'],
                            "single_base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "single_tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "single_tax_details": [],
                            "fee_amount": 0,
                            "commission_amount": 0,
                            "single_total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "base_total_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val * srch['ins'], 2),
                            "tax_total_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val * srch['ins'], 2),
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val * srch['ins'], 2),
                            "payable_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        offerTmp['price_details'].append(price_tmp)
            fareComponent = offerItem[0]['FareDetail']['FareComponent'] if await check_type(offerItem[0]['FareDetail']['FareComponent']) == 'list' else []
            
            offerTmp['baggages_info'] = await asyncio.create_task(get_baggages_info(offer['BaggageAllowance'], dataList))
            offerTmp['fares_info'] = await asyncio.create_task(get_fares_info(offerItem, dataList))
            
            if fareComponent == []:
                fareComponent.append(offerItem[0]['FareDetail']['FareComponent'])

            fareCode = fareComponent[0]['FareBasisCode']
            bookingClass = fareComponent[0]['RBD']['RBD_Code']
            segmentClass = fareComponent[0]['CabinType']['CabinTypeCode']
            holdBaggage = None
            carryOn = None
            baggages = offer['BaggageAllowance'] if await check_type(offer['BaggageAllowance']) == 'list' else [offer['BaggageAllowance']]
            bagList = dataList['BaggageAllowanceList']['BaggageAllowance'] if await check_type(dataList['BaggageAllowanceList']['BaggageAllowance']) == 'list' else [dataList['BaggageAllowanceList']['BaggageAllowance']]
            for bag in baggages:
                for bagId in bagList:
                    if bag['BaggageAllowanceRefID'] == bagId['BaggageAllowanceID']:
                        if bagId['TypeCode'] == 'CarryOn':
                            carryOn = f"{bagId['WeightAllowance']['MaximumWeightMeasure']['#text']} {bagId['WeightAllowance']['MaximumWeightMeasure']['UnitCode']}"
                        else:
                            holdBaggage = f"{bagId['PieceAllowance']['TotalQty']} PC"
            journeyIds = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']
            next = False
            for ids in offerItem:
                if journeyIds != ids['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']:
                    next = True
                    break
            if next:
                continue
            rt_ind = 0
            for journeyId in journeyIds:
                routeTmp = {
                    "route_index": rt_ind,
                    "direction"  : "",
                    "stops"      : 0,
                    "segments"   : []
                }
                rt_ind += 1    
                segList = dataList['PaxJourneyList']['PaxJourney'] if await check_type(dataList['PaxJourneyList']['PaxJourney']) == 'list' else [dataList['PaxJourneyList']['PaxJourney']]
                for seg in segList:
                    if journeyId == seg['PaxJourneyID']:
                        segments = []
                        if await check_type(seg['PaxSegmentRefID']) == 'string':
                            segments.append(seg['PaxSegmentRefID'])
                        elif await check_type(seg['PaxSegmentRefID']) == 'list':
                            segments = seg['PaxSegmentRefID']
                        seg_ind = 0
                        for segment in segments:
                            paxSegments = dataList['PaxSegmentList']['PaxSegment'] if await check_type(dataList['PaxSegmentList']['PaxSegment']) == 'list' else [dataList['PaxSegmentList']['PaxSegment']]
                            for paxSeg in paxSegments:
                                if paxSeg['PaxSegmentID'] == segment:
                                    mySeg = await make_segment(paxSeg, fareCode, segmentClass, bookingClass, holdBaggage, carryOn)
                                    mySeg['segment_index'] = seg_ind
                                    seg_ind += 1
                                    routeTmp['segments'].append(mySeg)
                routeTmp['stops'] = len(routeTmp['segments']) - 1
                routeTmp['direction'] = f"{routeTmp['segments'][0]['departure_airport']}-{routeTmp['segments'][-1]['arrival_airport']}"
                offerTmp['routes'].append(routeTmp)
            # fullOffer = AdditionsTicket(
            #     ticket=offerTmp,
            #     buy_id=client_id,
            #     other={
            #         'offerId': offer['OfferID'],
            #         'fareFamilies': offerSorted['fare_families'],
            #         'dataList': dataList,
            #         'offerItemList': offerItemList,
            #         'price': offer['TotalPrice']['TotalAmount']['#text'],
            #         'currency': offer['TotalPrice']['TotalAmount']['CurCode']
            #     },
            #     gds_id=0,
            #     sp_name=name
            # )
            full_offers.append(offerTmp)
    return full_offers

async def sort_offers(offers):
    # print(len(offers))
    new_offers = []
    available_tickets = []

    for offer in offers:
        offerItem = offer['OfferItem'] if await check_type(offer['OfferItem']) == 'list' else [offer['OfferItem']]
        if await check_type(offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']) == 'list':
            new_id = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'][0] + offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'][1]
            available_tickets.append(new_id)
        else:
            available_tickets.append(offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'])
    # new_offers = get_unique_offers(offers, set(available_tickets))
    return await get_unique_offers(offers, set(available_tickets))

async def get_unique_offers(offers, journeyIdList):
    new_offers = []
    template = {
        'offer': 'offer',
        'fare_families': []
    }
    for uniqueId in journeyIdList:
        offerListTmp = []
        for offer in offers:
            offerItem = offer['OfferItem'] if await check_type(offer['OfferItem']) == 'list' else [offer['OfferItem']]
            if await check_type(offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']) == 'list':
                new_id = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'][0] + offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'][1]
            else:
                new_id = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']
            if uniqueId == new_id:
                offerListTmp.append(offer)
        minOfferPrice = float(offerListTmp[0]['TotalPrice']['TotalAmount']['#text'])
        offerTmp = offerListTmp[0]
        for offer in offerListTmp:
            if minOfferPrice > float(offer['TotalPrice']['TotalAmount']['#text']):
                minOfferPrice = float(offer['TotalPrice']['TotalAmount']['#text'])
                offerTmp = offer
        new_offers.append({
            'offer': offerTmp,
            'fare_families': offerListTmp
        })
    return new_offers

async def make_segment(data, fareCode, segmentClass, bookingClass, holdBaggage, carryOn):
    depAir = await getAirport(data['Dep']['IATA_LocationCode'])
    arrAir = await getAirport(data['Arrival']['IATA_LocationCode'])
    segTmp = {
        "segment_index": 0,
        "leg": f"{data['Dep']['IATA_LocationCode']}-{data['Arrival']['IATA_LocationCode']}",
        "carrier_code": data['DatedOperatingLeg']['CarrierAircraftType']['CarrierAircraftTypeCode'],
        "carrier_name": data['OperatingCarrierInfo']['CarrierDesigCode'],
        "carrier_logo": 'https://b2b.easybooking.uz/images/airline/'+ data['OperatingCarrierInfo']['CarrierDesigCode'] + '.svg',
        "flight_number": data['OperatingCarrierInfo'].get('OperatingCarrierFlightNumberText', None),
        "departure_airport": data['Dep']['IATA_LocationCode'],
        "departure_date": await date_formater(data['Dep']['AircraftScheduledDateTime']),
        "departure_time": await time_formater(data['Dep']['AircraftScheduledDateTime']),
        "departure_timezone": "GMT+5:00",
        "arrival_airport": data['Arrival']['IATA_LocationCode'],
        "arrival_date": await date_formater(data['Arrival']['AircraftScheduledDateTime']),
        "arrival_time": await time_formater(data['Arrival']['AircraftScheduledDateTime']),
        "arrival_timezone": "GMT+5:00",
        "duration_minutes": await duration_formatter(data['Duration']),
        "seatmap_availability": False,
        "services_availability": False,
        "flights_info": {
            "airplane_info": {
                "airplane_code": data['DatedOperatingLeg']['CarrierAircraftType']['CarrierAircraftTypeCode'],
                "airplane_name": data['OperatingCarrierInfo']['CarrierDesigCode'],
                "seat_distance": "",
                "seat_width": "",
                "seat_angle": "",
                "has_wifi": False
            },
            "departure_country": 'Uzbekistan', #depAir.country_eng,
            "departure_city": 'TAS', #depAir.city_eng,
            "departure_city_code": 'TAS', #depAir.city_eng,
            "departure_airport": data['Dep']['IATA_LocationCode'],
            "departure_terminal": data['Dep'].get('TerminalName', None),
            "arrival_country": 'Turkey', #arrAir.country_eng,
            "arrival_city": 'IST', #arrAir.city_eng,
            "arrival_city_code": 'IST', #arrAir.city_eng,
            "arrival_airport": data['Arrival']['IATA_LocationCode'],
            "arrival_terminal": data['Arrival'].get('TerminalName', None),
            "stop_time_minutes": None,
            "marketing_airline_code": data['MarketingCarrierInfo']['CarrierDesigCode'],
            "marketing_airline_logo": 'https://b2b.easybooking.uz/images/airline/'+ data['MarketingCarrierInfo']['CarrierDesigCode'] +'.svg',
            "marketing_airline_name": data['MarketingCarrierInfo']['CarrierDesigCode'],
            "operating_airline_code": data['OperatingCarrierInfo']['CarrierDesigCode'],
            "operating_airline_logo": 'https://b2b.easybooking.uz/images/airline/'+ data['OperatingCarrierInfo']['CarrierDesigCode'] +'.svg',
            "operating_airline_name": data['OperatingCarrierInfo']['CarrierDesigCode'],
        }
    }
    return segTmp

async def getAirport(iata):
    air = None #Airports.objects.get(iata_code=iata)
    return air

async def date_formater(date: str):
    return date

async def time_formater(time: str):
    time = time.split('T')[1]
    time = time.split(':')
    return f"{time[0]}:{time[1]}:00"

async def duration_formatter(date: str):
    date = date.split('PT')[1]
    hours = 0
    minutes = 0
    if 'H' in date:
        hours = date.split('H')
        if len(hours) > 1:
            minutes = hours[1].split('M')[0]
    else:
        minutes = date.split('M')[0]

    amount = 0
    if hours != 0:
        hours = int(hours[0])
        amount += hours*60
    if minutes != '':
        minutes = int(minutes)
        amount += minutes

    return f"{amount}"

async def rules_parser(data, offer):
    getRulesData = {
        "status": "success",
        "message": "Successfully",
        "buy_id": offer['client_id'],
        "routes": []
    }

    dataSegments = data['data']['Body']['AppData']['Rules:Mixvel_OrderRulesRS']['Response']['DataLists']['PaxSegmentList']['PaxSegment']
    if await check_type(dataSegments) == 'dict':
        dataSegmentsTmp = [dataSegments]
        dataSegments = dataSegmentsTmp

    dataSegmentRules = data['data']['Body']['AppData']['Rules:Mixvel_OrderRulesRS']['Response']['Rules']
    if await check_type(dataSegmentRules) == 'dict':
        dataSegmentRulesTmp = [dataSegmentRules]
        dataSegmentRules = dataSegmentRulesTmp

    routesTmp = None #formatRoutes(offer['response']['routes'])
    for rt in routesTmp:
        for segment in rt['segments']:
            try:
                fare_condition = await get_fare_conditions(segment, dataSegments, dataSegmentRules)
            except:
                fare_condition = None
            rules = {
                "blocks": {
                    "airline": segment['carrier_code'],
                    "tariff": segment['tariff'],
                    "baggage": segment['baggage'],
                    "blocks": [],
                    "alldata": None,
                    "full_rules": fare_condition,
                    "redirect": None
                }
            }
            segment['rules'] = rules
    getRulesData['routes'] = routesTmp
    return getRulesData

async def get_fare_conditions(segment, dataSegments, dataSegmentRules):
    for seg in dataSegments:
        if seg['Arrival']['IATA_LocationCode'] == segment['arrival_airport'] and seg['Dep']['IATA_LocationCode'] == segment['departure_airport']:
            paxSegId = seg['PaxSegmentID']
            for rule in dataSegmentRules:
                if rule['PaxSegmentRefID'] == paxSegId:
                    return rule['FareRuleText']['Remark']
    return None

async def fare_family_parser(fareFamilies, currency, request_id, dataList, routes):
    if currency['curFrom'] == currency['curTo']:
        val = 1
    else:
        val = await Helper.currency_converter(currency['curFrom'], currency['curTo'])

    ffData = {
        "request_id": request_id,
        "status": "success",
        "message": "Successfully",
        "offers": []
    }
    
    srch = redis_client.get(f"{request_id}_search")

    for ff in fareFamilies:
        client_id = hashlib.md5(str("%0.11d" % random.randint(0, 999999999999)).encode()).hexdigest()
        ffTmp = {
            "buy_id": client_id,
            "price": round(float(ff['TotalPrice']['TotalAmount']['#text'])*val, 2),
            "price_details": [],
            "currency": currency['curTo'],
            "legs": [],
        }
        offerItem = ff['OfferItem'] if await check_type(ff['OfferItem']) == 'list' else [ff['OfferItem']]
        offerItemList = []
        for ofItm in offerItem:
            if await check_type(ofItm['FareDetail']['PaxRefID']) == 'string':
                    offerItemList.append({
                        'offerItemId': ofItm['OfferItemID'],
                        'paxRefId': ofItm['FareDetail']['PaxRefID']
                    })
            else:
                for paxRefId in ofItm['FareDetail']['PaxRefID']:
                    offerItemList.append({
                        'offerItemId': ofItm['OfferItemID'],
                        'paxRefId': paxRefId
                    })

        for item in offerItem:
            if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                narsa = ""
                pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                for paxrefid in pxid:
                    if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                        narsa = paxrefid['PTC']
                if "ADT" in narsa:
                    for _ in range(srch['adt']):
                        price_tmp = {
                            "passenger_type": "ADT",
                            "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "tax_details": [],
                            "commission_amount": 0,
                            "payable_amount": 0,
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "currency": currency['curTo'],
                            "fee_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        ffTmp['price_details'].append(price_tmp)
            elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                for itemObj in item['FareDetail']['PaxRefID']:
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == itemObj:
                            narsa = paxrefid['PTC']
                    if 'ADT' in narsa:
                        for i in range(srch['adt']):
                            price_tmp = {
                                "passenger_type": "ADT",
                                "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                                "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                                "tax_details": [],
                                "commission_amount": 0,
                                "payable_amount": 0,
                                "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                                "currency": currency['curTo'],
                                "fee_amount": 0
                            }
                            price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                            ffTmp['price_details'].append(price_tmp)
                        break
            
            if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                narsa = ""
                pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                for paxrefid in pxid:
                    if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                        narsa = paxrefid['PTC']
                if 'CNN' in narsa:
                    for i in range(srch['chd']):
                        price_tmp = {
                            "passenger_type": "CHD",
                            "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "tax_details": [],
                            "commission_amount": 0,
                            "payable_amount": 0,
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "currency": currency['curTo'],
                            "fee_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        ffTmp['price_details'].append(price_tmp)                  
            elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                for itemObj in item['FareDetail']['PaxRefID']:
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == itemObj:
                            narsa = paxrefid['PTC']
                    if 'CNN' in narsa:
                        for i in range(srch['chd']):
                            price_tmp = {
                                "passenger_type": "CHD",
                                "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                                "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                                "tax_details": [],
                                "commission_amount": 0,
                                "payable_amount": 0,
                                "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                                "currency": currency['curTo'],
                                "fee_amount": 0
                            }
                            price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                            ffTmp['price_details'].append(price_tmp)
                        break

            if await check_type(item['FareDetail']['PaxRefID']) == 'string':
                narsa = ""
                pxid = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
                for paxrefid in pxid:
                    if paxrefid['PaxID'] == item['FareDetail']['PaxRefID']:
                        narsa = paxrefid['PTC']
                if 'INF' in narsa:
                    for i in range(srch['inf']):
                        price_tmp = {
                            "passenger_type": "INF",
                            "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                            "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                            "tax_details": [],
                            "commission_amount": 0,
                            "payable_amount": 0,
                            "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                            "currency": currency['curTo'],
                            "fee_amount": 0
                        }
                        price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                        ffTmp['price_details'].append(price_tmp)        
            elif await check_type(item['FareDetail']['PaxRefID']) == 'list':
                for itemObj in item['FareDetail']['PaxRefID']:
                    narsa = ""
                    for paxrefid in dataList['PaxList']['Pax']:
                        if paxrefid['PaxID'] == itemObj:
                            narsa = paxrefid['PTC']
                    if 'INF' in narsa:
                        for i in range(srch['inf']):
                            price_tmp = {
                                "passenger_type": "INF",
                                "base_amount": round(float(item['FareDetail']['Price']['BaseAmount']['#text']) * val, 2),
                                "tax_amount": round(float(item['FareDetail']['Price']['TaxSummary']['TotalTaxAmount']['#text']) * val, 2),
                                "tax_details": [],
                                "commission_amount": 0,
                                "payable_amount": 0,
                                "total_amount": round(float(item['FareDetail']['Price']['TotalAmount']['#text']) * val, 2),
                                "currency": currency['curTo'],
                                "fee_amount": 0
                            }
                            price_tmp['payable_amount'] = round( price_tmp['total_amount'] - price_tmp['commission_amount'], 2)
                            ffTmp['price_details'].append(price_tmp)
                        break

        fareComponent = offerItem[0]['FareDetail']['FareComponent'] if await check_type(offerItem[0]['FareDetail']['FareComponent']) == 'list' else [offerItem[0]['FareDetail']['FareComponent']]

        PriceClassRefID = fareComponent[0]['PriceClassRefID']
        fareCode = fareComponent[0]['FareBasisCode']
        bookingClass = fareComponent[0]['RBD']['RBD_Code']
        segmentClass = fareComponent[0]['CabinType']['CabinTypeCode']
        holdBaggage = None
        carryOn = None
        baggages = ff['BaggageAllowance'] if await check_type(ff['BaggageAllowance']) == 'list' else [ff['BaggageAllowance']]
        bagList = dataList['BaggageAllowanceList']['BaggageAllowance'] if await check_type(dataList['BaggageAllowanceList']['BaggageAllowance']) == 'list' else [dataList['BaggageAllowanceList']['BaggageAllowance']]
        for bag in baggages:
            for bagId in bagList:
                if bag['BaggageAllowanceRefID'] == bagId['BaggageAllowanceID']:
                    if bagId['TypeCode'] == 'CarryOn':
                        carryOn = f"{bagId['WeightAllowance']['MaximumWeightMeasure']['#text']} {bagId['WeightAllowance']['MaximumWeightMeasure']['UnitCode']}"
                    else:
                        holdBaggage = f"{bagId['PieceAllowance']['TotalQty']} PC"
        journeyIds = offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID'] if await check_type(offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']) == 'list' else [offerItem[0]['Service']['ServiceAssociations']['PaxJourneyRef']['PaxJourneyRefID']]
        refundable = offerItem[0]['RefundStatus']
 
        for journeyId in journeyIds:
            legTmp = {
                "id": client_id,
                "fare_family": "",
                "segments": [],
            } 
            segList = dataList['PaxJourneyList']['PaxJourney'] if await check_type(dataList['PaxJourneyList']['PaxJourney']) == 'list' else [dataList['PaxJourneyList']['PaxJourney']]
            for seg in segList:
                if journeyId == seg['PaxJourneyID']:
                    segments = []
                    if await check_type(seg['PaxSegmentRefID']) == 'string':
                        segments.append(seg['PaxSegmentRefID'])
                    elif await check_type(seg['PaxSegmentRefID']) == 'list':
                        segments = seg['PaxSegmentRefID']

                    for segment in segments:
                        for paxSeg in dataList['PaxSegmentList']['PaxSegment']:
                            if paxSeg['PaxSegmentID'] == segment:
                                services = []
                                for pcl in dataList['PriceClassList']['PriceClass']:
                                    if pcl['PriceClassID'] == PriceClassRefID:
                                        legTmp['fare_family'] = pcl.get('Name', 'Unknown')
                                        services = pcl.get('Desc', [])
                                mySeg = await make_ff_segment(paxSeg, fareCode, segmentClass, holdBaggage, carryOn, services, bookingClass, refundable)
                                legTmp['segments'].append(mySeg)
            ffTmp['legs'].append(legTmp)
        ffData['offers'].append(copy.deepcopy(ffTmp))

        ffTmp['routes'] = routes

        other = {
            'offerId': ff['OfferID'],
            'offerItemList': offerItemList,
            'price': ff['TotalPrice']['TotalAmount']['#text'],
            'currency': ff['TotalPrice']['TotalAmount']['CurCode']
        }

        redis_client.set(
            f"{request_id}_offer_{client_id}",
            {
                "offer_id": ff['OfferID'],
                "client_id": client_id,
                "request_id": request_id,
                "response": ffTmp,
                "supplier_id": currency['sp_id'],
                "other": other,
                "next_token": None
            },
            1200
        )
    return ffData

async def make_ff_segment(paxSeg, fareCode, segmentClass, holdBaggage, carryOn, services, bookingClass, refundable):
    segTmp = {
        "fare_basis": fareCode,
        "booking_class": bookingClass,
        "service_class": segmentClass.lower(),
        "departure_airport": paxSeg['Dep']['IATA_LocationCode'],
        "arrival_airport": paxSeg['Arrival']['IATA_LocationCode'],
        "marketing_airline": "TK",
        "airline_logo": 'https://b2b.easybooking.uz/images/airline/'+ paxSeg['MarketingCarrierInfo']['CarrierDesigCode'] +'.svg',
        "ff_code": fareCode,
        "ff_data": {
            "name_short": fareCode,
            "name_ru": fareCode,
            "name_en": fareCode,
            "name_pop": fareCode,
            "baggage": holdBaggage,
            "is_refund": True if refundable.lower() == 'refundable' else False,
            "is_seat_choice": False,
            "services": [{
                "status": "included",
                "name_ru": service['DescText'],
                "name_en": service['DescText'],
                "code": service['Access']
            } for service in services]
        }
    }
    return segTmp

async def check_type(object):
    if isinstance(object, list):
        return 'list'
    elif isinstance(object, dict):
        return 'dict'
    elif isinstance(object, str):
        return 'string'
    elif isinstance(object, int):
        return 'int'
    elif isinstance(object, float):
        return 'float'

async def get_baggages_info(BaggageAllowance, DataList):
    answer = []
    baggages = BaggageAllowance if await check_type(BaggageAllowance) == 'list' else [BaggageAllowance]
    segs = baggages[0]['BaggageFlightAssociations']['PaxSegmentRef']['PaxSegmentRefID'] if await check_type(baggages[0]['BaggageFlightAssociations']['PaxSegmentRef']['PaxSegmentRefID']) == 'list' else [baggages[0]['BaggageFlightAssociations']['PaxSegmentRef']['PaxSegmentRefID']]
    for seg in segs:
        paxes = baggages[0]['PaxRefID'] if await check_type(baggages[0]['PaxRefID']) == 'list' else [baggages[0]['PaxRefID']]
        for pax in paxes:
            leg = ""
            segments = DataList['PaxSegmentList']['PaxSegment'] if await check_type(DataList['PaxSegmentList']['PaxSegment']) == 'list' else [DataList['PaxSegmentList']['PaxSegment']]
            for segment in segments:
                if segment['PaxSegmentID'] == seg:
                    leg = f"{segment['Dep']['IATA_LocationCode']}-{segment['Arrival']['IATA_LocationCode']}"
            passenger_type = ""
            passenngers = DataList['PaxList']['Pax'] if await check_type(DataList['PaxList']['Pax']) == 'list' else [DataList['PaxList']['Pax']]
            for px in passenngers:
                if px['PaxID'] == pax:
                    passenger_type = px['PTC'] if px['PTC'] != "CNN" else "CHD"
            baggage_cnt = 0
            hand_cnt = 0
            unit = "KG"

            bags = DataList['BaggageAllowanceList']['BaggageAllowance'] if await check_type(DataList['BaggageAllowanceList']['BaggageAllowance']) == 'list' else [DataList['BaggageAllowanceList']['BaggageAllowance']]
            for bag in bags:
                if baggages[0]['BaggageAllowanceRefID'] == bag['BaggageAllowanceID']:
                    if "PieceAllowance" in bag:
                        baggage_cnt = int(bag['PieceAllowance']['TotalQty'])
                    elif "WeightAllowance" in bag:
                        hand_cnt = int(bag['WeightAllowance']['MaximumWeightMeasure']['#text'])
                        unit     = bag['WeightAllowance']['MaximumWeightMeasure']['UnitCode'] if bag['WeightAllowance']['MaximumWeightMeasure']['UnitCode'] == "PC" else "KG"
                if baggages[1]['BaggageAllowanceRefID'] == bag['BaggageAllowanceID']:
                    if "PieceAllowance" in bag:
                        baggage_cnt = int(bag['PieceAllowance']['TotalQty'])
                    elif "WeightAllowance" in bag:
                        hand_cnt = int(bag['WeightAllowance']['MaximumWeightMeasure']['#text'])
                        unit     = bag['WeightAllowance']['MaximumWeightMeasure']['UnitCode'] if bag['WeightAllowance']['MaximumWeightMeasure']['UnitCode'] == "PC" else "KG"

            bagTmp = {
                "leg": leg,
                "passenger_type": passenger_type,
                "baggage": {
                    "value": baggage_cnt,
                    "unit" : "PC",
                    "size" : {
                        "height": None,
                        "width" : None,
                        "length": None,
                        "unit"  : "cm"
                    }
                },
                "hand_baggage": {
                    "value": hand_cnt,
                    "unit" : unit,
                    "size" : {
                        "height": None,
                        "width" : None,
                        "length": None,
                        "unit"  : "cm"
                    }
                },
                "description": ""
            }
            answer.append(bagTmp)
    return answer

async def get_fares_info(offerItem, dataList):
    answer = []
    for item in offerItem:
        pass_type = item['FareDetail']['PaxRefID'] if await check_type(item['FareDetail']['PaxRefID']) == 'string' else item['FareDetail']['PaxRefID'][0]
        paxes = dataList['PaxList']['Pax'] if await check_type(dataList['PaxList']['Pax']) == 'list' else [dataList['PaxList']['Pax']]
        for pax in paxes:
            if pass_type == pax['PaxID']:
                pass_type = pax['PTC'] if pax['PTC'] != "CNN" else "CHD"
        fareComponents = item['FareDetail']['FareComponent'] if await check_type(item['FareDetail']['FareComponent']) == 'list' else [item['FareDetail']['FareComponent']]

        for seg in fareComponents:
            leg = ""
            segments = dataList['PaxSegmentList']['PaxSegment'] if await check_type(dataList['PaxSegmentList']['PaxSegment']) == 'list' else [dataList['PaxSegmentList']['PaxSegment']]
            for segment in segments:
                if segment['PaxSegmentID'] == seg['PaxSegmentRefID']:
                    leg = f"{segment['Dep']['IATA_LocationCode']}-{segment['Arrival']['IATA_LocationCode']}"
            ff = seg['PriceClassRefID']
            ffs = dataList['PriceClassList']['PriceClass'] if await check_type(dataList['PriceClassList']['PriceClass']) == 'list' else [dataList['PriceClassList']['PriceClass']]
            ff_name = ""
            ff_services = []
            for fare_info in ffs:
                if ff == fare_info['PriceClassID']:
                    ff_name = fare_info['Name']
                    services = fare_info['Desc'] if await check_type(fare_info['Desc']) == 'list' else [fare_info['Desc']]
                    ff_services = [
                        {
                            "status": True,
                            "code"  : fare_info['Code'],
                            "name"  : x['DescText']
                        } for x in services
                    ]
            fareTmp = {
                "leg": leg,
                "passenger_type": pass_type,
                "seats": seg['RBD']['Availability'],
                "upsell": {
                    "name": ff_name,
                    "services": ff_services
                },
                "fare_code": seg['FareBasisCode'],
                "service_class": seg['CabinType']['CabinTypeCode'],
                "booking_class": seg['RBD']['RBD_Code'],
                "fare_messages": {
                    "LTD": "",
                    "PEN": ""
                    
                },
                "description": ""
            }
            answer.append(fareTmp)
    return answer
