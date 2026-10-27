from odoo import models, fields, api

class EthiopianTaxBracket(models.Model):
    _name = 'ethiopian.tax.bracket'
    _description = 'Ethiopian Employment Income Tax Brackets'
    _order = 'date_from desc, sequence, lower_bound'

    name = fields.Char(string='Description', required=True)
    date_from = fields.Date(string='Effective From', required=True)
    date_to = fields.Date(string='Effective To')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer(string='Sequence', default=10)
    
    lower_bound = fields.Monetary(string='Lower Bound (ETB)', currency_field='currency_id', required=True)
    upper_bound = fields.Monetary(string='Upper Bound (ETB)', currency_field='currency_id')
    tax_rate = fields.Float(string='Tax Rate (%)', required=True)
    deduction_amount = fields.Monetary(string='Constant Deduction (ETB)', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', readonly=True)

    @api.model
    def compute_income_tax(self, amount, company_id, date=None):
        if not date:
            date = fields.Date.today()
        bracket = self.search([
            ('company_id', '=', company_id),
            ('date_from', '<=', date),
            '|', ('date_to', '>=', date), ('date_to', '=', False),
            ('lower_bound', '<=', amount),
            '|', ('upper_bound', '>=', amount), ('upper_bound', '=', False)
        ], limit=1)
        
        if not bracket:
            return 0.0
        tax = (amount * (bracket.tax_rate / 100.0)) - bracket.deduction_amount
        return max(tax, 0.0)