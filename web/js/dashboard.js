/* ==========================================
   DASHBOARD MODULE
   Dashboard-specific functionality
   ========================================== */

const Dashboard = {
    init() {
        console.log('Dashboard module initialized');
        // Dashboard-specific initialization code can go here
    },

    // Any dashboard-specific functions can be added here
    updateMarketOverview() {
        // This function could be called from the main app
        console.log('Updating market overview...');
    },

    refreshData() {
        console.log('Refreshing dashboard data...');
    }
};

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});

// Export for global access
window.Dashboard = Dashboard; 