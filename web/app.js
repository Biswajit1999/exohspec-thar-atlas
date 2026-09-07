const fallback = {
  recommended_single_exposure_seconds: 120,
  exposures: [
    { exposure_seconds: 30, display_role: "protects bright line cores" },
    { exposure_seconds: 60, display_role: "bridges bright and faint regimes" },
    { exposure_seconds: 120, display_role: "best single-frame balance" },
    { exposure_seconds: 180, display_role: "reveals faint structure" },
  ],
};

const titles = {
  "protects bright line cores": "Bright-core guard",
  "bridges bright and faint regimes": "Bridge exposure",
  "best single-frame balance": "Best single frame",
  "reveals faint structure": "Faint-feature reach",
};

function renderSummary(summary) {
  const best = Number(summary.recommended_single_exposure_seconds);
  document.querySelector("#best-single").textContent = `${best} s`;

  const cards = document.querySelector("#exposure-cards");
  cards.replaceChildren(
    ...summary.exposures.map((item) => {
      const article = document.createElement("article");
      article.className = `verdict-card${Number(item.exposure_seconds) === best ? " featured" : ""}`;
      const time = document.createElement("span");
      time.textContent = `${Number(item.exposure_seconds)} s`;
      const title = document.createElement("h3");
      title.textContent = titles[item.display_role] || "Exposure role";
      const copy = document.createElement("p");
      copy.textContent = item.display_role.charAt(0).toUpperCase() + item.display_role.slice(1) + ".";
      article.append(time, title, copy);
      return article;
    }),
  );
}

fetch("data/summary.json")
  .then((response) => {
    if (!response.ok) throw new Error(`summary request failed: ${response.status}`);
    return response.json();
  })
  .then(renderSummary)
  .catch(() => renderSummary(fallback));

