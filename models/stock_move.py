from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.constrains('product_uom_qty')
    def _check_available_quantity(self):
        """Validate that transfer quantity doesn't exceed available quantity"""
        for move in self:
            if move.picking_type_id.code == 'outgoing':  # Only for outgoing transfers
                # Get available quantity at source location
                available_qty = self._get_available_quantity_at_location(
                    move.product_id, 
                    move.location_id
                )
                
                if move.product_uom_qty > available_qty:
                    raise ValidationError(_(
                        'Cannot transfer %s %s of product "%s" from location "%s". '
                        'Only %s available in stock.'
                    ) % (
                        move.product_uom_qty,
                        move.product_uom.name,
                        move.product_id.display_name,
                        move.location_id.display_name,
                        available_qty
                    ))
                    
    def _get_available_quantity_at_location(self, product, location):
        """Calculate available quantity for product at specific location"""
        # Get current quantity on hand
        quants = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id)
        ])
        
        current_qty = sum(quants.mapped('quantity'))
        
        # Subtract quantities from pending outgoing moves
        pending_out_moves = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
            ('state', 'in', ['waiting', 'confirmed', 'assigned']),
            ('picking_type_id.code', '=', 'outgoing'),
            ('id', '!=', self.id)  # Exclude current move
        ])
        
        pending_out_qty = sum(pending_out_moves.mapped('product_uom_qty'))
        
        return current_qty - pending_out_qty