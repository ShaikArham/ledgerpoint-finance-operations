(() => {
  "use strict";
  const valid = new Set(["overview","reconciliation","invoices","performance","case-study"]);
  const links = Array.from(document.querySelectorAll("[data-view]"));
  const views = Array.from(document.querySelectorAll(".view"));
  function show(name, scroll = false) {
    const chosen = valid.has(name) ? name : "overview";
    views.forEach(view => { view.classList.toggle("active", view.id === chosen); });
    links.forEach(link => {
      const active = link.dataset.view === chosen;
      link.classList.toggle("active", active);
      if (link.closest("nav")) {
        if (active) link.setAttribute("aria-current","page");
        else link.removeAttribute("aria-current");
      }
    });
    document.title = "LedgerPoint | " + ({
      overview:"Executive overview", reconciliation:"Bank reconciliation",
      invoices:"Invoice register", performance:"Financial performance",
      "case-study":"Case study"
    }[chosen]);
    if (scroll) window.scrollTo({top:0,behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});
  }
  function sync(scroll=false) { show(decodeURIComponent(location.hash.slice(1)),scroll); }
  links.forEach(link => link.addEventListener("click", () => {
    if (location.hash === link.getAttribute("href")) show(link.dataset.view,true);
  }));
  window.addEventListener("hashchange",() => sync(true));
  sync();
})();
