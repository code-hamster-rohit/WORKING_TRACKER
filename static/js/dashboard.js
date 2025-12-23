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

});

