import enum


class Service(enum.Enum):
    SEDEX_RETAIL = '40010'
    SEDEX_TO_CHARGE = '40045'
    SEDEX_10_RETAIL = '40215'
    SEDEX_TODAY_RETAIL = '40290'
    SEDEX_CASH = '4014'
    SEDEX_PAYMENT_ON_DELIVERY = '4065'
    PAC_RETAIL = '41106'
    PAC_CASH = '4510'
    PAC_PAYMENT_ON_DELIVERY = '4707'
    SEDEX_12 = '40169'


class ObjectType(enum.Enum):
    BOX = 1
    ROLL = 2
    LETTER = 3
