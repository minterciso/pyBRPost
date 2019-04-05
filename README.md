# Brazilian Post Office Module
This module is to help whoever needs a API to query the brazilian post office to know:
1. When the package will arrive
2. How much will it cost
3. Possibility to query different shipping methods

# Installation
To install this module simply add it via pip

    pip install pyBRPost

It requires some extra modules:

    pip install requests xmltodict
    
# Usage
To use this module all you need is to configure the package information and execute the get_fare()
method. Here's a simple test:

    from pybrpost import ship.fare, ship.options
    
    tst = fare.Fare()
    tst.requestServices = [
        options.Service.SEDEX_10_RETAIL,
        options.Service.SEDEX_12,
        options.Service.SEDEX_CASH,
        options.Service.SEDEX_RETAIL,
        options.Service.SEDEX_TODAY_RETAIL,
        options.Service.PAC_CASH,
        options.Service.PAC_RETAIL
    ]
    tst.dimensions['weight'] = 0.875
    tst.dimensions['length'] = 16
    tst.dimensions['width'] = 11
    tst.dimensions['height'] = 10
    tst.dimensions['diameter'] = 10
    tst.cepDestination = '09571000'
    tst.cepOrigin = '24738791'
    tst.value = 2500.75
    tst.packageFormat = options.ObjectType.BOX
    tst.extras['receiving_warning'] = True
    try:
        fare_return = tst.get_fare()
    except Exception as error:
        print(error)
        exit(-1)
    for ret in fare_return:
        print('Service: {serv}'.format(serv=ret['service']))
        error_code = ret['error_code']
        if error_code != 0:
            print('Error ({code}): {desc}'.format(code=error_code, desc=ret['error_msg']))
        else:
            print('Time: {time} day{mult}'.format(time=ret['delivery_time'], mult='s' if ret['delivery_time'] > 1 else ''))
            print('Value: R$ {val}'.format(val=ret['value']))
            print('Deliver on saturday? {sat}'.format(sat=ret['delivery_saturday']))
            print('Delivery on: {delivery_date}'.format(
                delivery_date=tst.get_estimated_delivery_day(add_days=1,
                                                             travel_days=ret['delivery_time'],
                                                             deliver_on_saturday=ret['delivery_saturday']).strftime('%d/%m/%Y')))
            print('')

This is a little big, so let's drill down this example in 3 easy steps:
## Import
    from pybrpost import ship.fare, ship.options
    
Those are the basic imports, there's also a 'ship.errors' import that you can use to capture
the exceptions.

The 'ship.options' file contains the enum classes Service and ObjectType that, are responsible to configure
the methods to send the package, and the format of the package.

Those are the options you have for the Service enum:
* SEDEX_RETAIL - Common Sedex type
* SEDEX_TO_CHARGE - Sedex to be charged on the receiver
* SEDEX_10_RETAIL - Sedex 10
* SEDEX_TODAY_RETAIL - Sedex on the same day
* SEDEX_CASH - Sedex payment on cash
* SEDEX_PAYMENT_ON_DELIVERY - Sedex payment on delivery
* SEDEX_12 - Sedex 12 
* PAC_RETAIL - Common PAC
* PAC_CASH - PAC on cash
* PAC_PAYMENT_ON_DELIVERY - PAC with payment on delivery

And those are the options you have for the ObjectType enum:
* BOX - Most common of Sedex for big products
* ROLL - Can be sometimes referred as "prism"
* LETTER - Anything that can be sent as ane Envelope

You can find more of those options on the [Correios site](http://correios.com.br/).

## Setup
After importing, you need to instantiate a 'ship.fare.Fare' object, and create the initial setup:

    tst = fare.Fare()
    tst.requestServices = [
        options.Service.SEDEX_10_RETAIL,
        options.Service.SEDEX_12,
        options.Service.SEDEX_CASH,
        options.Service.SEDEX_RETAIL,
        options.Service.SEDEX_TODAY_RETAIL,
        options.Service.PAC_CASH,
        options.Service.PAC_RETAIL
    ]
    tst.dimensions['weight'] = 0.875
    tst.dimensions['length'] = 16
    tst.dimensions['width'] = 11
    tst.dimensions['height'] = 10
    tst.dimensions['diameter'] = 10
    tst.cepDestination = '09571000'
    tst.cepOrigin = '24738791'
    tst.value = 2500.75
    tst.packageFormat = options.ObjectType.BOX
    tst.extras['receiving_warning'] = True
    
Of all those options, only those are mandatory:
* requestService
* dimenstions
* cepDestination
* cepOrigin
* packageFormat

If some of those are missing, or wrong, there's 2 possible exceptions that will be thrown when
executing the get_fare() method:
* InvalidParameterError
* MissingParametersError

## Getting the fare
After importing and setting up the information to query, you should call the get_fare() method:

    try:
        fare_return = tst.get_fare()
    except Exception as error:
        print(error)
        exit(-1)

This method will POST the Correios API with the setup you created before, if there's anything wrong
with the setup it'll raise an exception. If everything works out smoothly, it'll return a list
with all the results (usually one for 'requestService'), and you can easily read them as a dictionary:

     for ret in fare_return:
        print('Service: {serv}'.format(serv=ret['service']))
        error_code = ret['error_code']
        if error_code != 0:
            print('Error ({code}): {desc}'.format(code=error_code, desc=ret['error_msg']))
        else:
            print('Time: {time} day{mult}'.format(time=ret['delivery_time'], mult='s' if ret['delivery_time'] > 1 else ''))
            print('Value: R$ {val}'.format(val=ret['value']))
            print('Deliver on saturday? {sat}'.format(sat=ret['delivery_saturday']))

There's one "gift" inside this package that has **nothing** to do with the Correios API, an 
estimated delivery method, that you can call to get a possible date on the delivery: 

            print('Delivery on: {delivery_date}'.format(
                delivery_date=tst.get_estimated_delivery_day(add_days=1,
                                                             travel_days=ret['delivery_time'],
                                                             deliver_on_saturday=ret['delivery_saturday']).strftime('%d/%m/%Y')))
            print('')
