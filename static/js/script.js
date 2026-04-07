const currentPath = window.location.pathname;
const buttons = document.querySelectorAll('.button-container button');
buttons.forEach(button => {
    console.log(button.getAttribute('onclick'));
    console.log(currentPath);
    if (button.getAttribute('onclick').includes(currentPath)) {
        console.log(button);
        button.classList.add('active');
    }
});