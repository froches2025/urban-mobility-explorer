import { getSummary, getHourly, getBoroughs, getTopZones, getFareDistance, getTrips, isMock } from "./services/api.js";
import { renderHourly, renderBoroughs, renderZones, renderScatter } from "./components/charts.js";
import { renderTable, PAGE_SIZE } from "./components/tripTable.js";

const form = document.getElementById("filters");
const tripsBox = document.getElementById("trips");
let tableState = { sort: "pickup_time", order: "desc", page: 1 };

const readFilters = () => Object.fromEntries(new FormData(form).entries());
const set = (id, text) => (document.getElementById(id).textContent = text);

async function loadTable() {
    const data = await getTrips(readFilters(), { ...tableState, limit: PAGE_SIZE });
    renderTable(tripsBox, data, tableState, (next) => { 
        tableState = { sort: next.sort, order: next.order, page: next.page };
        loadTable();
    });
}

async function loadAll() { 
    const f = readFilters();
    const [summary, hourly, boroughs, zones, scatter] = await Promise.all([
        getSummary(f), getHourly(f), getBoroughs(f), getTopZones(f), getFareDistance(f),
    ]);
    set( "m-trips", summary.trips.toLocaleString());
    set("m-fare", `$${summary.avg_fare.toFixed(2)}`); 
    set("m-dist", summary.avg_distance.toFixed(1));
    set("m-speed", summary.avg_speed.toFixed(1));
    renderHourly(hourly);
    renderBoroughs(boroughs);
    renderZones(zones);
    renderScatter(scatter);
    tableState.page =1;
    await loadTable();
    document.getElementById("banner").hidden = !isMock();
}

form.addEventListener("submit", (e) => { e.preventDefault(); loadAll(); });
form.addEventListener("reset", () => setTimeout(loadAll));
loadAll();