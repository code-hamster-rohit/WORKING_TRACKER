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
