from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """Override to add quantity validation before transfer"""
        _logger.info("=== STOCK PICKING VALIDATION START ===")
        _logger.info(f"Picking ID: {self.id}, Name: {self.name}, Type: {self.picking_type_id.name}")
        _logger.info(f"User: {self.env.user.name} (ID: {self.env.user.id})")
        _logger.info(f"Number of moves: {len(self.move_ids)}")
        
        try:
            self._validate_transfer_quantities()
            _logger.info("Quantity validation passed successfully")
            
            result = super().button_validate()
            _logger.info("Transfer validation completed successfully")
            return result
            
        except ValidationError as e:
            _logger.error(f"Validation failed: {str(e)}")
            raise
        except Exception as e:
            _logger.error(f"Unexpected error during validation: {str(e)}")
            raise
    
    def _validate_transfer_quantities(self):
        """Validate all move quantities before confirming transfer"""
        _logger.info("--- Starting transfer quantity validation ---")
        
        for picking in self:
            _logger.info(f"Validating picking: {picking.name} (Type: {picking.picking_type_id.code})")
            
            if picking.picking_type_id.code == 'outgoing':
                _logger.info("Processing outgoing transfer - checking quantities")
                
                for move_index, move in enumerate(picking.move_ids, 1):
                    _logger.info(f"Move {move_index}/{len(picking.move_ids)}: {move.product_id.name}")
                    _logger.info(f"  - Requested quantity: {move.product_uom_qty} {move.product_uom.name}")
                    _logger.info(f"  - Source location: {move.location_id.display_name}")
                    
                    if move.product_uom_qty > 0:
                        try:
                            available_qty = move._get_available_quantity_at_location(
                                move.product_id,
                                move.location_id
                            )
                            
                            _logger.info(f"  - Available quantity: {available_qty} {move.product_uom.name}")
                            
                            if move.product_uom_qty > available_qty:
                                error_msg = (
                                    f'Transfer validation failed for "{move.product_id.display_name}".\n'
                                    f'Requested: {move.product_uom_qty} {move.product_uom.name}\n'
                                    f'Available: {available_qty} {move.product_uom.name}\n'
                                    f'Location: {move.location_id.display_name}'
                                )
                                _logger.error(f"VALIDATION FAILED: {error_msg}")
                                raise ValidationError(_(error_msg))
                            else:
                                _logger.info(f"  - ✓ Quantity check passed")
                        except Exception as e:
                            _logger.error(f"Error checking available quantity for move {move.id}: {str(e)}")
                            raise
                    else:
                        _logger.warning(f"  - Skipping move with zero quantity")
            else:
                _logger.info(f"Skipping validation for non-outgoing transfer: {picking.picking_type_id.code}")
        
        _logger.info("--- Transfer quantity validation completed ---")
    
    @api.constrains('state')
    def _check_transfer_permissions(self):
        """Check if user has permission to validate transfers"""
        _logger.info("=== CHECKING TRANSFER PERMISSIONS ===")
        
        for picking in self:
            _logger.info(f"Checking permissions for picking: {picking.name} (State: {picking.state})")
            
            if picking.state == 'done' and picking.picking_type_id.code == 'outgoing':
                user = self.env.user
                _logger.info(f"User: {user.name} (ID: {user.id})")
                
                # Check if user has the required group
                has_permission = user.has_group('new_modules_customization.group_inventory_transfer_manager')
                _logger.info(f"Has transfer manager permission: {has_permission}")
                
                if not has_permission:
                    # Log user's current groups for debugging
                    user_groups = user.groups_id.mapped('name')
                    _logger.warning(f"User groups: {user_groups}")
                    
                    error_msg = (
                        'You do not have permission to validate inventory transfers. '
                        'Please contact your administrator.'
                    )
                    _logger.error(f"PERMISSION DENIED: {error_msg}")
                    raise ValidationError(_(error_msg))
                else:
                    _logger.info("✓ Transfer permission check passed")
            else:
                _logger.info(f"Permission check skipped - State: {picking.state}, Type: {picking.picking_type_id.code}")
        
        _logger.info("=== TRANSFER PERMISSIONS CHECK COMPLETED ===")
        
    # @api.onchange('picking_type_id')
    # def _onchange_picking_type_id(self):
    #     res = super()._onchange_picking_type_id()
    #     if not res:
    #         res = {}
        
    #     if self.picking_type_id and self.picking_type_id.code == 'internal':
    #         domain = [
    #             ('usage', 'in', ['internal', 'view']),
    #             ('name', 'not ilike', 'Partners')
    #         ]
            
    #         if 'domain' not in res:
    #             res['domain'] = {}
            
    #         res['domain']['location_dest_id'] = domain
    #         res['domain']['location_id'] = domain
        
    #     return res
    
    def _get_internal_locations_domain(self):
        return [
            ('usage', 'in', ['internal', 'view']),
            ('name', 'not ilike', 'Partners'),
            ('name', 'not ilike', 'Customer'),
            ('name', 'not ilike', 'Vendor')
        ]
    
    location_dest_id = fields.Many2one(
        domain=lambda self: self._get_internal_locations_domain()
    )