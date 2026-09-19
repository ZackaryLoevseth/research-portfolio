// Keep the essay visible on arrival on narrow screens. Native details remains
// fully operable; without JavaScript, the complete table of contents is open.
const contents = document.querySelector('.essay-sidebar details');
const narrow = window.matchMedia('(max-width: 800px)');
const adapt = () => { contents.open = !narrow.matches; };
adapt();
narrow.addEventListener('change', adapt);
