const burger = document.querySelector(".burger");

if (burger) {
  burger.addEventListener("click", () => {
    burger.setAttribute("aria-expanded", document.body.classList.toggle("nav--active"));
  });
}
