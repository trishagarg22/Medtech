// ==========================================================================
// Medtech Dashboard JS - Interactive Frontend Engine
// ==========================================================================

// Global State
let medicinesData = [];
let devicesData = [];
let billingHistory = [];
let draftInvoiceItems = []; // Items in current bill invoice being created
let hasWarnedExpiry = false; // Expiry toast helper
let html5QrcodeScanner = null; // Scanner instance
let scannerTargetInputId = null; // Target field ID for scanned value
let allBillingItems = []; // Auto-suggest catalog cache

// DOM elements
const timeDisplay = document.getElementById('time-display');
const toastContainer = document.getElementById('toast-container');

// Tab Configuration
const tabs = {
    dashboard: {
        btn: document.getElementById('tab-dashboard-btn'),
        section: document.getElementById('section-dashboard'),
        title: 'Dashboard Overview',
        subtitle: 'Welcome back! Here is a summary of Medtech operations.'
    },
    medicines: {
        btn: document.getElementById('tab-medicines-btn'),
        section: document.getElementById('section-medicines'),
        title: 'Medicines Inventory',
        subtitle: 'Manage and search your pharmacy products database.'
    },
    devices: {
        btn: document.getElementById('tab-devices-btn'),
        section: document.getElementById('section-devices'),
        title: 'Healthcare Devices',
        subtitle: 'Track medical equipment stocks, warranties, and prices.'
    },
    billing: {
        btn: document.getElementById('tab-billing-btn'),
        section: document.getElementById('section-billing'),
        title: 'Billing & Invoices',
        subtitle: 'Generate customer receipts and browse sales history.'
    }
};

