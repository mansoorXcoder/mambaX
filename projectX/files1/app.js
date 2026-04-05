/* ═══════════════════════════════════════════════════════════
   CineLog — app.js
   Firebase Firestore + full CRUD + UI logic
════════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────
   1. FIREBASE CONFIGURATION
   ▸ Replace the values below with your own Firebase project config.
   ▸ You can find it in: Firebase Console → Project Settings → Your Apps → SDK setup & configuration
   ─────────────────────────────────────────────────────────
   FIREBASE SETUP STEPS:
   1. Go to https://console.firebase.google.com/
   2. Create a project (or use an existing one)
   3. Click "Add app" → Web (</> icon)
   4. Register the app, copy the firebaseConfig object here
   5. In Firebase Console → Firestore Database → Create database
   6. Choose "Start in test mode" (for development)
   7. That's it! The app is ready to use.
   ───────────────────────────────────────────────────────── */

const firebaseConfig = {
  apiKey:            "AIzaSyA-_8OmY4BFxQPqEa9hWb1ItvACPDPup5c",
  authDomain:        "movie-tracker-web-app-4bdec.firebaseapp.com",
  projectId:         "movie-tracker-web-app-4bdec",
  storageBucket:     "movie-tracker-web-app-4bdec.firebasestorage.app",
  messagingSenderId: "901631045576",
  appId:             "1:901631045576:web:db51af7c12de3cd1af1afd",
  measurementId:     "G-GSK7N51TMX"
};

/* ─── Initialize Firebase ─────────────────────────────── */
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

/* Collection references:
   - "users"  → documents: { name: "Siva" }
   - "movies" → documents: { title, type, status, rating, userId, ... }
*/
const usersCol  = db.collection("users");
const moviesCol = db.collection("movies");

/* ═══════════════════════════════════════════════════════════
   2. APP STATE
════════════════════════════════════════════════════════════ */
let currentUserId   = null;   // Firestore doc ID of the selected user
let currentUserName = null;
let allMovies       = [];     // movies for the current user (live from Firestore)
let moviesListener  = null;   // unsubscribe function for real-time listener

/* ═══════════════════════════════════════════════════════════
   3. DOM REFERENCES
════════════════════════════════════════════════════════════ */
const userSelect      = document.getElementById("userSelect");
const addUserBtn      = document.getElementById("addUserBtn");
const deleteUserBtn   = document.getElementById("deleteUserBtn");
const addUserForm     = document.getElementById("addUserForm");
const newUserName     = document.getElementById("newUserName");
const confirmAddUser  = document.getElementById("confirmAddUser");
const cancelAddUser   = document.getElementById("cancelAddUser");

const searchInput     = document.getElementById("searchInput");
const filterType      = document.getElementById("filterType");
const filterStatus    = document.getElementById("filterStatus");
const openAddModal    = document.getElementById("openAddModal");

const movieGrid       = document.getElementById("movieGrid");
const emptyState      = document.getElementById("emptyState");

const movieModal      = document.getElementById("movieModal");
const closeModal      = document.getElementById("closeModal");
const cancelModal     = document.getElementById("cancelModal");
const modalTitle      = document.getElementById("modalTitle");
const movieForm       = document.getElementById("movieForm");
const editId          = document.getElementById("editId");

// Form fields
const fTitle    = document.getElementById("fTitle");
const fType     = document.getElementById("fType");
const fStatus   = document.getElementById("fStatus");
const fRating   = document.getElementById("fRating");
const fGenre    = document.getElementById("fGenre");
const fPlatform = document.getElementById("fPlatform");
const fEpisodes = document.getElementById("fEpisodes");
const fRewatch  = document.getElementById("fRewatch");
const fPoster   = document.getElementById("fPoster");
const fNotes    = document.getElementById("fNotes");
const fFav      = document.getElementById("fFav");

const ratingDisplay = document.getElementById("ratingDisplay");
const themeToggle   = document.getElementById("themeToggle");

// Stats
const statTotal   = document.getElementById("statTotal");
const statWatched = document.getElementById("statWatched");
const statWatching= document.getElementById("statWatching");
const statPlan    = document.getElementById("statPlan");
const statFav     = document.getElementById("statFav");

