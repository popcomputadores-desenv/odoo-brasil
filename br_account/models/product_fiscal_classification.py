# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.addons.br_account.models.cst import CST_IPI


class ProductFiscalClassification(models.Model):
    _name = 'product.fiscal.classification'
    _description = u'Classificações Fiscais (NCM)'

    code = fields.Char(string=u"Código", size=14)
    name = fields.Char(string="Nome", size=200)
    company_id = fields.Many2one('res.company', string="Empresa")
    type = fields.Selection([('view', u'Visão'),
                             ('normal', 'Normal'),
                             ('extension', u'Extensão')], 'Tipo')
    parent_id = fields.Many2one('product.fiscal.classification', string="Pai")
    cest = fields.Char(string="CEST", size=10,
                       help="Código Especificador da Substituição Tributária")
    federal_nacional = fields.Float(u'Imposto Fed. Sobre Produto Nacional')
    federal_importado = fields.Float(u'Imposto Fed. Sobre Produto Importado')
    estadual_imposto = fields.Float(u'Imposto Estadual')
    municipal_imposto = fields.Float(u'Imposto Municipal')

    # IPI
    classe_enquadramento = fields.Char(string="Classe Enquadr.", size=5)
    codigo_enquadramento = fields.Char(
        string="Cód. Enquadramento", size=3, default='999')
    tax_ipi_id = fields.Many2one('account.tax', string="Alíquota IPI",
                                 domain=[('domain', '=', 'ipi')])
    ipi_tipo = fields.Selection(
        [('percent', 'Percentual')],
        'Tipo do IPI', required=True, default='percent')
    ipi_reducao_bc = fields.Float(
        '% Redução Base', required=True, digits=dp.get_precision('Account'),
        default=0.00)
    ipi_cst = fields.Selection(CST_IPI, string='CST IPI')

    # ICMS ST
    tax_icms_st_id = fields.Many2one('account.tax', string="Alíquota ICMS ST",
                                     domain=[('domain', '=', 'icmsst')])
    icms_st_aliquota_reducao_base = fields.Float(
        '% Red. Base ST',
        digits=dp.get_precision('Discount'))
    icms_st_aliquota_mva = fields.Float(
        'MVA Ajustado ST',
        digits=dp.get_precision('Discount'), default=0.00)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" % (rec.code, rec.name or '')))
        return result
