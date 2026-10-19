(() => {
  const $ = (id) => document.getElementById(id);

  // DOM Elements
  const dropzone = $("dropzone");
  const imageInput = $("image");
  const preview = $("preview");
  const dropCopy = $("drop-copy");
  const clearImgBtn = $("btn-clear-img");
  const statusEl = $("status");
  const statusDot = $("status-dot");
  const generateBtn = $("generate");
  const btnSpinner = $("btn-spinner");
  const btnText = $("btn-text");
  const modelSelect = $("model-select");
  const studioModal = $("studio-modal");
  const modalContent = $("modal-content");
  const modalTitle = $("modal-title");

  let selectedFile = null;
  let catalogItems = [];
  let currentModalMode = "tent"; // "tent", "cheat", or "full"

  // 1. Health check & dynamic Ollama model detection
  async function refreshHealth() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      statusEl.textContent = data.message;
      if (data.ollama) {
        statusDot.className = "status-dot online";
        statusEl.className = "status ok";
      } else {
        statusDot.className = "status-dot demo";
        statusEl.className = "status warn";
      }

      // Populate model dropdown
      if (data.models && data.models.length > 0) {
        const curVal = modelSelect.value;
        modelSelect.innerHTML = `<option value="">Auto-detect best installed model</option>`;
        data.models.forEach((m) => {
          const opt = document.createElement("option");
          opt.value = m;
          opt.textContent = m;
          modelSelect.appendChild(opt);
        });
        if (curVal) modelSelect.value = curVal;
      }
    } catch {
      statusDot.className = "status-dot warn";
      statusEl.textContent = "Server unreachable · check terminal";
      statusEl.className = "status warn";
    }
  }

  // 2. Load authentic sample dishes
  async function loadSamples() {
    try {
      const data = await (await fetch("/api/samples")).json();
      const wrap = $("samples");
      wrap.innerHTML = "";
      data.samples.forEach((s) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sample-btn";
        btn.innerHTML = `<span class="sample-name">${escapeHtml(s.dish_name)}</span> <span class="sample-region">${escapeHtml(s.cuisine.split("/")[0])}</span>`;
        btn.addEventListener("click", async () => {
          $("restaurant").value = s.restaurant_name;
          $("cuisine").value = s.cuisine;
          $("dish").value = s.dish_name;
          $("category").value = s.category || "Mains & Curries";
          $("price").value = s.price || "";
          $("source-lang").value = s.source_language;
          $("targets").value = s.target_languages.join(", ");
          $("ingredients").value = s.ingredients;
          $("story").value = s.story;
          $("allergens").value = s.allergens_known;
          $("voice").value = s.voice;

          if (s.image) {
            try {
              const blob = await (await fetch(s.image)).blob();
              selectedFile = new File([blob], s.id + ".jpg", { type: blob.type || "image/jpeg" });
              showPreview(URL.createObjectURL(blob));
            } catch (err) {
              console.warn("Could not load sample image preview:", err);
            }
          }
          // Scroll smoothly to form
          $("pass").scrollIntoView({ behavior: "smooth" });
        });
        wrap.appendChild(btn);
      });
    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  }

  // 3. Image Drag & Drop Preview
  function showPreview(url) {
    preview.src = url;
    preview.hidden = false;
    dropCopy.hidden = true;
    clearImgBtn.hidden = false;
  }

  function clearImage() {
    selectedFile = null;
    imageInput.value = "";
    preview.src = "";
    preview.hidden = true;
    dropCopy.hidden = false;
    clearImgBtn.hidden = true;
  }

  dropzone.addEventListener("click", (e) => {
    if (e.target !== clearImgBtn) imageInput.click();
  });

  clearImgBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearImage();
  });

  imageInput.addEventListener("change", () => {
    const file = imageInput.files?.[0];
    if (!file) return;
    selectedFile = file;
    showPreview(URL.createObjectURL(file));
  });

  ["dragenter", "dragover"].forEach((ev) => {
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.add("drag");
    });
  });

  ["dragleave", "drop"].forEach((ev) => {
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.remove("drag");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    selectedFile = file;
    showPreview(URL.createObjectURL(file));
  });

  // 4. Form Utilities & Presets
  $("btn-clear-form").addEventListener("click", () => {
    $("restaurant").value = "";
    $("cuisine").value = "";
    $("dish").value = "";
    $("category").value = "Mains & Curries";
    $("price").value = "";
    $("source-lang").value = "";
    $("targets").value = "English, Spanish";
    $("ingredients").value = "";
    $("story").value = "";
    $("allergens").value = "";
    clearImage();
  });

  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      $("targets").value = btn.dataset.targets;
    });
  });

  $("btn-demo-hint").addEventListener("click", () => {
    $("force-demo").checked = true;
    statusEl.textContent = "Offline Demo Engine active — zero download required.";
    statusDot.className = "status-dot demo";
    $("pass").scrollIntoView({ behavior: "smooth" });
  });

  // 5. Generate Menu Action
  generateBtn.addEventListener("click", async () => {
    const dish = $("dish").value.trim();
    if (!dish) {
      alert("Please enter a dish name.");
      $("dish").focus();
      return;
    }

    generateBtn.disabled = true;
    btnSpinner.hidden = false;
    btnText.textContent = "Forging menu cards…";

    try {
      const fd = new FormData();
      fd.append("restaurant_name", $("restaurant").value);
      fd.append("cuisine", $("cuisine").value);
      fd.append("dish_name", dish);
      fd.append("category", $("category").value);
      fd.append("price", $("price").value);
      fd.append("source_language", $("source-lang").value || "auto");
      fd.append("target_languages", $("targets").value);
      fd.append("ingredients", $("ingredients").value);
      fd.append("story", $("story").value);
      fd.append("allergens_known", $("allergens").value);
      fd.append("voice", $("voice").value);
      fd.append("model", modelSelect.value);
      fd.append("force_demo", $("force-demo").checked ? "true" : "false");
      if (selectedFile) fd.append("image", selectedFile);

      const res = await fetch("/api/generate", { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText);
      }
      const data = await res.json();
      showResult(data);
      loadCatalog(); // Refresh catalog with new dish!
    } catch (err) {
      alert("Generation failed: " + (err.message || String(err)));
    } finally {
      generateBtn.disabled = false;
      btnSpinner.hidden = true;
      btnText.textContent = "Forge Menu Cards";
    }
  });

  // 6. Display Result in Output Panel
  function showResult(data) {
    $("empty").hidden = true;
    $("result").hidden = false;
    $("head-actions").hidden = false;

    const badge = $("mode-badge");
    badge.hidden = false;
    badge.textContent = data.mode === "ollama" ? "local open weights" : "demo engine";
    badge.className = "badge" + (data.mode === "demo" ? " demo" : " local");

    // Header info
    $("out-category").textContent = data.category || "Main Course";
    $("out-cuisine").textContent = data.cuisine || "Heritage";
    $("out-dish-name").textContent = data.original_dish;
    $("out-restaurant-name").textContent = data.restaurant_name || "Independent Kitchen";
    $("out-price").textContent = data.price || "";

    // Spice meter
    const spice = (data.spice_level || "varies").toLowerCase();
    let spiceEmoji = "🌶️";
    if (spice.includes("hot") || spice.includes("fire")) spiceEmoji = "🌶️🌶️🌶️ Hot";
    else if (spice.includes("med")) spiceEmoji = "🌶️🌶️ Medium";
    else if (spice.includes("mild")) spiceEmoji = "🌶️ Mild";
    else spiceEmoji = `🌶️ ${data.spice_level}`;
    $("out-spice").textContent = spiceEmoji;

    // Pronunciation & QR
    $("out-pronounce").textContent = data.staff_pronunciation || data.original_dish;
    $("out-qr").textContent = data.qr_one_liner || `${data.original_dish} — special of the house.`;

    // Chips
    renderChips($("out-allergens"), data.allergens, "allergen");
    renderChips($("out-dietary"), data.dietary_tags, "dietary");
    renderChips($("out-pairings"), data.pairings, "pairing");

    // Bilingual Cards
    const cardsWrap = $("out-cards");
    cardsWrap.innerHTML = "";
    (data.cards || []).forEach((c, idx) => {
      const cardEl = document.createElement("div");
      cardEl.className = "bilingual-card";
      cardEl.innerHTML = `
        <div class="card-head">
          <span class="card-lang">${escapeHtml(c.language)}</span>
          <button type="button" class="btn-copy-card" data-idx="${idx}" title="Copy this translation">Copy</button>
        </div>
        <h4 class="card-title">${escapeHtml(c.dish_name)}</h4>
        <div class="card-blurb-box">
          <span class="card-sub-label">Board / Chalkboard:</span>
          <p class="card-blurb">${escapeHtml(c.short_blurb)}</p>
        </div>
        <div class="card-desc-box">
          <span class="card-sub-label">Printed Menu Description:</span>
          <p class="card-desc">${escapeHtml(c.full_description)}</p>
        </div>
      `;
      cardsWrap.appendChild(cardEl);
    });

    // Model Footnote
    $("out-model").textContent = `Engine: ${data.model_used}`;
    window.__currentMenu = data;

    // Attach card copy handlers
    cardsWrap.querySelectorAll(".btn-copy-card").forEach((b) => {
      b.addEventListener("click", async () => {
        const idx = parseInt(b.dataset.idx, 10);
        const c = data.cards[idx];
        const text = `${c.dish_name} (${c.language})\nBoard: ${c.short_blurb}\nDescription: ${c.full_description}`;
        await navigator.clipboard.writeText(text);
        b.textContent = "Copied!";
        setTimeout(() => (b.textContent = "Copy"), 1200);
      });
    });
  }

  function renderChips(container, items, type) {
    container.innerHTML = "";
    if (!items || items.length === 0) {
      const li = document.createElement("li");
      li.className = "chip-empty";
      li.textContent = "None noted";
      container.appendChild(li);
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = `chip ${type}-chip`;
      li.textContent = item;
      container.appendChild(li);
    });
  }

  // 7. Speech Pronunciation (Web Speech API)
  $("btn-speak").addEventListener("click", () => {
    const d = window.__currentMenu;
    if (!d) return;
    const textToSpeak = d.staff_pronunciation || d.original_dish;
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(textToSpeak);
      utter.rate = 0.85; // slightly slower for clear server phonetics
      window.speechSynthesis.speak(utter);
      $("btn-speak").classList.add("speaking");
      utter.onend = () => $("btn-speak").classList.remove("speaking");
    } else {
      alert("Pronunciation: " + textToSpeak);
    }
  });

  // 8. Copy QR one-liner
  $("btn-copy-qr").addEventListener("click", async () => {
    const text = $("out-qr").textContent;
    if (!text) return;
    await navigator.clipboard.writeText(text);
    $("btn-copy-qr").textContent = "Copied!";
    setTimeout(() => ($("btn-copy-qr").textContent = "Copy"), 1200);
  });

  // 9. Copy All Cards as Markdown
  $("copy-all").addEventListener("click", async () => {
    const d = window.__currentMenu;
    if (!d) return;
    const lines = [
      `# ${d.restaurant_name || "Restaurant"} — ${d.original_dish}`,
      `**Course:** ${d.category} | **Price:** ${d.price} | **Spice:** ${d.spice_level}`,
      `**Pronunciation:** ${d.staff_pronunciation}`,
      `**QR / Board Line:** ${d.qr_one_liner}`,
      `**Allergens:** ${(d.allergens || []).join(", ")}`,
      `**Dietary:** ${(d.dietary_tags || []).join(", ")}`,
      `**Pairings:** ${(d.pairings || []).join(", ")}`,
      "",
      "---",
      "",
    ];
    (d.cards || []).forEach((c) => {
      lines.push(`### ${c.language}: ${c.dish_name}`);
      lines.push(`*Chalkboard:* ${c.short_blurb}`);
      lines.push("");
      lines.push(c.full_description);
      lines.push("");
    });
    await navigator.clipboard.writeText(lines.join("\n"));
    $("copy-all").textContent = "Copied All to Clipboard!";
    setTimeout(() => ($("copy-all").textContent = "📋 Copy All Cards (Markdown)"), 1500);
  });

  // 10. Restaurant Menu Catalog
  async function loadCatalog(categoryFilter = "all") {
    try {
      const url = categoryFilter && categoryFilter !== "all"
        ? `/api/history?category=${encodeURIComponent(categoryFilter)}`
        : "/api/history";
      const res = await fetch(url);
      const data = await res.json();
      catalogItems = data.items || [];
      $("catalog-count").textContent = catalogItems.length;
      renderCatalogGrid(catalogItems);
    } catch (err) {
      console.error("Failed to load catalog:", err);
    }
  }

  function renderCatalogGrid(items) {
    const grid = $("catalog-grid");
    grid.innerHTML = "";
    if (!items || items.length === 0) {
      grid.innerHTML = `<div class="catalog-empty">No dishes saved in this category yet. Forge your first dish above!</div>`;
      return;
    }

    items.forEach((item) => {
      const m = item.menu;
      const card = document.createElement("div");
      card.className = "catalog-card";
      card.innerHTML = `
        <div class="cat-card-header">
          <span class="cat-card-course">${escapeHtml(item.category || m.category || "Main Course")}</span>
          <span class="cat-card-price">${escapeHtml(item.price || m.price || "")}</span>
        </div>
        <h4 class="cat-card-title">${escapeHtml(item.dish_name)}</h4>
        <p class="cat-card-cuisine">${escapeHtml(m.cuisine || "Heritage")}</p>
        <p class="cat-card-blurb">${escapeHtml(m.qr_one_liner || (m.cards?.[0]?.short_blurb) || "")}</p>
        <div class="cat-card-meta">
          <span>🌶️ ${escapeHtml(m.spice_level || "varies")}</span>
          <span>${(m.cards || []).length} languages</span>
        </div>
        <div class="cat-card-actions">
          <button type="button" class="btn-cat-load" data-id="${item.id}">Load Pass</button>
          <button type="button" class="btn-cat-tent" data-id="${item.id}">Table Tent</button>
          <button type="button" class="btn-cat-del" data-id="${item.id}" title="Delete dish">×</button>
        </div>
      `;

      card.querySelector(".btn-cat-load").addEventListener("click", () => {
        showResult(m);
        $("pass").scrollIntoView({ behavior: "smooth" });
      });

      card.querySelector(".btn-cat-tent").addEventListener("click", () => {
        openTableTentModal(m);
      });

      card.querySelector(".btn-cat-del").addEventListener("click", async () => {
        if (confirm(`Remove "${item.dish_name}" from your catalog?`)) {
          await fetch(`/api/history/${item.id}`, { method: "DELETE" });
          loadCatalog();
        }
      });

      grid.appendChild(card);
    });
  }

  // Catalog category filter pills
  $("catalog-filters").querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      $("catalog-filters").querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      loadCatalog(btn.dataset.cat);
    });
  });

  // Export catalog
  $("btn-export-json").addEventListener("click", async () => {
    window.open("/api/export?format=json", "_blank");
  });

  $("btn-export-md").addEventListener("click", async () => {
    window.open("/api/export?format=markdown", "_blank");
  });

  $("btn-clear-catalog").addEventListener("click", async () => {
    if (confirm("Are you sure you want to clear your entire restaurant menu catalog?")) {
      await fetch("/api/history", { method: "DELETE" });
      loadCatalog();
    }
  });

  $("btn-print-full-menu").addEventListener("click", () => {
    openFullMenuModal();
  });

  // 11. Print Studio Modals (Table Tent, Waitstaff Pocket Card, Full Menu)
  function openTableTentModal(menuData = null) {
    const d = menuData || window.__currentMenu;
    if (!d) {
      alert("Please forge a dish first to generate a table tent.");
      return;
    }
    currentModalMode = "tent";
    modalTitle.textContent = "Print Studio · Foldable Table Tent Stand";
    studioModal.hidden = false;

    const enCard = d.cards?.[0] || { dish_name: d.original_dish, short_blurb: "", full_description: "" };
    const secondCard = d.cards?.[1] || enCard;

    modalContent.innerHTML = `
      <div class="print-tent-container">
        <!-- Front Panel -->
        <div class="tent-panel tent-front">
          <div class="tent-badge">Chef's Table Selection</div>
          <h2 class="tent-title">${escapeHtml(d.original_dish)}</h2>
          <p class="tent-rest">${escapeHtml(d.restaurant_name || "House Heritage")} · <span class="tent-price">${escapeHtml(d.price || "")}</span></p>
          <p class="tent-short">${escapeHtml(enCard.short_blurb)}</p>
          <p class="tent-desc">${escapeHtml(enCard.full_description)}</p>
          <div class="tent-footer">
            <span>Spice: ${escapeHtml(d.spice_level)}</span>
            <span>${escapeHtml(d.cuisine || "")}</span>
          </div>
        </div>

        <!-- Folding Divider -->
        <div class="tent-fold-line">
          <span>✂ FOLD HERE FOR TABLE STAND (4" x 6") ✂</span>
        </div>

        <!-- Back Panel -->
        <div class="tent-panel tent-back">
          <div class="tent-back-grid">
            <div class="tent-back-info">
              <div class="tent-badge">${escapeHtml(secondCard.language)} Translation</div>
              <h3 class="tent-sub-title">${escapeHtml(secondCard.dish_name)}</h3>
              <p class="tent-desc">${escapeHtml(secondCard.full_description)}</p>
              <div class="tent-meta-pills">
                <strong>Allergens:</strong> ${(d.allergens || []).join(", ") || "None declared"}
              </div>
              <div class="tent-meta-pills">
                <strong>Pairings:</strong> ${(d.pairings || []).join(", ") || "Ask server"}
              </div>
              <div class="tent-pronounce">
                <strong>Say it:</strong> <em>"${escapeHtml(d.staff_pronunciation)}"</em>
              </div>
            </div>
            <div class="tent-qr-box">
              <div id="tent-qr-canvas" class="qr-code-holder"></div>
              <span class="qr-caption">Scan for Digital Story</span>
            </div>
          </div>
        </div>
      </div>
    `;

    // Render real QR Code in pure client JS
    setTimeout(() => {
      const qrHolder = $("tent-qr-canvas");
      if (qrHolder && window.QRCode) {
        new window.QRCode(qrHolder, {
          text: `https://menuforge.local/dish/${encodeURIComponent(d.original_dish)}?v=1`,
          width: 110,
          height: 110,
          colorDark: "#0c1412",
          colorLight: "#ffffff",
        });
      }
    }, 50);
  }

  function openWaitstaffPocketCard(menuData = null) {
    const d = menuData || window.__currentMenu;
    if (!d) {
      alert("Please forge a dish first to view server pocket card.");
      return;
    }
    currentModalMode = "cheat";
    modalTitle.textContent = "Print Studio · Waitstaff Shift Pocket Card (3x5\")";
    studioModal.hidden = false;

    modalContent.innerHTML = `
      <div class="print-cheat-card">
        <div class="cheat-header">
          <div>
            <span class="cheat-cat">${escapeHtml(d.category || "Special")}</span>
            <h2 class="cheat-title">${escapeHtml(d.original_dish)}</h2>
          </div>
          <div class="cheat-price">${escapeHtml(d.price || "")}</div>
        </div>

        <div class="cheat-section pronounce-highlight">
          <span class="cheat-label">Phonetic Pronunciation:</span>
          <strong class="cheat-pronounce">${escapeHtml(d.staff_pronunciation)}</strong>
        </div>

        <div class="cheat-section">
          <span class="cheat-label">15-Second Table Pitch:</span>
          <p class="cheat-pitch">"${escapeHtml(d.cards?.[0]?.short_blurb || d.qr_one_liner)}"</p>
        </div>

        <div class="cheat-grid">
          <div class="cheat-col">
            <span class="cheat-label text-danger">Allergen Hazards:</span>
            <ul class="cheat-list">
              ${(d.allergens || []).map((a) => `<li>⚠️ ${escapeHtml(a)}</li>`).join("")}
            </ul>
          </div>
          <div class="cheat-col">
            <span class="cheat-label text-brass">Upsell Drink / Side:</span>
            <ul class="cheat-list">
              ${(d.pairings || []).map((p) => `<li>🍷 ${escapeHtml(p)}</li>`).join("")}
            </ul>
          </div>
        </div>

        <div class="cheat-footer">
          <span>Heat Level: ${escapeHtml(d.spice_level)}</span>
          <span>Dietary: ${(d.dietary_tags || []).join(", ")}</span>
        </div>
      </div>
    `;
  }

  function openFullMenuModal() {
    if (!catalogItems || catalogItems.length === 0) {
      alert("Your menu catalog is empty. Forge dishes to populate your restaurant menu.");
      return;
    }
    currentModalMode = "full";
    modalTitle.textContent = "Print Studio · Full Restaurant Menu";
    studioModal.hidden = false;

    // Group items by category
    const grouped = {};
    catalogItems.forEach((it) => {
      const cat = it.category || it.menu.category || "Main Course";
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(it.menu);
    });

    const restName = catalogItems[0]?.menu?.restaurant_name || "The Restaurant";

    let menuHtml = `
      <div class="print-full-menu">
        <header class="menu-print-header">
          <h1 class="menu-print-rest">${escapeHtml(restName)}</h1>
          <p class="menu-print-sub">Seasonal Heritage Menu · Prepared Fresh Daily</p>
        </header>
    `;

    for (const [catName, dishes] of Object.entries(grouped)) {
      menuHtml += `
        <section class="menu-print-category">
          <h3 class="menu-cat-title">${escapeHtml(catName)}</h3>
          <div class="menu-cat-items">
      `;
      dishes.forEach((d) => {
        const primaryCard = d.cards?.[0] || {};
        menuHtml += `
          <div class="menu-print-item">
            <div class="menu-item-row">
              <strong class="menu-item-name">${escapeHtml(d.original_dish)}</strong>
              <span class="menu-item-dots"></span>
              <span class="menu-item-price">${escapeHtml(d.price || "")}</span>
            </div>
            <p class="menu-item-blurb">${escapeHtml(primaryCard.short_blurb || d.qr_one_liner)}</p>
            <p class="menu-item-desc">${escapeHtml(primaryCard.full_description)}</p>
            <div class="menu-item-notes">
              <small>Spice: ${escapeHtml(d.spice_level)} | Allergens: ${(d.allergens || []).join(", ") || "None"}</small>
            </div>
          </div>
        `;
      });
      menuHtml += `
          </div>
        </section>
      `;
    }

    menuHtml += `
        <footer class="menu-print-footer">
          <p>Please inform your server of any dietary requirements or food allergies before ordering.</p>
        </footer>
      </div>
    `;

    modalContent.innerHTML = menuHtml;
  }

  // Modal interactions
  $("modal-close").addEventListener("click", () => {
    studioModal.hidden = true;
  });

  $("modal-print-btn").addEventListener("click", () => {
    window.print();
  });

  $("modal-switch-mode").addEventListener("click", () => {
    if (currentModalMode === "tent") openWaitstaffPocketCard();
    else if (currentModalMode === "cheat") openFullMenuModal();
    else openTableTentModal();
  });

  $("quick-tent-btn").addEventListener("click", () => openTableTentModal());
  $("quick-cheat-btn").addEventListener("click", () => openWaitstaffPocketCard());
  $("btn-open-tent").addEventListener("click", () => openTableTentModal());
  $("btn-open-cheat").addEventListener("click", () => openWaitstaffPocketCard());

  // Close modal on Escape
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !studioModal.hidden) {
      studioModal.hidden = true;
    }
  });

  // Helper escape
  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initialize
  refreshHealth();
  loadSamples();
  loadCatalog();
  setInterval(refreshHealth, 25000);
})();
