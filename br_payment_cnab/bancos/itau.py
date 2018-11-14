from ..serialize.cnab240 import Cnab_240
import time
import logging
_logger = logging.getLogger(__name__)

try:
    from pycnab240.utils import get_tipo_de_servico
    from pycnab240.utils import get_ted_doc_finality
    from pycnab240.bancos import itau
except ImportError:
    _logger.error('Cannot import from pycnab240', exc_info=True)


class Itau240(Cnab_240):
    def __init__(self, pay_order):
        self._bank = itau
        self._order = pay_order
        super(Itau240, self).__init__()

    def segments_per_operation(self):
        return {  # TODO: SEGMENTOS DE TITULOS E TRIBUTOS
            "41": ["SegmentoA_outros_bancos", "SegmentoB"],  # TED - outros
            "03": ["SegmentoA_outros_bancos", "SegmentoB"],  # DOC - outros
            "31": ["SegmentoJ", "SegmentoJ52"],              # Títulos
            "91": ["SegmentoO"],                             # Barcode
            "17": ["SegmentoN_GPS", "SegmentoB"],            # GPS
            "16": ["SegmentoN_DarfNormal", "SegmentoB"],     # DARF normal
            "18": ["SegmentoN_DarfSimples", "SegmentoB"],    # DARF simples
            "35": ["SegmentoN_FGTS", "SegmentoB"],           # FGTS
            "22": ["SegmentoN_GareSP", "SegmentoB"],         # ICMS
            "06": ["SegmentoA_Itau_Unibanco", "SegmentoB"],  # CC - mesmo
            "07": ["SegmentoA_outros_bancos", "SegmentoB"],  # DOC - mesmo
            "43": ["SegmentoA_outros_bancos", "SegmentoB"],  # TED - mesmo
            "01": ["SegmentoA_Itau_Unibanco", "SegmentoB"],  # CC - outros
            }

    def _hour_now(self):
        return (int(time.strftime("%H%M%S")))

    def _get_header_arq(self):
        header = super(Itau240, self)._get_header_arq()

        header.update({
            'cedente_agencia': self._string_to_num(
                header.get('cedente_agencia')),
            'cedente_agencia_dv': header.get('cedente_agencia_dv') or '',
            'cedente_conta': self._string_to_num(header.get('cedente_conta')),
            'cedente_conta_dv': '0',
            'dac': self._string_to_num(header.get('cedente_conta_dv'))
        })
        return header

    def _get_header_lot(self, line, num_lot, lot):
        info_id = line.payment_information_id
        header = super(Itau240, self)._get_header_lot(line, num_lot)
        header.update({
            'tipo_pagamento': int(
                get_tipo_de_servico('itau', info_id.service_type)),
            'cedente_agencia': int(header.get('cedente_agencia')),
            'cedente_conta': self._string_to_num(header.get('cedente_conta')),
            'cedente_conta_dv': '0',
            'dac': self._string_to_num(header.get('cedente_conta_dv')),
            'cedente_cep': self._string_to_num(header.get('cedente_cep')),
        })
        return header

    def _get_segmento(self, line, lot_sequency, num_lot):
        segmento = super(Itau240, self)._get_segmento(
            line, lot_sequency, num_lot)

        if not segmento.get('favorecido_cidade'):
            segmento.update({'favorecido_cidade': ''})  # Verificar se isso
            # deve existir mesmo. Talvez tratar o erro da cidade faltando,
            # pro caso de obrigatoriedade desse campo
        del(segmento['codigo_camara_compensacao'])
        segmento.update({
            'tipo_movimento': int(segmento.get('tipo_movimento')),
            'favorecido_endereco_rua':
                segmento.get('favorecido_endereco_rua')[:30],
            'favorecido_bairro':
                segmento.get('favorecido_bairro')[:15] if segmento.get(
                    'favorecido_bairro') else '',
            'favorecido_endereco_complemento': str(
                segmento.get('favorecido_endereco_complemento'))[:15],
            'favorecido_nome': segmento.get('favorecido_nome')[:30],
            'numero_documento_cliente': str(
                segmento.get('numero_documento_cliente')),
            'favorecido_conta': self._string_to_num(
                segmento.get('favorecido_conta'), 0),
            'favorecido_agencia': self._string_to_num(
                segmento.get('favorecido_agencia'), 0),
            'valor_real_pagamento': self._string_to_monetary(
                segmento.get('valor_real_pagamento')),
            'favorecido_banco': int(line.bank_account_id.bank_id.bic),
            'finalidade_doc_ted': get_ted_doc_finality(
                'itau', line.payment_information_id.payment_type,
                segmento.get('finalidade_doc_ted'))
        })
        return segmento

    def _get_trailer_lot(self, total, num_lot):
        trailer = super(Itau240, self)._get_trailer_lot(total, num_lot)
        trailer.update({
        })
        return trailer

    def _get_trailer_arq(self):
        trailer = super(Itau240, self)._get_trailer_arq()
        trailer.update({
        })
        return trailer