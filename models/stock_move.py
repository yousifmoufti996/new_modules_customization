from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.constrains('product_uom_qty')
    def _check_available_quantity(self):
        """Validate that transfer quantity doesn't exceed available quantity"""
        _logger.info("=== STOCK MOVE QUANTITY VALIDATION ===")
        
        for move in self:
            _logger.info(f"Validating move ID: {move.id}")
            _logger.info(f"Product: {move.product_id.name} (ID: {move.product_id.id})")
            _logger.info(f"Requested quantity: {move.product_uom_qty} {move.product_uom.name}")
            _logger.info(f"Move state: {move.state}")
            _logger.info(f"Picking type: {move.picking_type_id.code if move.picking_type_id else 'No picking type'}")
            
            if move.picking_type_id and move.picking_type_id.code == 'outgoing':
                _logger.info("Processing outgoing move - checking available quantity")
                
                try:
                    # Get available quantity at source location
                    available_qty = self._get_available_quantity_at_location(
                        move.product_id, 
                        move.location_id
                    )
                    
                    _logger.info(f"Available quantity calculated: {available_qty}")
                    
                    if move.product_uom_qty > available_qty:
                        error_msg = (
                            f'Cannot transfer {move.product_uom_qty} {move.product_uom.name} '
                            f'of product "{move.product_id.display_name}" '
                            f'from location "{move.location_id.display_name}". '
                            f'Only {available_qty} available in stock.'
                        )
                        _logger.error(f"QUANTITY VALIDATION FAILED: {error_msg}")
                        raise ValidationError(_(error_msg))
                    else:
                        _logger.info("✓ Quantity validation passed")
                        
                except Exception as e:
                    _logger.error(f"Error during quantity validation: {str(e)}")
                    raise
            else:
                _logger.info("Skipping validation - not an outgoing move")
                    
    def _get_available_quantity_at_location(self, product, location):
        """Calculate available quantity for product at specific location"""
        _logger.info(f"--- Calculating available quantity ---")
        _logger.info(f"Product: {product.name} (ID: {product.id})")
        _logger.info(f"Location: {location.display_name} (ID: {location.id})")
        
        try:
            # Get current quantity on hand
            quants = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id)
            ])
            
            _logger.info(f"Found {len(quants)} quant records")
            
            current_qty = 0
            for quant in quants:
                _logger.info(f"  Quant ID {quant.id}: quantity = {quant.quantity}")
                current_qty += quant.quantity
            
            _logger.info(f"Total current quantity: {current_qty}")
            
            # Subtract quantities from pending outgoing moves
            pending_out_moves = self.env['stock.move'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('picking_type_id.code', '=', 'outgoing'),
                ('id', '!=', self.id)  # Exclude current move
            ])
            
            _logger.info(f"Found {len(pending_out_moves)} pending outgoing moves")
            
            pending_out_qty = 0
            for pending_move in pending_out_moves:
                _logger.info(f"  Pending move ID {pending_move.id}: {pending_move.product_uom_qty} {pending_move.product_uom.name}")
                pending_out_qty += pending_move.product_uom_qty
            
            _logger.info(f"Total pending outgoing quantity: {pending_out_qty}")
            
            available_qty = current_qty - pending_out_qty
            _logger.info(f"Final available quantity: {available_qty} ({current_qty} - {pending_out_qty})")
            
            return available_qty
            
        except Exception as e:
            _logger.error(f"Error calculating available quantity: {str(e)}")
            _logger.error(f"Product ID: {product.id}, Location ID: {location.id}")
            raise

    # Optional: Add logging to standard move methods for better tracking
    def _action_confirm(self, merge=True, merge_into=False):
        """Add logging to move confirmation"""
        _logger.info(f"=== CONFIRMING STOCK MOVE ===")
        for move in self:
            _logger.info(f"Confirming move: {move.product_id.name}, Qty: {move.product_uom_qty}")
        
        result = super()._action_confirm(merge=merge, merge_into=merge_into)
        _logger.info("Move confirmation completed")
        return result
    
    def _action_assign(self):
        """Add logging to move assignment"""
        _logger.info(f"=== ASSIGNING STOCK MOVE ===")
        for move in self:
            _logger.info(f"Assigning move: {move.product_id.name}, State: {move.state}")
        
        result = super()._action_assign()
        _logger.info("Move assignment completed")
        return result
    
    def _action_done(self, cancel_backorder=False):
        """Add logging to move completion"""
        _logger.info(f"=== COMPLETING STOCK MOVE ===")
        for move in self:
            _logger.info(f"Completing move: {move.product_id.name}, Final qty: {move.product_uom_qty}")
        
        result = super()._action_done(cancel_backorder=cancel_backorder)
        _logger.info("Move completion done")
        return result