/* ==========================================
   SETTINGS MODULE
   Application settings management
   ========================================== */

const Settings = {
    init() {
        console.log('Settings module initialized');
        this.setupSettingsEventListeners();
    },

    setupSettingsEventListeners() {
        // Additional settings-specific event listeners
        console.log('Setting up settings event listeners...');
    },

    // Settings management functions
    loadSettings() {
        const settings = localStorage.getItem('financeAppSettings');
        return settings ? JSON.parse(settings) : this.getDefaultSettings();
    },

    saveSettings(settings) {
        localStorage.setItem('financeAppSettings', JSON.stringify(settings));
        console.log('Settings saved:', settings);
    },

    getDefaultSettings() {
        return {
            theme: 'dark',
            defaultPeriod: '1M',
            autoRefresh: true,
            refreshInterval: 30000,
            apiKeys: {
                alphaVantage: '',
                finnhub: '',
                sec: ''
            },
            notifications: {
                enabled: true,
                sound: false,
                desktop: true
            },
            display: {
                currency: 'USD',
                timezone: 'America/New_York',
                dateFormat: 'MM/DD/YYYY'
            }
        };
    },

    updateTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        console.log('Theme updated to:', theme);
    },

    validateApiKey(keyType, key) {
        // Basic validation for API keys
        return key && key.length > 10;
    },

    exportSettings() {
        const settings = this.loadSettings();
        const dataStr = JSON.stringify(settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'finance_app_settings.json';
        link.click();
    },

    importSettings(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const settings = JSON.parse(e.target.result);
                this.saveSettings(settings);
                console.log('Settings imported successfully');
            } catch (error) {
                console.error('Error importing settings:', error);
            }
        };
        reader.readAsText(file);
    }
};

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Settings.init();
});

// Export for global access
window.Settings = Settings; 