try {
    const expanderBtn = document.getElementById('expander-btn');

    expanderBtn.addEventListener('click', () => {
        const navigationInner = document.querySelector('.navigation-inner');

        if (navigationInner.classList.contains('hidden')) {
            navigationInner.classList.remove('hidden');
            setTimeout(() => {
                navigationInner.classList.toggle('open');
            }, 50);
            expanderBtn.classList.toggle('bx-chevron-down');
            expanderBtn.classList.toggle('bx-chevron-up');
        } else {
            navigationInner.classList.remove('open');
            setTimeout(() => {
                navigationInner.classList.add('hidden');
            }, 350);
            expanderBtn.classList.toggle('bx-chevron-down');
            expanderBtn.classList.toggle('bx-chevron-up');
        }

        document.addEventListener('click', (e) => {
            const header = document.querySelector('.header');
            if (!navigationInner.classList.contains('hidden') &&
                !navigationInner.contains(e.target) &&
                !expanderBtn.contains(e.target) &&
                !header.contains(e.target)) {

                navigationInner.classList.remove('open');
                setTimeout(() => {
                    navigationInner.classList.add('hidden');
                }, 350);
                expanderBtn.classList.toggle('bx-chevron-up');
                expanderBtn.classList.toggle('bx-chevron-down');
            }
        });
    });
} catch (error) { }

try {
    const addWorkingDetailsBtn = document.getElementById('add-working-details-btn');

    addWorkingDetailsBtn.addEventListener('click', () => {
        const addWorkingDetails = document.querySelector('.add-working-details');

        if (addWorkingDetails.classList.contains('hidden')) {
            addWorkingDetails.classList.remove('hidden');
            setTimeout(() => {
                addWorkingDetails.classList.toggle('open');
            }, 50);
        } else {
            addWorkingDetails.classList.remove('open');
            setTimeout(() => {
                addWorkingDetails.classList.add('hidden');
            }, 350);
        }

        document.addEventListener('click', (e) => {
            if (!addWorkingDetails.contains(e.target)) {
                addWorkingDetails.classList.remove('open');
                setTimeout(() => {
                    addWorkingDetails.classList.add('hidden');
                }, 350);
            }
        });
    });
} catch (error) { }

function getHqDetails() {
    fetch('/get_hq_details')
        .then(response => response.json())
        .then(data => {
            if (data.status_code === 200) {
                const hqDetails = data.data;
                const mrSelect = document.getElementById('add-working-with');
                mrSelect.innerHTML = '';
                mrSelect.innerHTML += '<option value="" selected disabled>Working With</option>';
                hqDetails.forEach(hq => {
                    const option = document.createElement('option');
                    option.value = hq.mr_name;
                    option.textContent = hq.mr_name;
                    mrSelect.appendChild(option);
                });
                mrSelect.addEventListener('change', () => {
                    const hqSelect = document.getElementById('add-working-place');
                    hqSelect.innerHTML = '';
                    hqSelect.innerHTML += '<option value="" selected disabled>Working Place</option>';
                    const selectedMr = mrSelect.value;
                    hqDetails.forEach(hq => {
                        if (hq.mr_name === selectedMr) {
                            const option = document.createElement('option');
                            option.value = hq.wp_name;
                            option.textContent = hq.wp_name;
                            hqSelect.appendChild(option);
                        }
                    });
                });
            }
            else {
                alert(data.error);
            }
        })
}

getHqDetails();

function getFormData() {
    const workingWith = document.getElementById('add-working-with').value;
    if (workingWith === '') {
        alert('Please select working with');
        return;
    }
    const workingPlace = document.getElementById('add-working-place').value;
    if (workingPlace === '') {
        alert('Please select working place');
        return;
    }
    const date = document.getElementById('add-working-date').value;
    if (date === '') {
        alert('Please select date');
        return;
    }
    const day = new Date(date).toLocaleDateString('en-US', { weekday: 'long' });
    const spNote = document.getElementById('add-special-note').value;
    const data = {
        working_with: workingWith,
        working_place: workingPlace,
        date: date.split('-').reverse().join('-'),
        day: day,
        sp_note: spNote
    };
    return data;
}

function resetForm() {
    const addWorkingDetails = document.querySelector('.add-working-details');
    addWorkingDetails.classList.remove('open');
    showWorkingDetails();
    setTimeout(() => {
        addWorkingDetails.classList.add('hidden');
    }, 350);
}

function addWorking() {
    const data = getFormData();
    fetch('/add_working', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status_code === 200) {
                alert(data.message);
                resetForm();
            }
            else {
                alert(data.error);
            }
        })
}

const addWorkingBtn = document.getElementById('add-working-submit-btn');
addWorkingBtn.addEventListener('click', addWorking);

async function showWorkingDetails() {
    const res = await fetch('/get_working_details', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    const response = await res.json();
    if (response.status_code === 200) {
        const showWorkingDetailsDiv = document.getElementById('show-working-section');
        showWorkingDetailsDiv.innerHTML = '';
        for (let i = 0; i < response.data.length; i++) {
            if (i % 3 === 0) {
                const div = document.createElement('div');
                div.classList.add('grid-container');
                div.id = 'grid-container-' + Math.floor(i / 3);
                showWorkingDetailsDiv.appendChild(div);
                const contentCard = document.createElement('div');
                contentCard.classList.add('content-card');
                contentCard.innerHTML = `
                        <div class="card-header">
                            <div class="day" id="card-header-day">${response.data[i].day}</div>
                            <div class="date" id="card-header-date">${response.data[i].date}</div>
                        </div>
                        <div class="card-body">
                            <div class="working-place" id="working-place">${response.data[i].working_place}</div>
                            <div class="working-with" id="working-with">${response.data[i].working_with}</div>
                        </div>
                        <div class="card-footer">
                            <div class="special-note" id="special-note">${response.data[i].sp_note}</div>
                        </div>
                    `;
                div.appendChild(contentCard);
            }
            else {
                const div = document.getElementById('grid-container-' + Math.floor(i / 3));
                const contentCard = document.createElement('div');
                contentCard.classList.add('content-card');
                contentCard.innerHTML = `
                        <div class="card-header">
                            <div class="day" id="card-header-day">${response.data[i].day}</div>
                            <div class="date" id="card-header-date">${response.data[i].date}</div>
                        </div>
                        <div class="card-body">
                            <div class="working-place" id="working-place">${response.data[i].working_place}</div>
                            <div class="working-with" id="working-with">${response.data[i].working_with}</div>
                        </div>
                        <div class="card-footer">
                            <div class="special-note" id="special-note">${response.data[i].sp_note}</div>
                        </div>
                    `;
                div.appendChild(contentCard);
            }
        }
    }
    else {
        alert(data.error);
    }
}

window.addEventListener('load', showWorkingDetails);