from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class InventoryTransferWizard(models.TransientModel):
    _name = 'inventory.transfer.wizard'
    _description = 'Inventory Transfer Validation Wizard'
    
    picking_id = fields.Many2one('stock.picking', string='Transfer', required=True)
    line_ids = fields.One2many('inventory.transfer.wizard.line', 'wizard_id', string='Products')
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_id'):
            picking = self.env['stock.picking'].browse(self.env.context['active_id'])
            res['picking_id'] = picking.id
            
            lines = []
            for move in picking.move_ids:
                available_qty = move._get_available_quantity_at_location(
                    move.product_id,
                    move.location_id
                )
                lines.append({
                    'product_id': move.product_id.id,
                    'requested_qty': move.product_uom_qty,
                    'available_qty': available_qty,
                    'location_id': move.location_id.id,
                })
            res['line_ids'] = lines
        return res
    
    def action_confirm_transfer(self):
        """Confirm transfer after validation"""
        self._validate_all_quantities()
        self.picking_id.button_validate()
        return {'type': 'ir.actions.act_window_close'}
    
    def _validate_all_quantities(self):
        """Final validation before transfer"""
        for line in self.line_ids:
            if line.requested_qty > line.available_qty:
                raise ValidationError(_(
                    'Insufficient quantity for product "%s".\n'
                    'Requested: %s, Available: %s'
                ) % (line.product_id.display_name, line.requested_qty, line.available_qty))


class InventoryTransferWizardLine(models.TransientModel):
    _name = 'inventory.transfer.wizard.line'
    _description = 'Inventory Transfer Wizard Line'
    
    wizard_id = fields.Many2one('inventory.transfer.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    requested_qty = fields.Float(string='Requested Quantity', readonly=True)
    available_qty = fields.Float(string='Available Quantity', readonly=True)
    location_id = fields.Many2one('stock.location', string='Source Location', readonly=True)
    is_valid = fields.Boolean(string='Valid', compute='_compute_is_valid')
    
    @api.depends('requested_qty', 'available_qty')
    def _compute_is_valid(self):
        for line in self:
            line.is_valid = line.requested_qty <= line.available_qty