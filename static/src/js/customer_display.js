/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    
    // Add customer info display to payment screen
    get customerDisplayInfo() {
        const partner = this.currentOrder.get_partner();
        if (!partner) return null;
        
        return {
            // Arabic name
            name: partner.name || 'غير محدد',
            
            // Phone numbers  
            phone: partner.phone || '',
            mobile: partner.mobile || '',
            
            // Family number
            family_number: partner.family_number || '',
            
            // Prepaid balance (total due)
            balance: this.formatCurrency(partner.total_due || 0),
            
            // Remaining days
            remaining_days: this.formatDays(partner.number_of_expired_days || 0),
            
            // Status
            status: partner.status === 'active' ? 'نشط' : 'منتهي الصلاحية',
            status_class: partner.status === 'active' ? 'success' : 'danger',
            
            // Category tags
            categories: this.formatCategories(partner.category_id || []),
            
            // Region name
            region: this.getRegionName(partner.area_name_id),
        };
    },
    
    formatDays(days) {
        if (days <= 0) return 'منتهي الصلاحية';
        return `${days} يوم متبقي`;
    },
    
    formatCategories(categories) {
        if (!categories || categories.length === 0) return '';
        return categories.map(cat => cat.name || cat).join(', ');
    },
    
    getRegionName(area) {
        if (!area) return '';
        // Handle [id, name] format
        if (Array.isArray(area) && area.length > 1) return area[1];
        return area.name || area;
    }
});