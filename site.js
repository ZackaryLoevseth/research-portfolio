(() => {
  document.documentElement.classList.add("js");

  const toggle = document.querySelector(".menu-toggle");
  const navigation = document.querySelector(".site-nav");

  if (!toggle || !navigation) {
    return;
  }

  const setOpen = (open) => {
    navigation.dataset.open = String(open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.textContent = open ? "Close" : "Menu";
  };

  setOpen(false);

  toggle.addEventListener("click", () => {
    setOpen(navigation.dataset.open !== "true");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && navigation.dataset.open === "true") {
      setOpen(false);
      toggle.focus();
    }
  });
})();
