document.querySelectorAll('.edit-button').forEach(button => {
    button.addEventListener('click', function (e) {
        const form = this.closest('form');
        if (this.dataset.editing === 'false' || !this.dataset.editing) {
            e.preventDefault();
            this.dataset.editing = 'true';
            this.textContent = 'Save';
            this.type = 'submit';

            // Allow editing most fields, keep date readonly
            form.querySelectorAll('input:not([type="date"]):not([type="hidden"]), textarea').forEach(input => {
                input.removeAttribute('readonly');
            });
        }
    });
});

document.querySelectorAll('.previous-working').forEach(form => {
    form.addEventListener('submit', function (e) {
        const p = prompt("Are you sure you want to update this entry? (y/n)");
        if (p !== 'y' && p !== 'Y') {
            e.preventDefault();
        }
    });
});