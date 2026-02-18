const addFieldBtn = document.getElementById('add-field-btn');

async function addField() {
    const repName = document.getElementById('rep-name').value;
    const wpName = document.getElementById('wp-name').value;
    const inputBucket = document.getElementById('input-bucket');
    const div = document.createElement('div');
    div.classList.add('input-bucket-item');
    const subDivs = [
        document.createElement('div'),
        document.createElement('div'),
        document.createElement('div'),
    ]
    subDivs.forEach(subDiv => {
        subDiv.classList.add('input-bucket-item-sub');
    })
    subDivs[0].innerHTML = `
        <input type="text" value="${repName}" placeholder="Representative Name *" required>
    `
    subDivs[1].innerHTML = `
        <input type="text" value="${wpName}" placeholder="Working Place Name (Exact) e.g. Arwal *" required>
    `
    subDivs[2].innerHTML = `
        <i class='bx bx-trash input-bucket-item-delete-btn'></i>
    `
    subDivs.forEach(subDiv => {
        div.appendChild(subDiv);
    })
    inputBucket.appendChild(div);
    document.getElementById('rep-name').value = '';
    document.getElementById('wp-name').value = '';
    const inputBucketItemDeleteBtn = document.querySelectorAll('.input-bucket-item-delete-btn');
    inputBucketItemDeleteBtn.forEach(inputBucketItemDeleteBtn => {
        inputBucketItemDeleteBtn.addEventListener('click', () => {
            inputBucketItemDeleteBtn.parentElement.parentElement.remove();
        });
    });
}

addFieldBtn.addEventListener('click', addField);

const finalAddBtn = document.getElementById('final-add-btn');
finalAddBtn.addEventListener('click', async () => {
    const confirm = prompt('Are you sure you want to add these details? Please make sure you have added all the details correctly and Working place name is exact as in SFC. Type "Y" to confirm "N" to cancel');
    if (confirm !== 'Y') {
        return;
    }
    const inputBucket = document.getElementById('input-bucket');
    const inputBucketItems = inputBucket.querySelectorAll('.input-bucket-item');
    const finalData = [];
    inputBucketItems.forEach(inputBucketItem => {
        const subDivs = inputBucketItem.querySelectorAll('.input-bucket-item-sub');
        const repName = subDivs[0].querySelector('input').value;
        if (repName === '') {
            alert('Representative Name is required');
            return;
        }
        const wpName = subDivs[1].querySelector('input').value;
        if (wpName === '') {
            alert('Working Place Name is required');
            return;
        }
        finalData.push({
            mr_name: repName.toLowerCase(),
            wp_name: wpName.toLowerCase()
        });
    });
    const response = await fetch('/add_hq_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(finalData)
    });
    const data = await response.json();
    if (data.status_code === 200) {
        alert(data.message);
        inputBucket.innerHTML = '';
        getHqDetails();
    } else {
        alert(data.error);
    }
});

async function addFieldHqUpdate() {
    const mrUpdateSelect = document.getElementById('mr-update');
    const mrUpdateSelectValue = mrUpdateSelect.value;
    if (mrUpdateSelectValue === '') {
        alert('Please select a MR');
        return;
    }
    const hqUpdateSelect = document.getElementById('hq-update');
    const hqUpdateSelectValue = hqUpdateSelect.value;
    if (hqUpdateSelectValue === '') {
        alert('Please select a HQ');
        return;
    }
    const hqBucket = document.getElementById('hq-bucket-update');
    const div = document.createElement('div');
    div.classList.add('input-bucket-item');
    const subDivs = [
        document.createElement('div'),
        document.createElement('div'),
        document.createElement('div'),
        document.createElement('div')
    ]
    subDivs.forEach(subDiv => {
        subDiv.classList.add('input-bucket-item-sub');
    })
    subDivs[0].innerHTML = `
        <input type="text" value="${mrUpdateSelectValue}" placeholder="Representative Name *" required disabled>
    `
    subDivs[1].innerHTML = `
        <input type="text" value="${hqUpdateSelectValue}" placeholder="Working Place Name *" required>
    `
    subDivs[2].innerHTML = `
        <input style="display: none;" id="old_hq_name_for_update" value="${hqUpdateSelectValue}">
    `
    subDivs[3].innerHTML = `
        <i class='bx bx-trash input-bucket-item-delete-btn'></i>
    `
    subDivs.forEach(subDiv => {
        div.appendChild(subDiv);
    })
    hqBucket.appendChild(div);
    document.getElementById('mr-update').value = '';
    document.getElementById('hq-update').value = '';
    const inputBucketItemDeleteBtn = document.querySelectorAll('.input-bucket-item-delete-btn');
    inputBucketItemDeleteBtn.forEach(inputBucketItemDeleteBtn => {
        inputBucketItemDeleteBtn.addEventListener('click', () => {
            inputBucketItemDeleteBtn.parentElement.parentElement.remove();
        });
    });
}

