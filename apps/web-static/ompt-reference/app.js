(function () {
  const root = document.documentElement;
  const page = root.dataset.page || document.body.dataset.page;

  const navLinks = document.querySelectorAll("[data-nav-link]");
  navLinks.forEach((link) => {
    if (link.dataset.navLink === page) link.classList.add("active");
  });

  const header = document.querySelector("[data-header]");
  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 12);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const navToggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    nav.addEventListener("click", (event) => {
      const target = event.target;
      if (target instanceof HTMLAnchorElement) {
        nav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  const revealTargets = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealTargets.forEach((el, index) => {
      el.style.transitionDelay = `${Math.min(index * 34, 220)}ms`;
      observer.observe(el);
    });
  } else {
    revealTargets.forEach((el) => el.classList.add("in"));
  }

  const glow = document.querySelector(".cursor-glow");
  if (glow && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    let x = window.innerWidth * 0.5;
    let y = window.innerHeight * 0.18;
    let tx = x;
    let ty = y;

    window.addEventListener(
      "pointermove",
      (event) => {
        tx = event.clientX;
        ty = event.clientY;
      },
      { passive: true }
    );

    const animateGlow = () => {
      x += (tx - x) * 0.055;
      y += (ty - y) * 0.055;
      glow.style.left = `${x}px`;
      glow.style.top = `${y}px`;
      requestAnimationFrame(animateGlow);
    };
    animateGlow();
  }

  const filterBar = document.querySelector("[data-filterbar]");
  const records = Array.from(document.querySelectorAll("[data-topic]"));

  if (filterBar && records.length) {
    filterBar.addEventListener("click", (event) => {
      const button = event.target.closest("[data-filter]");
      if (!button) return;

      const filter = button.dataset.filter;
      filterBar.querySelectorAll("[data-filter]").forEach((btn) => {
        btn.classList.toggle("active", btn === button);
      });

      records.forEach((record) => {
        const topics = record.dataset.topic || "";
        const show = filter === "all" || topics.split(" ").includes(filter);
        record.classList.toggle("is-hidden", !show);
      });
    });
  }

  const toast = document.querySelector("[data-toast]");
  let toastTimer = null;

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 1500);
  };

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.dataset.copy;
      if (!text) return;

      try {
        await navigator.clipboard.writeText(text);
        showToast("Copied DOI");
      } catch {
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
        showToast("Copied DOI");
      }
    });
  });
})();
