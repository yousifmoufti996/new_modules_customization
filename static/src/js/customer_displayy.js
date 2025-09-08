/** @odoo-module */
// Step 2: Simple customer display widget for POS - load data via ORM
// File: static/src/js/customer_display.js

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    
    // Get customer info with additional fields
    async getCustomerDisplayInfo() {
        const partner = this.currentOrder.get_partner();
        if (!partner) return null;
        
        // Load additional customer fields via ORM
        try {
            const customerData = await this.env.services.orm.read(
                "res.partner",
                [partner.id],
                [
                    'name', 'phone', 'mobile', 'family_number', 
                    'total_due', 'number_of_expired_days', 'status',
                    'category_id', 'menu_type_ids', 'area_name_id', 'area_number_id'
                ]
            );
            
            if (customerData && customerData.length > 0) {
                const data = customerData[0];
                return {
                    // Arabic name
                    name: data.name || 'غير محدد',
                    
                    // Phone numbers  
                    phone: data.phone || '',
                    mobile: data.mobile || '',
                    
                    // Family number
                    family_number: data.family_number || '',
                    
                    // Prepaid balance (total due)
                    balance: this.formatCurrency(data.total_due || 0),
                    
                    // Remaining days
                    remaining_days: this.formatDays(data.number_of_expired_days || 0),
                    
                    // Status
                    status: data.status === 'active' ? 'نشط' : 'منتهي الصلاحية',
                    status_class: data.status === 'active' ? 'success' : 'danger',
                    
                    // Category tags
                    categories: this.formatCategories(data.category_id || []),
                    
                    // Region name
                    region: this.getRegionName(data.area_name_id),
                };
            }
        } catch (error) {
            console.log('Error loading customer data:', error);
        }
        
        // Fallback to basic partner data
        return {
            name: partner.name || 'غير محدد',
            phone: partner.phone || '',
            mobile: partner.mobile || '',
            family_number: '',
            balance: '0.00',
            remaining_days: 'غير محدد',
            status: 'غير معروف',
            status_class: 'secondary',
            categories: '',
            region: '',
        };
    },
    
    formatDays(days) {
        if (days <= 0) return 'منتهي الصلاحية';
        return `${days} يوم متبقي`;
    },
    
    formatCategories(categories) {
        if (!categories || categories.length === 0) return '';
        return categories.map(cat => cat[1] || cat).join(', ');
    },
    
    getRegionName(area) {
        if (!area) return '';
        // Handle [id, name] format
        if (Array.isArray(area) && area.length > 1) return area[1];
        return area.name || area;
    }
});