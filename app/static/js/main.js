document.addEventListener("DOMContentLoaded", function () {
  initBurgerMenu();
  initSlider();
  initFlashToasts();
  initAdminStatusForms();
});

/* ---------- Бургер-меню (мобильная адаптивная навигация) ---------- */
function initBurgerMenu() {
  const burger = document.getElementById("burgerBtn");
  const nav = document.getElementById("mainNav");
  if (!burger || !nav) return;
  burger.addEventListener("click", function () {
    const isOpen = nav.classList.toggle("open");
    burger.classList.toggle("open", isOpen);
    burger.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
}

/* ---------- Слайдер портфолио: 4 изображения, автопрокрутка 3с, кнопки ---------- */
function initSlider() {
  const track = document.getElementById("sliderTrack");
  if (!track) return;

  const slides = track.querySelectorAll(".slide");
  const dotsWrap = document.getElementById("sliderDots");
  const prevBtn = document.getElementById("sliderPrev");
  const nextBtn = document.getElementById("sliderNext");
  const total = slides.length;
  let index = 0;
  let timer = null;

  slides.forEach((_, i) => {
    const dot = document.createElement("button");
    dot.setAttribute("role", "tab");
    dot.setAttribute("aria-label", "Слайд " + (i + 1));
    if (i === 0) dot.classList.add("active");
    dot.addEventListener("click", () => goTo(i));
    dotsWrap.appendChild(dot);
  });
  const dots = dotsWrap.querySelectorAll("button");

  function render() {
    track.style.transform = `translateX(-${index * (100 / total)}%)`;
    dots.forEach((d, i) => d.classList.toggle("active", i === index));
  }

  function goTo(i) {
    index = (i + total) % total;
    render();
    restartTimer();
  }

  function next() { goTo(index + 1); }
  function prev() { goTo(index - 1); }

  function restartTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(next, 3000);
  }

  prevBtn.addEventListener("click", prev);
  nextBtn.addEventListener("click", next);

  // пауза автопрокрутки при наведении/фокусе (доступность и удобство)
  const sliderEl = track.closest(".slider");
  sliderEl.addEventListener("mouseenter", () => clearInterval(timer));
  sliderEl.addEventListener("mouseleave", restartTimer);

  render();
  restartTimer();
}

/* ---------- Тосты для flash-сообщений Flask ---------- */
function showToast(message, category) {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast " + (category === "error" ? "error" : "success");
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3100);
}

function initFlashToasts() {
  if (window.__flashMessages) {
    window.__flashMessages.forEach(([category, message]) => {
      showToast(message, category);
    });
  }
}

/* ---------- Админ-панель: смена статуса без перезагрузки страницы ---------- */
function initAdminStatusForms() {
  document.querySelectorAll(".status-form").forEach((form) => {
    const select = form.querySelector("select[name=status]");
    select.addEventListener("change", function () {
      select.className = "status-select status-" + select.value;
      const formData = new FormData(form);
      fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: formData,
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.ok) {
            showToast("Статус заявки №" + form.dataset.bookingId + " изменён на «" + data.label + "»", "success");
          } else {
            showToast(data.error || "Ошибка обновления статуса", "error");
          }
        })
        .catch(() => showToast("Не удалось обновить статус. Проверьте соединение.", "error"));
    });
  });
}
