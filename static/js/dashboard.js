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
            expanderBtn.classList.toggle('bx-chevron-down');
            expanderBtn.classList.toggle('bx-chevron-up');
        }
    });
});

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