/* ═══════════════════════════════════════════════════════════
   4. THEME TOGGLE
════════════════════════════════════════════════════════════ */
function initTheme() {
  const saved = localStorage.getItem("cinelog-theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  themeToggle.textContent = saved === "dark" ? "🌙" : "☀️";
}

themeToggle.addEventListener("click", () => {
  const html    = document.documentElement;
  const current = html.getAttribute("data-theme");
  const next    = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  themeToggle.textContent = next === "dark" ? "🌙" : "☀️";
  localStorage.setItem("cinelog-theme", next);
});

/* ═══════════════════════════════════════════════════════════
   5. USER MANAGEMENT
════════════════════════════════════════════════════════════ */

/** Load all users from Firestore and populate the dropdown */
async function loadUsers() {
  const snapshot = await usersCol.orderBy("name").get();

  userSelect.innerHTML = '<option value="">— Select User —</option>';

  if (snapshot.empty) {
    // Seed default users on first run
    await seedDefaultUsers();
    return loadUsers();
  }

  snapshot.forEach(doc => {
    const opt = document.createElement("option");
    opt.value       = doc.id;
    opt.textContent = doc.data().name;
    userSelect.appendChild(opt);
  });

  // Restore last selected user
  const savedId = localStorage.getItem("cinelog-userId");
  if (savedId) {
    userSelect.value = savedId;
    if (userSelect.value) onUserChange(savedId);
  }
}

/** Insert Siva, Vishnu, Geto as the default users */
async function seedDefaultUsers() {
  const defaults = ["Siva", "Vishnu", "Geto"];
  const batch    = db.batch();
  defaults.forEach(name => {
    const ref = usersCol.doc(); // auto ID
    batch.set(ref, { name });
  });
  await batch.commit();
}

/** Called whenever the dropdown selection changes */
function onUserChange(userId) {
  currentUserId   = userId;
  currentUserName = userSelect.options[userSelect.selectedIndex]?.text || "";
  localStorage.setItem("cinelog-userId", userId);

  // Detach previous real-time listener
  if (moviesListener) moviesListener();

  if (!userId) {
    allMovies = [];
    renderCards();
    return;
  }

  // Attach real-time listener for this user's movies
  moviesListener = moviesCol
    .where("userId", "==", userId)
    .orderBy("createdAt", "desc")
    .onSnapshot(snapshot => {
      allMovies = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      renderCards();
      updateStats();
    });
}

userSelect.addEventListener("change", () => onUserChange(userSelect.value));

/* ── Add User UI ─────────────────────────────────────────── */
addUserBtn.addEventListener("click", () => {
  addUserForm.classList.toggle("hidden");
  newUserName.focus();
});

cancelAddUser.addEventListener("click", () => {
  addUserForm.classList.add("hidden");
  newUserName.value = "";
});

confirmAddUser.addEventListener("click", async () => {
  const name = newUserName.value.trim();
  if (!name) return alert("Please enter a user name.");

  // Prevent duplicates
  const existing = await usersCol.where("name", "==", name).get();
  if (!existing.empty) return alert("A user with that name already exists.");

  const ref = await usersCol.add({ name });
  addUserForm.classList.add("hidden");
  newUserName.value = "";

  await loadUsers();
  userSelect.value = ref.id;
  onUserChange(ref.id);
});

/* ── Delete User ─────────────────────────────────────────── */
deleteUserBtn.addEventListener("click", async () => {
  if (!currentUserId) return alert("Select a user first.");
  if (!confirm(`Delete user "${currentUserName}" and ALL their movies? This cannot be undone.`)) return;

  // Delete all movies for this user
  const moviesSnap = await moviesCol.where("userId", "==", currentUserId).get();
  const batch = db.batch();
  moviesSnap.forEach(doc => batch.delete(doc.ref));
  batch.delete(usersCol.doc(currentUserId));
  await batch.commit();

  currentUserId = null;
  await loadUsers();
  allMovies = [];
  renderCards();
  updateStats();
});

/* ═══════════════════════════════════════════════════════════
   6. MOVIE CRUD
════════════════════════════════════════════════════════════ */

/** Add a new movie document to Firestore */
async function addMovie(data) {
  await moviesCol.add({
    ...data,
    userId:    currentUserId,
    createdAt: firebase.firestore.FieldValue.serverTimestamp()
  });
}

/** Update an existing movie document */
async function updateMovie(id, data) {
  await moviesCol.doc(id).update(data);
}

/** Delete a movie document */
async function deleteMovie(id) {
  await moviesCol.doc(id).delete();
}

/** Toggle the favourite flag */
async function toggleFav(id, currentVal) {
  await moviesCol.doc(id).update({ favourite: !currentVal });
}

/* ═══════════════════════════════════════════════════════════
   7. MODAL — OPEN / CLOSE
════════════════════════════════════════════════════════════ */
function openModal(movie = null) {
  movieForm.reset();
  fRating.value = 5;
  ratingDisplay.textContent = "5";

  if (movie) {
    // Edit mode
    modalTitle.textContent  = "Edit Movie";
    editId.value            = movie.id;
    fTitle.value            = movie.title    || "";
    fType.value             = movie.type     || "";
    fStatus.value           = movie.status   || "";
    fRating.value           = movie.rating   ?? 5;
    ratingDisplay.textContent = movie.rating ?? 5;
    fGenre.value            = movie.genre    || "";
    fPlatform.value         = movie.platform || "";
    fEpisodes.value         = movie.episodes || "";
    fRewatch.value          = movie.rewatch  || "";
    fPoster.value           = movie.poster   || "";
    fNotes.value            = movie.notes    || "";
    fFav.checked            = movie.favourite || false;
  } else {
    // Add mode
    modalTitle.textContent = "Add Movie";
    editId.value = "";
  }

  movieModal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  fTitle.focus();
}

function closeModalFn() {
  movieModal.classList.add("hidden");
  document.body.style.overflow = "";
}

openAddModal.addEventListener("click", () => {
  if (!currentUserId) return alert("Please select a user first.");
  openModal();
});

closeModal.addEventListener("click",  closeModalFn);
cancelModal.addEventListener("click", closeModalFn);
movieModal.addEventListener("click", e => { if (e.target === movieModal) closeModalFn(); });

/* Live rating display */
fRating.addEventListener("input", () => {
  ratingDisplay.textContent = fRating.value;
});

/* ── Form Submit ─────────────────────────────────────────── */
movieForm.addEventListener("submit", async e => {
  e.preventDefault();

  const data = {
    title:     fTitle.value.trim(),
    type:      fType.value,
    status:    fStatus.value,
    rating:    Number(fRating.value),
    genre:     fGenre.value.trim(),
    platform:  fPlatform.value.trim(),
    episodes:  fEpisodes.value ? Number(fEpisodes.value) : null,
    rewatch:   fRewatch.value  ? Number(fRewatch.value)  : 0,
    poster:    fPoster.value.trim(),
    notes:     fNotes.value.trim(),
    favourite: fFav.checked
  };

  const id = editId.value;

  try {
    if (id) {
      await updateMovie(id, data);
    } else {
      await addMovie(data);
    }
    closeModalFn();
  } catch (err) {
    console.error("Save error:", err);
    alert("Error saving movie. Check the console for details.");
  }
});

/* ═══════════════════════════════════════════════════════════
   8. RENDER CARDS
════════════════════════════════════════════════════════════ */
function getFilteredMovies() {
  const q  = searchInput.value.toLowerCase();
  const ft = filterType.value;
  const fs = filterStatus.value;

  return allMovies.filter(m => {
    const matchTitle  = !q  || m.title.toLowerCase().includes(q);
    const matchType   = !ft || m.type   === ft;
    const matchStatus = !fs || m.status === fs;
    return matchTitle && matchType && matchStatus;
  });
}

function statusClass(status) {
  if (status === "Watched")       return "status-watched";
  if (status === "Watching")      return "status-watching";
  if (status === "Plan to Watch") return "status-plan";
  return "";
}

function renderCards() {
  movieGrid.innerHTML = "";
  const movies = getFilteredMovies();

  if (movies.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }
  emptyState.classList.add("hidden");

  movies.forEach(m => {
    const card = document.createElement("div");
    card.className = `movie-card${m.favourite ? " is-fav" : ""}`;
    card.dataset.id = m.id;

    /* Poster */
    const posterHTML = m.poster
      ? `<img class="card-poster" src="${escHtml(m.poster)}" alt="${escHtml(m.title)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'" />
         <div class="card-poster-placeholder" style="display:none">🎬</div>`
      : `<div class="card-poster-placeholder">🎬</div>`;

    /* Meta lines */
    const metaLines = [];
    if (m.genre)    metaLines.push(`🎭 ${escHtml(m.genre)}`);
    if (m.platform) metaLines.push(`📺 ${escHtml(m.platform)}`);
    if (m.episodes) metaLines.push(`📋 ${m.episodes} eps`);
    if (m.rewatch)  metaLines.push(`🔁 Rewatched ×${m.rewatch}`);

    card.innerHTML = `
      ${posterHTML}
      <div class="card-body">
        <div class="card-top">
          <span class="card-title">${escHtml(m.title)}</span>
          <button class="fav-btn" title="Toggle favourite" data-id="${m.id}" data-fav="${m.favourite || false}">
            ${m.favourite ? "❤️" : "🤍"}
          </button>
        </div>

        <div class="card-tags">
          <span class="tag">${escHtml(m.type)}</span>
          <span class="tag ${statusClass(m.status)}">${escHtml(m.status)}</span>
        </div>

        <div class="card-rating">
          <div class="rating-bar"><div class="rating-fill" style="width:${m.rating * 10}%"></div></div>
          <span class="rating-value">${m.rating}/10</span>
        </div>

        ${metaLines.length ? `<div class="card-meta">${metaLines.map(l => `<span>${l}</span>`).join("")}</div>` : ""}

        ${m.notes ? `<p class="card-notes">${escHtml(m.notes)}</p>` : ""}
      </div>

      <div class="card-actions">
        <button class="btn btn-ghost edit-btn" data-id="${m.id}">✏️ Edit</button>
        <button class="btn btn-danger del-btn" data-id="${m.id}">🗑 Delete</button>
      </div>
    `;

    movieGrid.appendChild(card);
  });

  attachCardListeners();
}

function attachCardListeners() {
  /* Edit */
  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const movie = allMovies.find(m => m.id === btn.dataset.id);
      if (movie) openModal(movie);
    });
  });

  /* Delete */
  document.querySelectorAll(".del-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this movie?")) return;
      await deleteMovie(btn.dataset.id);
    });
  });

  /* Favourite */
  document.querySelectorAll(".fav-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const isFav = btn.dataset.fav === "true";
      await toggleFav(btn.dataset.id, isFav);
    });
  });
}

/* ═══════════════════════════════════════════════════════════
   9. STATS
════════════════════════════════════════════════════════════ */
function updateStats() {
  statTotal.textContent   = allMovies.length;
  statWatched.textContent = allMovies.filter(m => m.status === "Watched").length;
  statWatching.textContent= allMovies.filter(m => m.status === "Watching").length;
  statPlan.textContent    = allMovies.filter(m => m.status === "Plan to Watch").length;
  statFav.textContent     = allMovies.filter(m => m.favourite).length;
}

/* ═══════════════════════════════════════════════════════════
   10. SEARCH & FILTER LISTENERS
════════════════════════════════════════════════════════════ */
searchInput.addEventListener("input",  renderCards);
filterType.addEventListener("change",  renderCards);
filterStatus.addEventListener("change", renderCards);

/* ═══════════════════════════════════════════════════════════
   11. UTILITY
════════════════════════════════════════════════════════════ */
/** Escape HTML to prevent XSS */
function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ═══════════════════════════════════════════════════════════
   12. BOOTSTRAP THE APP
════════════════════════════════════════════════════════════ */
(async function init() {
  initTheme();
  await loadUsers();
  updateStats();
})();
