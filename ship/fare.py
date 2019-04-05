import requests
import xmltodict
from datetime import datetime, timedelta
import ship.options as options
from ship.errors import InvalidParameterError, MissingParametersError


class Fare:
    """
    This class is the main class of the module and is used to query the Correios API to get predictions on both time
    needed to send the package via the service chosen and the cost you'll have.
    """

    def __init__(self):
        # The package size (in cm) and weight in Kg
        self.dimensions = {
            'weight': 0.0,
            'length': 0.0,
            'height': 0.0,
            'width': 0.0,
            'diameter': 0.0
        }
        # The origin and destination CEP (Zip code)
        self.cepOrigin = ''
        self.cepDestination = ''
        # Package value, used only when you have to (or want to) declare the value of the package contents (in R$)
        self.value = 0.0
        # Some extra options specific to the Brazilian Post Office
        self.extras = {
            'receiving_warning': False,  # Set this to True if you'll need a warning of when the package was received
            'by_own_hand': False  # Set this to True if you want the user to receive on his own hand (named package)
        }
        self.packageFormat = options.ObjectType.BOX  # Select the format of the package the will be sent
        self.requestServices = []  # Add all the services you want to receive a prediction
        self.__payload = {}
        self.__url = 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx/CalcPrecoPrazo'

    def __setup(self):
        """
        Before executing the get_fare() method, use this to create the payload. If there's an error it'll raise
        an ShipException error
        """
        # Check for errors
        missing_parameters = []
        if len(self.requestServices) == 0:
            missing_parameters.append('requestServices')
        if len(self.cepDestination) == 0:
            missing_parameters.append('cepDestination')
        if len(self.cepOrigin) == 0:
            missing_parameters.append('cepOrigin')
        if len(missing_parameters) > 0:
            msg = 'The parameters {params} must be specified'.format(
                params=', '.join(['\'' + x + '\'' for x in missing_parameters]))
            raise MissingParametersError(parameters=missing_parameters, message=msg)
        if len(self.cepOrigin) != 8:
            raise InvalidParameterError(value=self.cepOrigin, message='invalid cepOrigin')
        if len(self.cepDestination) != 8:
            raise InvalidParameterError(value=self.cepDestination, message='invalid cepDestination')
        for key, item in self.dimensions.items():
            if item < 0:
                raise InvalidParameterError(value=item, message='invalid value for \'{key}\''.format(key=key))
        for key, item in self.extras.items():
            if type(item) != bool:
                raise InvalidParameterError(value=item, message='invalid value for \'{key}\''.format(key=key))

        # Now create the payload
        self.__payload = {
            'nCdEmpresa': '',
            'sDsSenha': '',
            'nCdServico': ','.join([x.value for x in self.requestServices]),
            'sCepOrigem': self.cepOrigin,
            'sCepDestino': self.cepDestination,
            'nVlPeso': self.dimensions['weight'],
            'nVlComprimento': self.dimensions['length'],
            'nVlAltura': self.dimensions['height'],
            'nVlLargura': self.dimensions['width'],
            'nVlDiametro': self.dimensions['diameter'],
            'nCdFormato': self.packageFormat.value,
            'nVlValorDeclarado': self.value,
            'sCdMaoPropria': 'S' if self.extras['by_own_hand'] else 'N',
            'sCdAvisoRecebimento': 'S' if self.extras['receiving_warning'] else 'N'
        }

    def get_fare(self):
        """
        Create the payload, and query via POST method the Correios API.

        .. note::
            We use the POST method instead of the XML, because the POST is the only one that actually returns
            everything we need

        :return: A list with the results of the API, where each item is a different requested service
        """
        self.__setup()
        r = requests.post(self.__url, data=self.__payload)
        ret_dict = xmltodict.parse(r.text)
        result_values = ret_dict['cResultado']['Servicos']['cServico']
        result = []
        for res in result_values:
            result.append(
                {
                    'service': options.Service(res['Codigo']).name,
                    'delivery_time': int(res['PrazoEntrega']),
                    'value': float(res['Valor'].replace(',', '.')),
                    'value_by_own_hand': float(res['ValorMaoPropria'].replace(',', '.')),
                    'value_receiving_warning': float(res['ValorAvisoRecebimento'].replace(',', '.')),
                    'value_declared_value': float(res['ValorValorDeclarado'].replace(',', '.')),
                    'delivery': str(res['EntregaDomiciliar']),
                    'delivery_saturday': True if res['EntregaSabado'] == 'S' else False,
                    'error_code': int(res['Erro']),
                    'error_msg': str(res['MsgErro'])
                }
            )
        return result

    @staticmethod
    def get_estimated_delivery_day(add_days: int = 0, travel_days: int = 1, deliver_on_saturday: bool = False):
        """
        Returns an estimated delivery day. This assumes that the post office is working normally on saturdays.

        :param add_days: The amount of days YOU'LL need to post the object
        :param travel_days: How many travel days we need
        :param deliver_on_saturday: Is it possible to deliver on a saturday
        :return: A datetime object with the expected delivery day
        """
        today = datetime.today()
        ship_date = today + timedelta(days=add_days)
        if ship_date.weekday() > 5:  # If the ship day is saturday, we can ship it (post office works on saturday)
            ship_date = ship_date + timedelta(days=1)  # Otherwise add one day (skip the sunday)
        delivery_date = ship_date + timedelta(days=travel_days)
        delivery_day = delivery_date.weekday()
        if deliver_on_saturday:
            if delivery_day == 6:
                delivery_date = delivery_date + timedelta(days=1)
        else:
            if delivery_day >= 5:
                missing_days = 6 - delivery_day + 1
                delivery_date = delivery_date + timedelta(days=missing_days)
        return delivery_date
