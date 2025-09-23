function updateProfile() {
    const profile = document.getElementById('profile').value;
    const customInput = document.getElementById('custom_depth');
    if (profile === 'custom') {
        customInput.style.display = 'block';
        customInput.required = true;
    } else {
        customInput.style.display = 'none';
        customInput.required = false;
    }
    validateScanForm();
}

function validateScanForm() {
    const root = document.getElementById('root').value.trim();
    const profile = document.getElementById('profile').value;
    const customDepth = document.getElementById('custom_depth');
    const btn = document.getElementById('scan-btn');
    const errors = document.getElementById('scan-errors');

    let isValid = root !== '';
    if (profile === 'custom') {
        isValid = isValid && customDepth.value && parseInt(customDepth.value) >= 1;
    }

    btn.disabled = !isValid;

    if (!isValid) {
        errors.textContent = 'Please fill in all required fields.';
        errors.style.display = 'block';
    } else {
        errors.style.display = 'none';
    }

    return isValid;
}

document.getElementById('root').addEventListener('input', validateScanForm);
document.getElementById('custom_depth').addEventListener('input', validateScanForm);

// Initial validation
validateScanForm();
