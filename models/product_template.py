from odoo import models, fields




class ProductTemplateAutoTrack(models.Model):
    _inherit = 'product.template'
    
    def _setup_fields(self):
        """Automatically add tracking=True to all fields"""
        super()._setup_fields()
        
        # Fields to exclude from tracking (system/computed/related fields)
        exclude_fields = {
            # System fields
            'id', 'create_date', 'create_uid', 'write_date', 'write_uid', 
            '__last_update', 'display_name',
            
            # Message/chatter fields
            'message_ids', 'message_follower_ids', 'message_partner_ids', 
            'message_channel_ids', 'message_unread', 'message_unread_counter', 
            'message_needaction', 'message_needaction_counter', 'message_has_error', 
            'message_has_error_counter', 'message_has_sms_error', 'message_has_whatsapp_error',
            'message_attachment_count', 'website_message_ids', 'message_is_follower',
            'has_message',
            
            # Activity fields
            'activity_ids', 'activity_state', 'activity_user_id', 'activity_type_id', 
            'activity_summary', 'activity_date_deadline', 'my_activity_date_deadline', 
            'activity_exception_decoration', 'activity_exception_icon', 
            'activity_calendar_event_id', 'activity_type_icon',
            
            # Computed quantity fields
            'qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty',
            'forecasted_qty', 'free_qty', 'nbr_moves_in', 'nbr_moves_out',
            
            # Computed count fields
            'bom_count', 'product_variant_count', 'pricelist_item_count',
            'product_document_count', 'sales_count', 'purchased_product_qty',
            'mrp_product_qty', 'nbr_reordering_rules', 'used_in_bom_count',
            'reordering_min_qty', 'reordering_max_qty',
            
            # Related/computed display fields
            'uom_name', 'weight_uom_name', 'volume_uom_name', 'currency_id',
            'cost_currency_id', 'tax_string', 'product_tooltip', 'expense_policy_tooltip',
            'fiscal_country_codes',
            
            # Boolean computed fields
            'can_image_1024_be_zoomed', 'has_configurable_attributes', 'is_product_variant',
            'has_available_route_ids', 'show_on_hand_qty_status_button', 
            'show_forecasted_qty_status_button', 'visible_expense_policy', 'is_kits',
            
            # Related route fields
            'route_from_categ_ids',
            
            # Property fields (these are stored but better handled manually)
            'property_account_expense_id', 'property_account_income_id',
            'property_account_creditor_price_difference', 'property_stock_inventory',
            'property_stock_production',
            
            # Computed selection fields
            'cost_method', 'valuation', 'service_policy', 'service_to_purchase',
            
            # Image fields (usually too verbose for tracking)
            'image_1920', 'image_1024', 'image_512', 'image_256', 'image_128',
            
            # One2many fields that are better tracked on the related model
            'product_variant_ids', 'attribute_line_ids', 'packaging_ids',
            'seller_ids', 'variant_seller_ids', 'bom_ids', 'bom_line_ids',
            'product_document_ids', 'rating_ids', 'expiration_ids',
            
            # Valid attribute lines (computed)
            'valid_product_template_attribute_line_ids',
        }
        
        # Add tracking to all non-excluded fields
        for field_name, field in self._fields.items():
            if (field_name not in exclude_fields and 
                not field.compute and  # Skip computed fields
                not field.related and  # Skip related fields
                field.store):  # Only stored fields
                
                field.tracking = True