async function getHqDetails() {
    const response = await fetch('/get_hq_details');
    const data = await response.json();
    if (data.status_code === 200) {
        const mrUpdateSelect = document.getElementById('mr-update');
        mrUpdateSelect.innerHTML = '';
        var option = document.createElement('option');
        option.value = '';
        option.innerHTML = 'SELECT MR';
        option.disabled = true;
        option.selected = true;
        mrUpdateSelect.appendChild(option);
        data.data.forEach(data => {
            const option = document.createElement('option');
            option.value = data.mr_name;
            option.innerHTML = data.mr_name;
            mrUpdateSelect.appendChild(option);
        });
        mrUpdateSelect.addEventListener('change', async () => {
            const hqUpdateSelect = document.getElementById('hq-update');
            hqUpdateSelect.innerHTML = '';
            var option = document.createElement('option');
            option.value = '';
            option.innerHTML = 'SELECT HQ';
            option.disabled = true;
            option.selected = true;
            hqUpdateSelect.appendChild(option);
            data.data.forEach(data => {
                if (data.mr_name === mrUpdateSelect.value) {
                    const option = document.createElement('option');
                    option.value = data.wp_name;
                    option.innerHTML = data.wp_name;
                    hqUpdateSelect.appendChild(option);
                }
            });
            hqUpdateSelect.addEventListener('change', addFieldHqUpdate);
        })
        const mrEditSelect = document.getElementById('mr-edit');
        mrEditSelect.innerHTML = '';
        var option = document.createElement('option');
        option.value = '';
        option.innerHTML = 'SELECT MR';
        option.disabled = true;
        option.selected = true;
        mrEditSelect.appendChild(option);
        data.data.forEach(data => {
            const option = document.createElement('option');
            option.value = data.mr_name;
            option.innerHTML = data.mr_name;
            mrEditSelect.appendChild(option);
        });
    } else {
        alert(data.error);
    }
}

async function addFieldMrEdit() {
    const mrEditSelect = document.getElementById('mr-edit');
    const mrEditSelectValue = mrEditSelect.value;
    if (mrEditSelectValue === '') {
        alert('Please select a MR');
        return;
    }
    const mrBucket = document.getElementById('mr-bucket');
    const div = document.createElement('div');
    div.classList.add('input-bucket-item');
    const subDivs = [
        document.createElement('div'),
        document.createElement('div'),
        document.createElement('div')
    ]
    subDivs.forEach(subDiv => {
        subDiv.classList.add('input-bucket-item-sub');
    })
    subDivs[0].innerHTML = `
        <input type="text" value="${mrEditSelectValue}" placeholder="Representative Name *" required>
    `
    subDivs[1].innerHTML = `
        <input style="display: none;" id="old_mr_name_for_update" value="${mrEditSelectValue}">
    `
    subDivs[2].innerHTML = `
        <i class='bx bx-trash input-bucket-item-delete-btn'></i>
    `
    subDivs.forEach(subDiv => {
        div.appendChild(subDiv);
    })
    mrBucket.appendChild(div);
    document.getElementById('mr-edit').value = '';
    const inputBucketItemDeleteBtn = document.querySelectorAll('.input-bucket-item-delete-btn');
    inputBucketItemDeleteBtn.forEach(inputBucketItemDeleteBtn => {
        inputBucketItemDeleteBtn.addEventListener('click', () => {
            inputBucketItemDeleteBtn.parentElement.parentElement.remove();
        });
    });
}

const mrEdit = document.getElementById('mr-edit');
mrEdit.addEventListener('change', addFieldMrEdit);

const updateHqBtn = document.getElementById('update-hq-btn');
updateHqBtn.addEventListener('click', async () => {
    const hqBucket = document.getElementById('hq-bucket-update');
    const hqBucketItems = hqBucket.querySelectorAll('.input-bucket-item');
    const hqData = [];
    hqBucketItems.forEach(hqBucketItem => {
        const hqBucketItemSubs = hqBucketItem.querySelectorAll('.input-bucket-item-sub');
        mrName = hqBucketItemSubs[0].querySelector('input').value;
        newWpName = hqBucketItemSubs[1].querySelector('input').value;
        oldWpName = hqBucketItemSubs[2].querySelector('input').value;
        hqData.push({
            mr_name: mrName.toLowerCase(),
            new_wp_name: newWpName.toLowerCase(),
            old_wp_name: oldWpName.toLowerCase()
        });
    });
    const response = await fetch('/update_hq_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(hqData)
    });
    const data = await response.json();
    if (data.status_code === 200) {
        alert(data.message);
        hqBucket.innerHTML = '';
        getHqDetails();
    } else {
        alert(data.error);
    }
});

const updateMrBtn = document.getElementById('update-mr-btn');
updateMrBtn.addEventListener('click', async () => {
    const mrBucket = document.getElementById('mr-bucket');
    const mrBucketItems = mrBucket.querySelectorAll('.input-bucket-item');
    const mrData = [];
    mrBucketItems.forEach(mrBucketItem => {
        const mrBucketItemSubs = mrBucketItem.querySelectorAll('.input-bucket-item-sub');
        newMrName = mrBucketItemSubs[0].querySelector('input').value;
        oldMrName = mrBucketItemSubs[1].querySelector('input').value;
        mrData.push({
            new_mr_name: newMrName.toLowerCase(),
            old_mr_name: oldMrName.toLowerCase()
        });
    });
    const response = await fetch('/update_mr_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(mrData)
    });
    const data = await response.json();
    if (data.status_code === 200) {
        alert(data.message);
        mrBucket.innerHTML = '';
        getHqDetails();
    } else {
        alert(data.error);
    }
});

getHqDetails();
