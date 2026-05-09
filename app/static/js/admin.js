async function requestJson(url, method, body) {
    const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || response.statusText);
    }
    return response.json();
}

function showAlert(selector, message, type = 'success') {
    const element = document.querySelector(selector);
    if (!element) return;
    element.innerHTML = `<div class="alert alert-${type} py-2">${message}</div>`;
    setTimeout(() => { element.innerHTML = ''; }, 4000);
}

function editCustomer(customerId, name, phone, address) {
    document.querySelector('#customerId').value = customerId;
    document.querySelector('#customerName').value = name;
    document.querySelector('#customerPhone').value = phone;
    document.querySelector('#customerAddress').value = address;
    document.querySelector('#customerSubmit').textContent = 'Cập nhật khách';
}

async function submitCustomerForm(event) {
    event.preventDefault();
    const customerId = document.querySelector('#customerId').value;
    const body = {
        CustomerName: document.querySelector('#customerName').value.trim(),
        PhoneNumber: document.querySelector('#customerPhone').value.trim(),
        Address: document.querySelector('#customerAddress').value.trim(),
    };
    try {
        if (customerId) {
            await requestJson(`/customers/${customerId}`, 'PUT', body);
            showAlert('#customerMessage', 'Cập nhật khách hàng thành công.', 'success');
        } else {
            await requestJson('/customers/', 'POST', body);
            showAlert('#customerMessage', 'Thêm khách hàng thành công.', 'success');
        }
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert('#customerMessage', error.message || 'Lỗi khi lưu khách hàng.', 'danger');
    }
}

function editTable(tableId, number, capacity, status) {
    document.querySelector('#tableId').value = tableId;
    document.querySelector('#tableNumber').value = number;
    document.querySelector('#tableCapacity').value = capacity;
    document.querySelector('#tableStatus').value = status;
    document.querySelector('#tableSubmit').textContent = 'Cập nhật bàn';
}

async function submitTableForm(event) {
    event.preventDefault();
    const tableId = document.querySelector('#tableId').value;
    const body = {
        TableNumber: document.querySelector('#tableNumber').value.trim(),
        Capacity: Number(document.querySelector('#tableCapacity').value),
        Status: document.querySelector('#tableStatus').value,
    };
    try {
        if (tableId) {
            await requestJson(`/tables/${tableId}`, 'PUT', body);
            showAlert('#tableMessage', 'Cập nhật bàn thành công.', 'success');
        } else {
            await requestJson('/tables/', 'POST', body);
            showAlert('#tableMessage', 'Thêm bàn thành công.', 'success');
        }
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert('#tableMessage', error.message || 'Lỗi khi lưu bàn.', 'danger');
    }
}

function editMenuItem(itemId, name, price, categoryId) {
    document.querySelector('#menuItemId').value = itemId;
    document.querySelector('#menuDishName').value = name;
    document.querySelector('#menuPrice').value = price;
    document.querySelector('#menuCategory').value = categoryId;
    document.querySelector('#menuSubmit').textContent = 'Cập nhật món';
}

async function submitMenuForm(event) {
    event.preventDefault();
    const itemId = document.querySelector('#menuItemId').value;
    const body = {
        DishName: document.querySelector('#menuDishName').value.trim(),
        Price: Number(document.querySelector('#menuPrice').value),
        CategoryID: Number(document.querySelector('#menuCategory').value),
    };
    try {
        if (itemId) {
            await requestJson(`/menu/items/${itemId}`, 'PUT', body);
            showAlert('#menuMessage', 'Cập nhật món ăn thành công.', 'success');
        } else {
            await requestJson('/menu/items', 'POST', body);
            showAlert('#menuMessage', 'Thêm món ăn thành công.', 'success');
        }
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert('#menuMessage', error.message || 'Lỗi khi lưu món ăn.', 'danger');
    }
}

async function submitReservationForm(event) {
    event.preventDefault();
    const body = {
        CustomerID: Number(document.querySelector('#reservationCustomer').value),
        TableID: Number(document.querySelector('#reservationTable').value),
        DateTime: document.querySelector('#reservationDatetime').value,
        GuestCount: Number(document.querySelector('#reservationGuests').value),
    };
    try {
        await requestJson('/reservations/', 'POST', body);
        showAlert('#reservationMessage', 'Tạo đặt bàn thành công.', 'success');
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert('#reservationMessage', error.message || 'Lỗi khi tạo đặt bàn.', 'danger');
    }
}

if (document.querySelector('#customerForm')) {
    document.querySelector('#customerForm').addEventListener('submit', submitCustomerForm);
}
if (document.querySelector('#tableForm')) {
    document.querySelector('#tableForm').addEventListener('submit', submitTableForm);
}
if (document.querySelector('#menuForm')) {
    document.querySelector('#menuForm').addEventListener('submit', submitMenuForm);
}
if (document.querySelector('#reservationForm')) {
    document.querySelector('#reservationForm').addEventListener('submit', submitReservationForm);
}
