/*
 * Handles mobile nav
 */

function toggleMobileNavState() {
  const body = document.querySelector("body");
  const burger = document.querySelector(".burger");
  const isActive = body.classList.toggle("nav--active");
  burger.setAttribute("aria-expanded", isActive);
}

/*
 * Initializes burger functionality
 */

function initBurger() {
  const burger = document.querySelector(".burger");
  if (!burger) return;
  burger.addEventListener("click", toggleMobileNavState);
  burger.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleMobileNavState();
    }
  });
}

initBurger();
