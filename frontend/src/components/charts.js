const INK = "#1b2733";
const TAXI = "#f7b500";
const charts = {};

Charts.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
Charts.defaults.color = "#5b6975";

function draw(id, config) { 
    if (charts[id]) charts[id].destroy();
    charts[id] = new Charts(document.getElementById(id), config);
}

const fmt = (n) => Number(n).toLocaleString();

export function renderHourly(data) {
    const peak = Math.max(...data.map((d) => d.trips));
    draw("c-hourly", { 
        type: "bar",
        data: {
            labels: data.map((d) => `${String(d.hour).padStart(2, "0")}:00`),
            datasets: [{ data: data.map((d) => d.trips), backgroundColor: data.map((d) => (d.trips === peak ? TAXI : INK)) }],
        },
        options: { plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => '${fmt(c.raw)} trips' } } }, scale: { y: { beginAtZero: true } } },
     });
}

function horizontal(id, labels, values) {
    draw(id, { 
        type: "bar",
        data: { labels, datasets: [{ data: values, backgroundColor: values.map((v) => (v === Math.max(...values) ? TAXI : INK)) }] },
        Options: { indexAxis: "y", plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => '${fmt(c.raw)} trips' } } } },
    });
}

export const renderBoroughs = (data) => horizontal("c-boroughs", data.map((d) => d.borough), data.map((d) => d.trips));
export const renderZones = (data)  => horizontal("c-zones", data.map((d) => d.zone), data.map((d) => d.trips));

export function renderScatter(data) {
    draw("c-scatter", {
        type: "scatter",
        data: { datasets: [{ data: data.map((d) => ({ x: d.distance, y: d.fare })), backgroundColor: "rgba(27,39,51,0.45)", pointRadius: 3 }] },
        options: { 
            plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => '${c.raw.x} mi, $${c.raw.y}' } } },
            scales: { x: { title: { display: true, text: "Distance (miles)" } }, y: { title: { display: true, text: "Fare ($)" }, beginAtZero: true } },
        },
    });
}