from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """Override to add quantity validation before transfer"""
        self._validate_transfer_quantities()
        return super().button_validate()
    
    def _validate_transfer_quantities(self):
        """Validate all move quantities before confirming transfer"""
        for picking in self:
            if picking.picking_type_id.code == 'outgoing':
                for move in picking.move_ids:
                    if move.product_uom_qty > 0:
                        available_qty = move._get_available_quantity_at_location(
                            move.product_id,
                            move.location_id
                        )
                        
                        if move.product_uom_qty > available_qty:
                            raise ValidationError(_(
                                'Transfer validation failed for "%s".\n'
                                'Requested: %s %s\n'
                                'Available: %s %s\n'
                                'Location: %s'
                            ) % (
                                move.product_id.display_name,
                                move.product_uom_qty,
                                move.product_uom.name,
                                available_qty,
                                move.product_uom.name,
                                move.location_id.display_name
                            ))
    
    @api.constrains('state')
    def _check_transfer_permissions(self):
        """Check if user has permission to validate transfers"""
        for picking in self:
            if picking.state == 'done' and picking.picking_type_id.code == 'outgoing':
                # Use your module's technical name
                if not self.env.user.has_group('new_modules_customization.group_inventory_transfer_manager'):
                    raise ValidationError(_(
                        'You do not have permission to validate inventory transfers. '
                        'Please contact your administrator.'
                    ))