const openModalButtons = document.querySelectorAll('[data-modal-target]')
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')

openModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = document.querySelector(button.dataset.modalTarget)
        openModal(modal)
        const customerId = button.dataset.customerId;
        const deleteForm = document.getElementById('delete-form');
        const actionUrl = `/delete-customer/${customerId}/`;
        deleteForm.action = actionUrl;
    })
})

document.getElementById('confirm-delete').addEventListener('click', (event) => {
    event.preventDefault(); // Prevent default form submission
    const deleteForm = document.getElementById('delete-form');
    const modal = deleteForm.closest('.modal');
    closeModal(modal); // Close the modal after deletion
    fetch(deleteForm.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Function to get CSRF token from cookie
        },
        body: JSON.stringify({})  // You can include additional data if needed
    })
    .then(response => {
        if (response.ok) {
            // Update UI or reload page as needed
            console.log('Customer deleted successfully.');
            // Example: Reload page after deletion
            window.location.reload();
        } else {
            console.error('Error deleting customer.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
})

overlay.addEventListener('click', () => {
    const modals = document.querySelectorAll('.modal.active')
    modals.forEach(modal => {
        closeModal(modal)
    })
})

closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal')
        closeModal(modal)
    })
})

function openModal(modal) {
    if (modal == null) return
    modal.classList.add('active')
    overlay.classList.add('active')
}

function closeModal(modal) {
    if (modal == null) return
    modal.classList.remove('active')
    overlay.classList.remove('active')
}

// Function to get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
