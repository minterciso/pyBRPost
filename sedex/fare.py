import requests
import xmltodict
from datetime import datetime, timedelta
import sedex.options as options


class Fare:
    def __init__(self):
        self.dimensions = {
            'weight': 0.0,
            'length': 0.0,
            'height': 0.0,
            'width': 0.0,
            'diameter': 0.0
        }
        self.cepOrigin = ''
        self.cepDestination = ''
        self.value = 0.0
        self.extras = {
            'receiving_warning': False,
            'by_own_hand': False
        }
        self.package_format = options.ObjectType.BOX
        self.request_services = []
        self.__payload = {}
        self.__url = 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx/CalcPrecoPrazo'

    def setup(self):
        self.__payload = {
            'nCdEmpresa': '',
            'sDsSenha': '',
            'nCdServico': ','.join([x.value for x in self.request_services]),
            'sCepOrigem': self.cepOrigin,
            'sCepDestino': self.cepDestination,
            'nVlPeso': self.dimensions['weight'],
            'nVlComprimento': self.dimensions['length'],
            'nVlAltura': self.dimensions['height'],
            'nVlLargura': self.dimensions['width'],
            'nVlDiametro': self.dimensions['diameter'],
            'nCdFormato': self.package_format.value,
            'nVlValorDeclarado': self.value,
            'sCdMaoPropria': 'S' if self.extras['by_own_hand'] else 'N',
            'sCdAvisoRecebimento': 'S' if self.extras['receiving_warning'] else 'N'
        }

    def get_fare(self):
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
    def get_estimated_delivery_day(add_days: int = 0, travel_days: int = 1, count_saturday: bool = False):
        today = datetime.today()
        ship_date = today + timedelta(days=add_days)
        if ship_date.weekday() > 5:  # If the ship day is saturday, we can ship it (post office works on saturday)
            ship_date = ship_date + timedelta(days=1)  # Otherwise add one day (skip the sunday)
        delivery_date = ship_date + timedelta(days=travel_days)
        delivery_day = delivery_date.weekday()
        if count_saturday:
            if delivery_day == 6:
                delivery_date = delivery_date + timedelta(days=1)
        else:
            if delivery_day >= 5:
                missing_days = 6 - delivery_day + 1
                delivery_date = delivery_date + timedelta(days=missing_days)
        return delivery_date
