document.addEventListener("DOMContentLoaded", () => {
    const nameInput = document.getElementById("name");
    const placesInput = document.getElementById("place");
    const deleteBtn = document.getElementById("delete-btn");

    function updateFields() {
        if (!nameInput.value) {
            placesInput.value = "";
            deleteBtn.style.display = "none";
            return;
        }

        const name = nameInput.value.toLowerCase();
        
        let found = false;
        for (const key in placesData) {
            if (key.toLowerCase() === name) {
                const places = placesData[key];
                placesInput.value = places.join(";").toUpperCase();
                deleteBtn.style.display = "block";
                found = true;
                break;
            }
        }
        
        if (!found) {
            placesInput.value = "";
            deleteBtn.style.display = "none";
        }
    }

    nameInput.addEventListener("input", updateFields);
    nameInput.addEventListener("change", updateFields);
    
    const form = document.getElementById("settings-form");
    if (form) {
        form.addEventListener('submit', function(e) {
            const action = e.submitter ? e.submitter.value : "update";
            const msg = action === "delete" 
                ? "Are you sure you want to delete this representative?" 
                : "Are you sure you want to save these changes?";
            const p = prompt(`${msg} (y/n)`);
            if (p !== 'y' && p !== 'Y') {
                e.preventDefault();
            }
        });
    }
    
    updateFields();
});