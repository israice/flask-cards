document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("cards-container");
  const templates = {};

  // Load templates by status
  function loadTemplates() {
    const mapping = {
      STATUS_1: "/card_1.html",
      STATUS_2: "/card_2.html",
      STATUS_3: "/card_3.html",
    };
    return Promise.all(
      Object.entries(mapping).map(([status, url]) =>
        fetch(url)
          .then((res) => {
            if (!res.ok) throw new Error(`Failed to load ${url}`);
            return res.text();
          })
          .then((html) => {
            const div = document.createElement("div");
            div.innerHTML = html;
            templates[status] = div.querySelector("template").content;
          })
      )
    );
  }

  // Render cards
  function renderCards(cards) {
    container.innerHTML = "";

    cards.forEach((card) => {
      const tmpl = templates[card.status] || templates["STATUS_1"];
      const clone = tmpl.cloneNode(true);

      // fill basic fields
      const img = clone.querySelector(".card-img-top");
      if (img) img.src = card.url;
      clone
        .querySelectorAll(".card-chain")
        .forEach((el) => (el.textContent = card.CARD_CHAIN));
      clone
        .querySelectorAll(".card-name")
        .forEach((el) => (el.textContent = card.CARD_NAME));
      clone
        .querySelectorAll(".card-theme")
        .forEach((el) => (el.textContent = card.CARD_THEME));
      clone
        .querySelectorAll(".card-type")
        .forEach((el) => (el.textContent = card.CARD_TYPE));

      // Custom layout for STATUS_1: split CARD_COINS into array and render N rows
      if (card.status === "STATUS_1") {
        let coinsArr = [];
        if (Array.isArray(card.CARD_COINS)) {
          coinsArr = card.CARD_COINS;
        } else if (typeof card.CARD_COINS === "string") {
          coinsArr = card.CARD_COINS.split(",").map((s) => s.trim());
        }

        const coinsContainer = clone.querySelector(".stat-coins");
        coinsContainer.innerHTML = ""; // clear placeholder

        const table = document.createElement("table");
        coinsContainer.appendChild(table);

        coinsArr.forEach((_, idx) => {
          const tr = document.createElement("tr");

          if (idx === 0) {
            const tdLabel = document.createElement("td");
            tdLabel.rowSpan = coinsArr.length;
            tdLabel.textContent = "CARD_COINS";
            tr.appendChild(tdLabel);
          }

          const tdIcon = document.createElement("td");
          tdIcon.innerHTML = '<i class="bi bi-coin"></i>';
          tr.appendChild(tdIcon);

          const tdText = document.createElement("td");
          tdText.textContent = "COIN";
          tr.appendChild(tdText);

          table.appendChild(tr);
        });
      } else {
        clone
          .querySelectorAll(".card-coins")
          .forEach((el) => (el.textContent = card.CARD_COINS));
      }

      // fill remaining fields
      clone
        .querySelectorAll(".card-ammount")
        .forEach((el) => (el.textContent = card.USD_AMMOUNT));
      clone
        .querySelectorAll(".card-id")
        .forEach((el) => (el.textContent = card.CARD_ID));
      clone
        .querySelectorAll(".pack-id")
        .forEach((el) => (el.textContent = card.PACK_ID));
      clone
        .querySelectorAll(".card-date")
        .forEach((el) => (el.textContent = card.CARD_DATE));

      // flip on click
      const cardEl = clone.querySelector(".card");
      if (cardEl) cardEl.onclick = () => cardEl.classList.toggle("flipped");

      container.appendChild(clone);
    });
  }

  // Initialize loading and polling
  function initialize() {
    const saved = localStorage.getItem("cards");
    if (saved) {
      try {
        renderCards(JSON.parse(saved));
      } catch {
        localStorage.removeItem("cards");
      }
    }
    async function loadCards() {
      try {
        const res = await fetch("/api/cards");
        if (!res.ok) throw new Error("Network response was not ok");
        const cards = await res.json();
        renderCards(cards);
        localStorage.setItem("cards", JSON.stringify(cards));
      } catch (err) {
        console.error("Failed to load cards:", err);
      }
    }
    loadCards();
    setInterval(loadCards, 5000);
  }

  loadTemplates()
    .then(initialize)
    .catch((err) => console.error(err));
});
