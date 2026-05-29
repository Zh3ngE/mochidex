/* STATE */

const state = {
    currentPage: 1,
    gridSize: 4,
    binder: "default",
    currentPosition: null
};

/* DOM ELEMENTS */

const cardGrid = document.getElementById("cardGrid");
const searchInput = document.getElementById("searchCard");
const searchResults = document.getElementById("searchResults");

/* LOCAL DB */

const Storage = {
    get(key, fallback = {}) {
        return JSON.parse(localStorage.getItem(key)) || fallback;
    },
    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }
};

/* API */

async function searchCards(query) {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    return data.data || [];
}

/* GRID SYSTEM */

function createGrid() {
    cardGrid.innerHTML = "";

    for (let i = 0; i < state.gridSize; i++) {
        const slot = document.createElement("div");
        slot.className = "card-slot empty";
        slot.textContent = "+";

        slot.onclick = () => openAddCard(i);

        cardGrid.appendChild(slot);
    }
}

function addCardToSlot(card, position) {
    const slot = cardGrid.children[position];

    slot.classList.remove("empty");
    slot.innerHTML = `<img src="${card.images.small}">`;

    slot.cardData = card;

    savePage();
}

/* LOGIC (PAGE SAVE) */

function savePage() {
    const data = {};

    [...cardGrid.children].forEach((slot, i) => {
        if (!slot.classList.contains("empty")) {
            data[i] = {
                imageUrl: slot.querySelector("img").src,
                cardData: slot.cardData
            };
        }
    });

    Storage.set(`${state.binder}_page_${state.currentPage}`, data);
}

function loadPage() {
    const data = Storage.get(`${state.binder}_page_${state.currentPage}`);

    Object.entries(data).forEach(([pos, card]) => {
        const slot = cardGrid.children[pos];

        slot.classList.remove("empty");
        slot.innerHTML = `<img src="${card.imageUrl}">`;
        slot.cardData = card.cardData;
    });
}

/* SEARCH */

searchInput?.addEventListener("input", debounce(async (e) => {
    const query = e.target.value;

    if (query.length < 2) {
        searchResults.innerHTML = "";
        return;
    }

    const results = await searchCards(query);

    searchResults.innerHTML = results.map((card, i) => `
        <div class="search-item" data-index="${i}">
            <img src="${card.images.small}">
            <span>${card.name}</span>
        </div>
    `).join("");

    document.querySelectorAll(".search-item").forEach((el, i) => {
        el.onclick = () => addCardToSlot(results[i], state.currentPosition);
    });

}, 400));

/* ACTIONS */

function openAddCard(position) {
    state.currentPosition = position;
}

/* UTIL */

function debounce(func, wait) {
    let timeout;

    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

/* INIT */

createGrid();
loadPage();