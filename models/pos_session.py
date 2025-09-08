# from odoo import models

# class PosSession(models.Model):
#     _inherit = 'pos.session'

#     def _get_pos_ui_res_partner(self, params):
#         # Get the default partner fields first
#         result = super()._get_pos_ui_res_partner(params)
        
#         # Add our custom fields to the existing fields list
#         additional_fields = [
#             'family_number',             # Family number (الرقم العائلي)
#             'total_due',                 # Prepaid balance (الرصيد المستحق)
#             'number_of_expired_days',    # Remaining days (الأيام المتبقية)
#             'status',                    # Status (حالة الاشتراك)
#             'category_id',               # Category tags (نوع الاشتراك)
#             'menu_type_ids',             # Customer group (مجموعة العملاء)
#             'area_name_id',              # Region name (اسم المنطقة)
#             'area_number_id',            # Area number (رقم المنطقة)
#         ]
        
#         # Extend the fields in the result
#         if 'fields' in result:
#             result['fields'].extend(additional_fields)
        
#         return result