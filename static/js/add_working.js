document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function (e) {
            const p = prompt("Are you sure you want to add this entry? (y/n)");
            if (p !== 'y' && p !== 'Y') {
                e.preventDefault();
            }
        });
    }

    const dateInput = document.getElementById("date");
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    dateInput.value = `${year}-${month}-${day}`;
    dateInput.max = `${year}-${month}-${day}`;
});