// --------------------------------------------------------------------------
// Initialization & Events
// --------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    // Start Clock Tick
    setInterval(updateClock, 1000);
    updateClock();

    // Setup Tab Routing
    Object.keys(tabs).forEach(tabKey => {
        tabs[tabKey].btn.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(tabKey);
        });
    });

    // Quick Navigation Buttons on Dashboard
    document.getElementById('quick-bill-btn').addEventListener('click', () => switchTab('billing', 'new'));
    document.getElementById('btn-quick-nav-billing').addEventListener('click', () => switchTab('billing', 'new'));

    // Setup Search & Filters
    document.getElementById('med-search-input').addEventListener('input', filterMedicines);
    document.getElementById('med-stock-filter').addEventListener('change', filterMedicines);
    document.getElementById('med-expiry-check-btn').addEventListener('click', filterExpiringMedicines);
    
    document.getElementById('dev-search-input').addEventListener('input', filterDevices);
    document.getElementById('dev-filter-btn').addEventListener('click', filterDevices);

    // Setup Billing Sub-tabs
    const subtabNewBtn = document.getElementById('billing-subtab-new-btn');
    const subtabHistoryBtn = document.getElementById('billing-subtab-history-btn');
    const subtabNewContent = document.getElementById('billing-subtab-new');
    const subtabHistoryContent = document.getElementById('billing-subtab-history');

    subtabNewBtn.addEventListener('click', () => {
        subtabNewBtn.classList.add('active');
        subtabHistoryBtn.classList.remove('active');
        subtabNewContent.classList.add('active');
        subtabHistoryContent.classList.remove('active');
    });

    subtabHistoryBtn.addEventListener('click', () => {
        subtabHistoryBtn.classList.add('active');
        subtabNewBtn.classList.remove('active');
        subtabHistoryContent.classList.add('active');
        subtabNewContent.classList.remove('active');
        loadBillingHistory();
    });

    // Billing Form: Item Selection change listener
    const itemSelector = document.getElementById('bill-item-selector');
    itemSelector.addEventListener('change', () => {
        const selectedOption = itemSelector.options[itemSelector.selectedIndex];
        if (selectedOption && selectedOption.dataset.price) {
            document.getElementById('bill-item-price').value = selectedOption.dataset.price;
        } else {
            document.getElementById('bill-item-price').value = '';
        }
    });

    // Billing Form: Autocomplete search input listener
    const itemSearchInput = document.getElementById('bill-item-search');
    const suggestionsBox = document.getElementById('bill-item-suggestions');

    itemSearchInput.addEventListener('input', () => {
        const query = itemSearchInput.value.toLowerCase().trim();
        suggestionsBox.innerHTML = '';
        
        if (query.length < 2) {
            suggestionsBox.classList.remove('active');
            return;
        }

        const filtered = allBillingItems.filter(item => 
            item.name.toLowerCase().includes(query)
        );

        if (filtered.length === 0) {
            suggestionsBox.innerHTML = '<div class="suggestion-row" style="color: var(--text-dimmed); font-style: italic;">No items found</div>';
        } else {
            filtered.forEach(item => {
                const row = document.createElement('div');
                row.className = 'suggestion-row';
                
                const typeClass = item.type === 'Medicine' ? 'badge-success' : 'badge-secondary';
                
                row.innerHTML = `
                    <div>
                        <strong>${item.name}</strong> 
                        <span class="badge ${typeClass}" style="margin-left: 6px; font-size: 10px;">${item.type}</span>
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted);">
                        ₹${item.price.toFixed(2)} (Stock: ${item.stock})
                    </div>
                `;
                
                row.addEventListener('click', () => {
                    itemSearchInput.value = item.name;
                    
                    // Select key in hidden selector
                    itemSelector.value = item.key;
                    
                    // Dispatch change event to populate unit price
                    itemSelector.dispatchEvent(new Event('change'));
                    
                    suggestionsBox.classList.remove('active');
                    document.getElementById('bill-item-qty').focus();
                });
                
                suggestionsBox.appendChild(row);
            });
        }
        suggestionsBox.classList.add('active');
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (e.target !== itemSearchInput && e.target !== suggestionsBox && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.remove('active');
        }
    });

    // Show suggestions on focus if query length is >= 2
    itemSearchInput.addEventListener('focus', () => {
        if (itemSearchInput.value.trim().length >= 2) {
            suggestionsBox.classList.add('active');
        }
    });

    // Billing Form: Add Item to Draft
    document.getElementById('add-item-to-list-btn').addEventListener('click', addItemToDraftList);

    // Billing Form: Submit Bill
    document.getElementById('billing-form').addEventListener('submit', submitNewBill);

    // Modals: Forms submit listeners
    document.getElementById('medicine-form').addEventListener('submit', handleMedicineFormSubmit);
    document.getElementById('device-form').addEventListener('submit', handleDeviceFormSubmit);

    // Barcode Scan launchers
    document.getElementById('scan-med-code-btn').addEventListener('click', () => openScanner('med-code'));
    document.getElementById('scan-dev-id-btn').addEventListener('click', () => openScanner('dev-id'));

    // Close modals on Escape key press
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeInvoiceModal();
            closeMedicineModal();
            closeDeviceModal();
            closeScannerModal();
            closeChangePasswordModal();
        }
    });

    // Void / Delete Invoice click handler
    document.getElementById('void-invoice-btn').addEventListener('click', async () => {
        const billId = document.getElementById('inv-bill-id').textContent;
        if (!billId) return;
        
        if (!confirm(`Are you sure you want to void and delete Bill: ${billId}? This will delete the bill and return the stock items to the inventory.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/bills/${billId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                showToast(result.message, 'success');
                closeInvoiceModal();
                
                // Refresh billing records and dashboard statistics
                loadBillingHistory();
                loadMedicines();
                loadDevices();
                loadDashboardStats();
            } else {
                showToast(result.error, 'error');
            }
        } catch (err) {
            showToast('Error voiding/deleting invoice.', 'error');
        }
    });

    // Login form submit trigger
    document.getElementById('login-form').addEventListener('submit', handleLoginFormSubmit);

    // Logout trigger
    document.getElementById('sidebar-logout-btn').addEventListener('click', (e) => {
        e.preventDefault();
        logoutAdmin();
    });

    // Double-click profile footer to show Owner settings
    document.getElementById('user-profile-trigger').addEventListener('dblclick', () => {
        document.getElementById('change-password-modal').classList.add('active');
        document.getElementById('owner-passkey').focus();
    });

    // Form submit listener for Owner settings
    document.getElementById('change-password-form').addEventListener('submit', handleChangePasswordSubmit);

    // Initial Load
    checkLoginSession();
});

// Clock Tick function
function updateClock() {
    const now = new Date();
    timeDisplay.textContent = now.toLocaleTimeString();
}

// Switching Primary Tabs
function switchTab(tabKey, subtab = null) {
    // Update active sidebar nav
    Object.keys(tabs).forEach(key => {
        if (key === tabKey) {
            tabs[key].btn.classList.add('active');
            tabs[key].section.classList.add('active');
        } else {
            tabs[key].btn.classList.remove('active');
            tabs[key].section.classList.remove('active');
        }
    });

    // Update Header Text
    document.getElementById('current-tab-title').textContent = tabs[tabKey].title;
    document.getElementById('current-tab-subtitle').textContent = tabs[tabKey].subtitle;

    // Load data specific to tabs
    if (tabKey === 'dashboard') {
        loadDashboardStats();
    } else if (tabKey === 'medicines') {
        loadMedicines();
    } else if (tabKey === 'devices') {
        loadDevices();
    } else if (tabKey === 'billing') {
        populateBillingItemsDropdown();
        if (subtab === 'new') {
            document.getElementById('billing-subtab-new-btn').click();
        } else {
            loadBillingHistory();
        }
    }
}

// --------------------------------------------------------------------------
// Notification Toasts
// --------------------------------------------------------------------------
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'none';
        toast.offsetHeight; // trigger reflow
        toast.style.transition = 'all 0.3s';
        toast.style.transform = 'translateY(-20px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --------------------------------------------------------------------------
// API Calls & Data Fetching
// --------------------------------------------------------------------------

// 1. Dashboard Stats
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();
        if (result.success) {
            document.getElementById('stat-medicines').textContent = result.medicines;
            document.getElementById('stat-devices').textContent = result.devices;
            document.getElementById('stat-customers').textContent = result.customers;
            document.getElementById('stat-revenue').textContent = `₹${result.revenue.toFixed(2)}`;
            
            // Also load warnings (stock alerts)
            loadDashboardStockAlerts();
        } else {
            showToast(result.error || 'Failed to fetch dashboard statistics.', 'error');
        }
    } catch (e) {
        showToast(e.message || 'Error loading dashboard.', 'error');
    }
}

async function loadDashboardStockAlerts() {
    try {
        const resMed = await fetch('/api/medicines');
        const resDev = await fetch('/api/devices');
        const medResult = await resMed.json();
        const devResult = await resDev.json();

        const alertsContainer = document.getElementById('stock-alerts-list');
        alertsContainer.innerHTML = '';

        let alerts = [];
        let expiredCount = 0;

        if (medResult.success) {
            medResult.data.forEach(med => {
                // Check if expired
                const isExpired = new Date(med.expire_date) < new Date();
                if (isExpired) {
                    alerts.push({ type: 'danger', title: 'Expired Medicine ⚠️', desc: `"${med.med_name}" expired on ${med.expire_date}.` });
                    expiredCount++;
                } else if (med.medstock === 0) {
                    alerts.push({ type: 'danger', title: 'Out of Stock', desc: `Medicine "${med.med_name}" is empty.` });
                } else if (med.medstock <= 20) {
                    alerts.push({ type: 'warning', title: 'Low Stock', desc: `Medicine "${med.med_name}" has ${med.medstock} left.` });
                }
            });

            // Trigger global warning toast once on load
            if (!hasWarnedExpiry && expiredCount > 0) {
                showToast(`Warning: There are ${expiredCount} expired medicine(s) in the database!`, 'error');
                hasWarnedExpiry = true;
            }
        }

        if (devResult.success) {
            devResult.data.forEach(dev => {
                if (dev.stock === 0) {
                    alerts.push({ type: 'danger', title: 'Out of Stock', desc: `Device "${dev.name}" is empty.` });
                } else if (dev.stock <= 5) {
                    alerts.push({ type: 'warning', title: 'Low Stock', desc: `Device "${dev.name}" has ${dev.stock} left.` });
                }
            });
        }

        if (alerts.length === 0) {
            alertsContainer.innerHTML = '<p class="empty-state">✅ All stocks and expiries are healthy.</p>';
        } else {
            alerts.slice(0, 5).forEach(alert => {
                const item = document.createElement('div');
                item.className = `alert-item ${alert.type}`;
                item.innerHTML = `
                    <div class="alert-indicator"></div>
                    <div class="alert-content">
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-desc">${alert.desc}</div>
                    </div>
                `;
                alertsContainer.appendChild(item);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

// 2. Medicines Manager
async function loadMedicines() {
    try {
        const response = await fetch('/api/medicines');
        const result = await response.json();
        if (result.success) {
            medicinesData = result.data;
            renderMedicinesTable(medicinesData);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Error loading medicines list.', 'error');
    }
}

function renderMedicinesTable(data) {
    const tbody = document.getElementById('medicines-table-body');
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="empty-table-text">No medicines found.</td></tr>`;
        return;
    }
    
    data.forEach(med => {
        const tr = document.createElement('tr');
        
        let stockBadgeClass = 'badge-success';
        if (med.medstock === 0) stockBadgeClass = 'badge-danger';
        else if (med.medstock <= 20) stockBadgeClass = 'badge-warning';

        // Check if expired
        const isExpired = new Date(med.expire_date) < new Date();
        const expiryDisplay = isExpired 
            ? `<span class="text-rose font-bold">${med.expire_date} (Expired)</span>` 
            : med.expire_date;

        tr.innerHTML = `
            <td><code>${med.med_code}</code></td>
            <td><strong>${med.med_name}</strong></td>
            <td>${med.manufacturer || '-'}</td>
            <td>${med.dosage_form || '-'}</td>
            <td>${med.category || '-'}</td>
            <td>${expiryDisplay}</td>
            <td>₹${parseFloat(med.price).toFixed(2)}</td>
            <td><span class="badge ${stockBadgeClass}">${med.medstock}</span></td>
            <td>
                <button class="table-action-btn" onclick="openMedicineModal('edit', '${med.med_code}')" title="Edit">✏️</button>
                <button class="table-action-btn" onclick="deleteMedicine('${med.med_code}')" title="Delete">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterMedicines() {
    const query = document.getElementById('med-search-input').value.toLowerCase();
    const stockFilter = document.getElementById('med-stock-filter').value;
    
    let filtered = medicinesData.filter(med => {
        const matchesQuery = 
            med.med_code.toLowerCase().includes(query) ||
            med.med_name.toLowerCase().includes(query) ||
            (med.manufacturer && med.manufacturer.toLowerCase().includes(query)) ||
            (med.category && med.category.toLowerCase().includes(query));
            
        let matchesStock = true;
        if (stockFilter === 'low') {
            matchesStock = med.medstock > 0 && med.medstock <= 20;
        } else if (stockFilter === 'out') {
            matchesStock = med.medstock === 0;
        }
        
        return matchesQuery && matchesStock;
    });
    
    renderMedicinesTable(filtered);
}

function filterExpiringMedicines() {
    // Show medicines expiring in the next 6 months
    const sixMonthsFromNow = new Date();
    sixMonthsFromNow.setMonth(sixMonthsFromNow.getMonth() + 6);
    
    let filtered = medicinesData.filter(med => {
        const expiry = new Date(med.expire_date);
        return expiry <= sixMonthsFromNow;
    });
    
    // Sort by expiry date ascending (soonest first)
    filtered.sort((a, b) => new Date(a.expire_date) - new Date(b.expire_date));
    
    renderMedicinesTable(filtered);
    showToast(`Showing medicines expiring before ${sixMonthsFromNow.toISOString().split('T')[0]}`, 'info');
}

// 3. Healthcare Devices Manager
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        const result = await response.json();
        if (result.success) {
            devicesData = result.data;
            renderDevicesTable(devicesData);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Error loading devices list.', 'error');
    }
}

function renderDevicesTable(data) {
    const tbody = document.getElementById('devices-table-body');
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-table-text">No devices found.</td></tr>`;
        return;
    }
    
    data.forEach(dev => {
        const tr = document.createElement('tr');
        
        let stockBadgeClass = 'badge-success';
        if (dev.stock === 0) stockBadgeClass = 'badge-danger';
        else if (dev.stock <= 5) stockBadgeClass = 'badge-warning';

        tr.innerHTML = `
            <td><code>${dev.machine_id}</code></td>
            <td><strong>${dev.name}</strong></td>
            <td>${dev.Warranty || '-'}</td>
            <td>${dev.manufacturer || '-'}</td>
            <td>${dev.useins || '-'}</td>
            <td>₹${parseFloat(dev.price).toFixed(2)}</td>
            <td><span class="badge ${stockBadgeClass}">${dev.stock}</span></td>
            <td>
                <button class="table-action-btn" onclick="openDeviceModal('edit', '${dev.machine_id}')" title="Edit">✏️</button>
                <button class="table-action-btn" onclick="deleteDevice('${dev.machine_id}')" title="Delete">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterDevices() {
    const query = document.getElementById('dev-search-input').value.toLowerCase();
    const minVal = parseFloat(document.getElementById('dev-price-min').value) || 0;
    const maxVal = parseFloat(document.getElementById('dev-price-max').value) || Infinity;
    
    let filtered = devicesData.filter(dev => {
        const matchesQuery = 
            dev.machine_id.toLowerCase().includes(query) ||
            dev.name.toLowerCase().includes(query) ||
            (dev.manufacturer && dev.manufacturer.toLowerCase().includes(query));
            
        const price = parseFloat(dev.price);
        const matchesPrice = price >= minVal && price <= maxVal;
        
        return matchesQuery && matchesPrice;
    });
    
    renderDevicesTable(filtered);
}

// --------------------------------------------------------------------------
// Medicine Modals Operations (Add/Edit/Delete)
// --------------------------------------------------------------------------
const medicineModal = document.getElementById('medicine-modal');

function openMedicineModal(mode, code = '') {
    const title = document.getElementById('med-modal-title');
    const formMode = document.getElementById('med-form-mode');
    const codeInput = document.getElementById('med-code');
    
    // Clear form
    document.getElementById('medicine-form').reset();
    
    if (mode === 'add') {
        title.textContent = 'Add Medicine';
        formMode.value = 'add';
        codeInput.disabled = false;
    } else {
        title.textContent = 'Edit Medicine';
        formMode.value = 'edit';
        codeInput.disabled = true;
        
        const med = medicinesData.find(m => m.med_code === code);
        if (med) {
            document.getElementById('med-code').value = med.med_code;
            document.getElementById('med-name').value = med.med_name;
            document.getElementById('med-manufacturer').value = med.manufacturer || '';
            document.getElementById('med-dosage').value = med.dosage_form || '';
            document.getElementById('med-category').value = med.category || '';
            document.getElementById('med-expiry').value = med.expire_date;
            document.getElementById('med-price').value = med.price;
            document.getElementById('med-stock').value = med.medstock;
        }
    }
    medicineModal.classList.add('active');
}

function closeMedicineModal() {
    medicineModal.classList.remove('active');
}

async function handleMedicineFormSubmit(e) {
    e.preventDefault();
    const mode = document.getElementById('med-form-mode').value;
    const code = document.getElementById('med-code').value;
    
    const payload = {
        med_code: code,
        med_name: document.getElementById('med-name').value,
        manufacturer: document.getElementById('med-manufacturer').value,
        dosage_form: document.getElementById('med-dosage').value,
        category: document.getElementById('med-category').value,
        expire_date: document.getElementById('med-expiry').value,
        price: parseFloat(document.getElementById('med-price').value),
        medstock: parseInt(document.getElementById('med-stock').value)
    };
    
    try {
        let url = '/api/medicines';
        let method = 'POST';
        
        if (mode === 'edit') {
            url = `/api/medicines/${code}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.success) {
            showToast(result.message || 'Operation successful!', 'success');
            closeMedicineModal();
            loadMedicines();
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error saving medicine record.', 'error');
    }
}

async function deleteMedicine(code) {
    if (!confirm(`Are you sure you want to delete medicine code: ${code}?`)) return;
    try {
        const response = await fetch(`/api/medicines/${code}`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) {
            showToast('Medicine record deleted successfully.', 'success');
            loadMedicines();
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error deleting medicine.', 'error');
    }
}

// --------------------------------------------------------------------------
// Device Modals Operations (Add/Edit/Delete)
// --------------------------------------------------------------------------
const deviceModal = document.getElementById('device-modal');

function openDeviceModal(mode, machineId = '') {
    const title = document.getElementById('dev-modal-title');
    const formMode = document.getElementById('dev-form-mode');
    const idInput = document.getElementById('dev-id');
    
    document.getElementById('device-form').reset();
    
    if (mode === 'add') {
        title.textContent = 'Add Healthcare Device';
        formMode.value = 'add';
        idInput.disabled = false;
    } else {
        title.textContent = 'Edit Healthcare Device';
        formMode.value = 'edit';
        idInput.disabled = true;
        
        const dev = devicesData.find(d => d.machine_id === machineId);
        if (dev) {
            document.getElementById('dev-id').value = dev.machine_id;
            document.getElementById('dev-name').value = dev.name;
            document.getElementById('dev-warranty').value = dev.Warranty || '';
            document.getElementById('dev-manufacturer').value = dev.manufacturer || '';
            document.getElementById('dev-useins').value = dev.useins || '';
            document.getElementById('dev-price').value = dev.price;
            document.getElementById('dev-stock').value = dev.stock;
        }
    }
    deviceModal.classList.add('active');
}

function closeDeviceModal() {
    deviceModal.classList.remove('active');
}

async function handleDeviceFormSubmit(e) {
    e.preventDefault();
    const mode = document.getElementById('dev-form-mode').value;
    const id = document.getElementById('dev-id').value;
    
    const payload = {
        machine_id: id,
        name: document.getElementById('dev-name').value,
        Warranty: document.getElementById('dev-warranty').value,
        manufacturer: document.getElementById('dev-manufacturer').value,
        useins: document.getElementById('dev-useins').value,
        price: parseFloat(document.getElementById('dev-price').value),
        stock: parseInt(document.getElementById('dev-stock').value)
    };
    
    try {
        let url = '/api/devices';
        let method = 'POST';
        
        if (mode === 'edit') {
            url = `/api/devices/${id}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.success) {
            showToast(result.message || 'Operation successful!', 'success');
            closeDeviceModal();
            loadDevices();
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error saving device record.', 'error');
    }
}

async function deleteDevice(id) {
    if (!confirm(`Are you sure you want to delete healthcare device ID: ${id}?`)) return;
    try {
        const response = await fetch(`/api/devices/${id}`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) {
            showToast('Device record deleted successfully.', 'success');
            loadDevices();
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error deleting device.', 'error');
    }
}

// --------------------------------------------------------------------------
// Billing, Customer & Invoice Logic
// --------------------------------------------------------------------------

// Populate dropdown of select items in the billing form
async function populateBillingItemsDropdown() {
    try {
        const resMed = await fetch('/api/medicines');
        const resDev = await fetch('/api/devices');
        const medResult = await resMed.json();
        const devResult = await resDev.json();
        
        const selector = document.getElementById('bill-item-selector');
        selector.innerHTML = '<option value="" disabled selected>Choose medicine or device...</option>';
        
        allBillingItems = []; // Reset autocomplete cache
        
        if (medResult.success) {
            medResult.data.forEach(med => {
                if (med.medstock > 0) {
                    const opt = document.createElement('option');
                    opt.value = `med:${med.med_code}`;
                    opt.textContent = `[Medicine] ${med.med_name} (Stock: ${med.medstock}) - ₹${parseFloat(med.price).toFixed(2)}`;
                    opt.dataset.price = med.price;
                    opt.dataset.name = med.med_name;
                    opt.dataset.maxStock = med.medstock;
                    selector.appendChild(opt);
                    
                    // Cache item for suggestions
                    allBillingItems.push({
                        key: `med:${med.med_code}`,
                        name: med.med_name,
                        price: parseFloat(med.price),
                        stock: parseInt(med.medstock),
                        type: 'Medicine'
                    });
                }
            });
        }
        
        if (devResult.success) {
            devResult.data.forEach(dev => {
                if (dev.stock > 0) {
                    const opt = document.createElement('option');
                    opt.value = `dev:${dev.machine_id}`;
                    opt.textContent = `[Device] ${dev.name} (Stock: ${dev.stock}) - ₹${parseFloat(dev.price).toFixed(2)}`;
                    opt.dataset.price = dev.price;
                    opt.dataset.name = dev.name;
                    opt.dataset.maxStock = dev.stock;
                    selector.appendChild(opt);
                    
                    // Cache item for suggestions
                    allBillingItems.push({
                        key: `dev:${dev.machine_id}`,
                        name: dev.name,
                        price: parseFloat(dev.price),
                        stock: parseInt(dev.stock),
                        type: 'Device'
                    });
                }
            });
        }
    } catch (err) {
        console.error('Failed to populate item list', err);
    }
}

// Add item to active draft list
function addItemToDraftList() {
    const selector = document.getElementById('bill-item-selector');
    const selectedOption = selector.options[selector.selectedIndex];
    const qtyInput = document.getElementById('bill-item-qty');
    const qty = parseInt(qtyInput.value);
    
    if (!selectedOption || !selectedOption.value) {
        showToast('Please select a valid item first.', 'warning');
        return;
    }
    
    const price = parseFloat(selectedOption.dataset.price);
    const name = selectedOption.dataset.name;
    const maxStock = parseInt(selectedOption.dataset.maxStock);
    const itemKey = selectedOption.value;
    
    if (isNaN(qty) || qty <= 0) {
        showToast('Quantity must be greater than 0.', 'warning');
        return;
    }
    
    if (qty > maxStock) {
        showToast(`Quantity exceeded available stock (${maxStock} units max).`, 'warning');
        return;
    }
    
    // Check if item is already in list
    const existingIndex = draftInvoiceItems.findIndex(item => item.key === itemKey);
    if (existingIndex > -1) {
        const newQty = draftInvoiceItems[existingIndex].quantity + qty;
        if (newQty > maxStock) {
            showToast(`Total quantity in draft (${newQty}) exceeds available stock (${maxStock}).`, 'warning');
            return;
        }
        draftInvoiceItems[existingIndex].quantity = newQty;
        draftInvoiceItems[existingIndex].total = newQty * price;
    } else {
        draftInvoiceItems.push({
            key: itemKey,
            item_name: name,
            quantity: qty,
            price: price,
            total: qty * price
        });
    }
    
    // Reset selectors & inputs
    selector.selectedIndex = 0;
    document.getElementById('bill-item-search').value = '';
    document.getElementById('bill-item-price').value = '';
    qtyInput.value = '1';
    
    renderDraftInvoiceTable();
}

function renderDraftInvoiceTable() {
    const tbody = document.getElementById('invoice-items-body');
    const totalSpan = document.getElementById('bill-grand-total');
    
    tbody.innerHTML = '';
    if (draftInvoiceItems.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-table-text">No items added to this bill yet.</td></tr>`;
        totalSpan.textContent = '₹0.00';
        return;
    }
    
    let grandTotal = 0;
    
    draftInvoiceItems.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${item.item_name}</strong></td>
            <td>${item.quantity}</td>
            <td>₹${item.price.toFixed(2)}</td>
            <td>₹${item.total.toFixed(2)}</td>
            <td>
                <button type="button" class="table-action-btn" onclick="removeDraftItem(${index})" title="Remove">❌</button>
            </td>
        `;
        grandTotal += item.total;
        tbody.appendChild(tr);
    });
    
    totalSpan.textContent = `₹${grandTotal.toFixed(2)}`;
}

function removeDraftItem(index) {
    draftInvoiceItems.splice(index, 1);
    renderDraftInvoiceTable();
}

// Submit Invoice Form
async function submitNewBill(e) {
    e.preventDefault();
    
    if (draftInvoiceItems.length === 0) {
        showToast('Please add at least one item to the invoice before submitting.', 'warning');
        return;
    }
    
    const payload = {
        cust_id: document.getElementById('bill-cust-id').value,
        cust_name: document.getElementById('bill-cust-name').value,
        contact: document.getElementById('bill-cust-contact').value,
        address: document.getElementById('bill-cust-address').value,
        bill_id: document.getElementById('bill-invoice-id').value,
        dt_purchase: document.getElementById('bill-date').value,
        payment_mode: document.getElementById('bill-payment').value,
        items: draftInvoiceItems
    };
    
    try {
        const response = await fetch('/api/bills', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.success) {
            showToast('Invoice created successfully!', 'success');
            
            // Capture the ID to print immediately
            const billId = payload.bill_id;
            
            // Clear current form
            document.getElementById('billing-form').reset();
            draftInvoiceItems = [];
            renderDraftInvoiceTable();
            
            // Open print invoice modal
            openInvoicePrintView(billId);
            
            // Reload stocks dropdown list for updated quantities
            populateBillingItemsDropdown();
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error recording invoice.', 'error');
    }
}

// 4. Billing History
async function loadBillingHistory() {
    try {
        const response = await fetch('/api/bills');
        const result = await response.json();
        if (result.success) {
            billingHistory = result.data;
            renderHistoryTable(billingHistory);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Error loading billing history.', 'error');
    }
}

function renderHistoryTable(data) {
    const tbody = document.getElementById('history-table-body');
    tbody.innerHTML = '';
    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-table-text">No invoices found.</td></tr>`;
        return;
    }
    
    data.forEach(bill => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><code>${bill.bill_id}</code></td>
            <td><code>${bill.cust_id}</code></td>
            <td><strong>${bill.cust_name}</strong></td>
            <td>${bill.dt_purchase}</td>
            <td><span class="badge badge-secondary">${bill.payment_mode}</span></td>
            <td><strong>₹${parseFloat(bill.total_amount).toFixed(2)}</strong></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="openInvoicePrintView('${bill.bill_id}')" style="padding: 4px 10px;">👁️ View Invoice</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// --------------------------------------------------------------------------
// Invoice Print Modal
// --------------------------------------------------------------------------
const invoiceModal = document.getElementById('invoice-modal');

async function openInvoicePrintView(billId) {
    try {
        const response = await fetch(`/api/bills/${billId}`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Set fields in Print view modal
            document.getElementById('inv-bill-id').textContent = data.bill_id;
            document.getElementById('inv-date').textContent = data.dt_purchase;
            document.getElementById('inv-cust-name').textContent = data.cust_name;
            document.getElementById('inv-cust-address').textContent = data.address || 'Address not provided';
            document.getElementById('inv-cust-contact').textContent = data.contact || 'N/A';
            document.getElementById('inv-payment-mode').textContent = data.payment_mode;
            document.getElementById('inv-total-amount').textContent = `₹${data.total_amount.toFixed(2)}`;
            
            const tbody = document.getElementById('invoice-items-list');
            tbody.innerHTML = '';
            
            data.items.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.item_name}</strong></td>
                    <td class="text-center">${item.quantity}</td>
                    <td class="text-right">₹${item.price.toFixed(2)}</td>
                    <td class="text-right">₹${item.total.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });
            
            invoiceModal.classList.add('active');
        } else {
            showToast(result.error, 'error');
        }
    } catch (err) {
        showToast('Error loading invoice preview.', 'error');
    }
}

function closeInvoiceModal() {
    invoiceModal.classList.remove('active');
}

function printInvoice() {
    window.print();
}

// --------------------------------------------------------------------------
// Barcode Scanner Engine
// --------------------------------------------------------------------------
function openScanner(targetInputId) {
    scannerTargetInputId = targetInputId;
    document.getElementById('scanner-modal').classList.add('active');

    // Create a new instance of Html5Qrcode
    html5QrcodeScanner = new Html5Qrcode("scanner-view");

    // Barcodes are wider than QR codes, so config box is adjusted
    const config = { 
        fps: 10, 
        qrbox: { width: 300, height: 160 } 
    };

    html5QrcodeScanner.start(
        { facingMode: "environment" }, // Prefer back camera on mobile devices
        config,
        onScanSuccess,
        onScanFailure
    ).catch(err => {
        console.error("Camera access failed", err);
        showToast("Webcam access failed. Verify camera connection and browser permissions.", "error");
        closeScannerModal();
    });
}

function onScanSuccess(decodedText, decodedResult) {
    if (scannerTargetInputId) {
        document.getElementById(scannerTargetInputId).value = decodedText;
    }
    showToast(`Barcode Scanned: ${decodedText}`, "success");
    
    // Play sound notification
    playBeepSound();

    closeScannerModal();
}

function onScanFailure(error) {
    // Suppress console flood during continuous scanning frames
}

function closeScannerModal() {
    document.getElementById('scanner-modal').classList.remove('active');
    
    if (html5QrcodeScanner) {
        html5QrcodeScanner.stop().then(() => {
            console.log("Camera feed stopped successfully.");
            html5QrcodeScanner = null;
        }).catch(err => {
            console.error("Failed to stop camera stream", err);
            html5QrcodeScanner = null;
        });
    }
}

function playBeepSound() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(900, audioCtx.currentTime); // 900 Hz Tone
        gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime); // Soft volume

        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.12); // Duration 120ms
    } catch (e) {
        console.warn("Audio Context sound failed", e);
    }
}

// --------------------------------------------------------------------------
// Administrator Session Lifecycle Management
// --------------------------------------------------------------------------
function getTodayDateString() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function checkLoginSession() {
    const loginContainer = document.getElementById('login-container');
    const appContainer = document.querySelector('.app-container');
    const todayStr = getTodayDateString();
    const storedLoginDate = localStorage.getItem('medtech_login_date');
    
    if (storedLoginDate === todayStr) {
        loginContainer.style.display = 'none';
        appContainer.style.display = 'flex';
        
        switchTab('dashboard');
        loadDashboardStats();
        loadBillingHistory();
        loadMedicines();
        loadDevices();
    } else {
        loginContainer.style.display = 'flex';
        appContainer.style.display = 'none';
        document.getElementById('login-username').focus();
    }
}

async function handleLoginFormSubmit(e) {
    e.preventDefault();
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const username = usernameInput.value;
    const password = passwordInput.value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        
        if (result.success) {
            showToast('Login successful!', 'success');
            
            localStorage.setItem('medtech_login_date', getTodayDateString());
            
            usernameInput.value = '';
            passwordInput.value = '';
            
            document.getElementById('login-container').style.display = 'none';
            document.querySelector('.app-container').style.display = 'flex';
            
            switchTab('dashboard');
            loadDashboardStats();
            loadBillingHistory();
            loadMedicines();
            loadDevices();
        } else {
            showToast(result.error || 'Authentication failed', 'error');
        }
    } catch (err) {
        showToast('Connection to auth server failed.', 'error');
    }
}

