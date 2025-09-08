/** @odoo-module */
// Working POS Customer Display
// File: static/src/js/pos_customer_display.js

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { useState, onMounted } from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.customerInfo = useState({ data: null, loading: false });
        
        // Load customer info when screen loads
        onMounted(() => {
            this.loadCustomerInfo();
        });
    },

    async loadCustomerInfo() {
        const partner = this.currentOrder.get_partner();
        if (!partner) {
            this.customerInfo.data = null;
            return;
        }

        this.customerInfo.loading = true;
        
        try {
            // Load additional customer data
            const result = await this.env.services.orm.read(
                "res.partner",
                [partner.id],
                [
                    'name', 'phone', 'mobile', 'family_number', 
                    'total_due', 'number_of_expired_days', 'status',
                    'category_id', 'area_name_id'
                ]
            );

            if (result && result.length > 0) {
                const data = result[0];
                this.customerInfo.data = {
                    name: data.name || 'غير محدد',
                    phone: data.phone || '',
                    mobile: data.mobile || '',
                    family_number: data.family_number || '',
                    balance: data.total_due || 0,
                    remaining_days: data.number_of_expired_days || 0,
                    status: data.status || 'active',
                    region: this.getAreaName(data.area_name_id),
                    categories: this.getCategories(data.category_id)
                };
            }
        } catch (error) {
            console.log('Error loading customer info:', error);
            // Use basic partner data as fallback
            this.customerInfo.data = {
                name: partner.name || 'غير محدد',
                phone: partner.phone || '',
                mobile: partner.mobile || '',
                family_number: '',
                balance: 0,
                remaining_days: 0,
                status: 'active',
                region: '',
                categories: ''
            };
        }
        
        this.customerInfo.loading = false;
    },

    getAreaName(area) {
        if (!area) return '';
        if (Array.isArray(area) && area.length > 1) return area[1];
        return area.name || area || '';
    },

    getCategories(categories) {
        if (!categories || categories.length === 0) return '';
        return categories.map(cat => Array.isArray(cat) ? cat[1] : cat.name || cat).join(', ');
    },

    formatCurrency(amount) {
        return this.env.utils.formatCurrency(amount || 0);
    },

    formatDays(days) {
        if (!days || days <= 0) return 'منتهي الصلاحية';
        if (days === 1) return 'يوم واحد متبقي';
        if (days === 2) return 'يومان متبقيان';
        if (days <= 10) return `${days} أيام متبقية`;
        return `${days} يوم متبقي`;
    },

    getStatusClass(status) {
        return status === 'active' ? 'text-success' : 'text-danger';
    },

    getStatusText(status) {
        return status === 'active' ? 'نشط' : 'منتهي الصلاحية';
    },

    // Override selectPartner to reload customer info when partner changes
    async selectPartner() {
        await super.selectPartner();
        await this.loadCustomerInfo();
    }
});