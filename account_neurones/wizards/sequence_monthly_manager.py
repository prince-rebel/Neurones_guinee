# -*- coding:utf-8 -*-

from odoo import api, fields, models, exceptions


class SequenceMonthlyManager(models.TransientModel):
    _name = 'sequence.monthly.manager'
    _description = "Sequence mensuelle"

    journal_ids = fields.Many2many('account.journal', 'account_journal_sequence_manager', 'sequence_id', 'journal_id',
                                   'les journaux', required=True)
    start_date = fields.Date('Date de début', required=True)
    end_date = fields.Date('Date de fin', required=True)

    def compute(self):
        for rec in self:
            vals = {
                'date_from': rec.start_date,
                'date_to': rec.end_date,
                'number_next': 1
            }
            datarange_obj = rec.env['ir.sequence.date_range']
            for journal in rec.journal_ids:
                if journal.sequence_id:
                    vals['sequence_id'] = journal.sequence_id.id
                    id = datarange_obj.create(vals)