function logoutAdmin() {
    if (!confirm('Are you sure you want to lock the dashboard? You will need to log in again.')) {
        return;
    }
    localStorage.removeItem('medtech_login_date');
    
    document.getElementById('login-container').style.display = 'flex';
    document.querySelector('.app-container').style.display = 'none';
    showToast('Dashboard locked successfully.', 'info');
}

function closeChangePasswordModal() {
    document.getElementById('change-password-modal').classList.remove('active');
    document.getElementById('owner-passkey').value = '';
    document.getElementById('new-admin-password').value = '';
    document.getElementById('confirm-admin-password').value = '';
}

async function handleChangePasswordSubmit(e) {
    e.preventDefault();
    const ownerKeyInput = document.getElementById('owner-passkey');
    const newPassInput = document.getElementById('new-admin-password');
    const confirmPassInput = document.getElementById('confirm-admin-password');
    
    const owner_key = ownerKeyInput.value;
    const new_password = newPassInput.value;
    const confirm_password = confirmPassInput.value;
    
    if (new_password !== confirm_password) {
        showToast('New passwords do not match.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ owner_key, new_password })
        });
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            closeChangePasswordModal();
            
            // Log out admin to enforce login with new password
            localStorage.removeItem('medtech_login_date');
            document.getElementById('login-container').style.display = 'flex';
            document.querySelector('.app-container').style.display = 'none';
        } else {
            showToast(result.error || 'Failed to update password.', 'error');
        }
    } catch (err) {
        showToast('Connection to auth server failed.', 'error');
    }
}
