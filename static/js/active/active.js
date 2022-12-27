const listRoute = document.querySelectorAll('.app-menu__item');
const path = window.location.pathname.slice(0);

listRoute.forEach((route) => {
    if (route.getAttribute('href') == path) {
        route.classList.add('active');
    } else {
        route.classList.remove('active');
    }
});

