const NS = "http://www.w3.org/2000/svg";
let profileData = null;

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(NS, name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  return element;
}

function renderSpectrum(seriesName) {
  if (!profileData) return;
  const svg = document.querySelector("#spectrum-chart");
  const title = svg.querySelector("title").cloneNode(true);
  const desc = svg.querySelector("desc").cloneNode(true);
  svg.replaceChildren(title, desc);

  const width = 1000;
  const height = 420;
  const margin = { left: 78, right: 24, top: 24, bottom: 66 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const raw = profileData.series[seriesName];
  const values = raw.map((value) => Math.asinh(28 * Math.max(0, value)) / Math.asinh(28));
  const maxY = Math.max(1, ...values) * 1.04;

  const grid = svgElement("g", { stroke: "#d7dee6", "stroke-width": "1" });
  for (let i = 0; i <= 5; i += 1) {
    const x = margin.left + (plotWidth * i) / 5;
    const y = margin.top + (plotHeight * i) / 5;
    grid.append(svgElement("line", { x1: x, x2: x, y1: margin.top, y2: margin.top + plotHeight }));
    grid.append(svgElement("line", { x1: margin.left, x2: margin.left + plotWidth, y1: y, y2: y }));
  }
  svg.append(grid);

  const axes = svgElement("g", { stroke: "#24364a", "stroke-width": "1.5" });
  axes.append(svgElement("line", { x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotHeight }));
  axes.append(svgElement("line", { x1: margin.left, x2: margin.left + plotWidth, y1: margin.top + plotHeight, y2: margin.top + plotHeight }));
  svg.append(axes);

  const labels = svgElement("g", { fill: "#536174", "font-family": "Inter, Segoe UI, sans-serif", "font-size": "15" });
  for (let i = 0; i <= 5; i += 1) {
    const xValue = i / 5;
    const x = margin.left + plotWidth * xValue;
    const label = svgElement("text", { x, y: margin.top + plotHeight + 27, "text-anchor": "middle" });
    label.textContent = xValue.toFixed(1);
    labels.append(label);
  }
  const xLabel = svgElement("text", { x: margin.left + plotWidth / 2, y: height - 14, "text-anchor": "middle", fill: "#142033", "font-size": "16" });
  xLabel.textContent = "Normalized detector coordinate (not wavelength)";
  labels.append(xLabel);
  const yLabel = svgElement("text", { x: 19, y: margin.top + plotHeight / 2, transform: `rotate(-90 19 ${margin.top + plotHeight / 2})`, "text-anchor": "middle", fill: "#142033", "font-size": "16" });
  yLabel.textContent = "Asinh-scaled relative signal rate";
  labels.append(yLabel);
  svg.append(labels);

  const points = values.map((value, index) => {
    const x = margin.left + (plotWidth * index) / Math.max(values.length - 1, 1);
    const y = margin.top + plotHeight * (1 - value / maxY);
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });
  svg.append(svgElement("polyline", { points: points.join(" "), fill: "none", stroke: "#1e5e91", "stroke-width": "2.1", "stroke-linejoin": "round" }));
  document.querySelector("#series-label").textContent = seriesName;
}

function setPressed(buttons, selected) {
  buttons.forEach((button) => {
    const active = button === selected;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

const imageButtons = [...document.querySelectorAll(".image-choice")];
imageButtons.forEach((button) => button.addEventListener("click", () => {
  setPressed(imageButtons, button);
  document.querySelector("#detector-image").src = button.dataset.image;
  document.querySelector("#detector-caption").textContent = button.dataset.caption;
}));

const seriesButtons = [...document.querySelectorAll("[data-series]")];
seriesButtons.forEach((button) => button.addEventListener("click", () => {
  setPressed(seriesButtons, button);
  renderSpectrum(button.dataset.series);
}));

Promise.all([
  fetch("data/spectrum-profiles.json").then((response) => response.json()),
  fetch("data/science-metrics.json").then((response) => response.ok ? response.json() : null).catch(() => null),
])
  .then(([profiles, metrics]) => {
    profileData = profiles;
    renderSpectrum("HDR");
    if (metrics) {
      document.querySelectorAll('[data-metric="r2"]').forEach((node) => { node.textContent = Number(metrics.linearity_r_squared).toFixed(4); });
      document.querySelectorAll('[data-metric="shift"]').forEach((node) => { node.textContent = Number(metrics.registration_max_magnitude_px).toFixed(3); });
    }
  })
  .catch(() => {
    document.querySelector("#spectrum-chart").setAttribute("aria-label", "Spectrum profile unavailable. See the static profile figure below.");
  });
