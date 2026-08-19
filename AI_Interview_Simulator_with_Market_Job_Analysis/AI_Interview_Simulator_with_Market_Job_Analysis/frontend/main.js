// MAAI - Landing page behavior

document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".feature-card");
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(12px)";
    setTimeout(() => {
      card.style.transition = "opacity 280ms ease, transform 280ms ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, 80 * index);
  });
});
