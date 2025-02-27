document.addEventListener("DOMContentLoaded", function () {
    const themeSelector = document.getElementById("themeSelector");
    const body = document.body;

    // List of all available themes
    const themes = ["dark-mode", "violet-crush"];

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme && themes.includes(savedTheme)) {
        body.classList.add(savedTheme);
        themeSelector.value = savedTheme;
    }

    // Changes theme when the user selects an option
    themeSelector.addEventListener("change", function () {
        themes.forEach(theme => body.classList.remove(theme));

        const selectedTheme = themeSelector.value;
        if (themes.includes(selectedTheme)) {
            body.classList.add(selectedTheme);
        }

        localStorage.setItem("theme", selectedTheme);
    });
});
