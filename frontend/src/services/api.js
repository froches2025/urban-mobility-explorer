/*
* API service. Endpoints agreed with favour
*   GET /api/summary       -> { trips, avg_fare, avg_distance, avg_speed }
*   GET /api/hourly        -> [{ hour, trips }]            (24 items)
*   GET /api/boroughs      -> [{ boroughs, trips }]
*   GET /api/zones/top     -> [{ zone, trips }]
*   GET /api/fare-distance -> [{ distance, fare }]       (sampled points)
*   GET /api/trips         -> { total, rows: [{ pickup_time, pickup_zone, dropoff_zone,
                              distance, duration_min, fare, cost_per_mile, speed }] }
* Filter params on every endpoint: start, end, hour_min, hour_max, min_distance,
* max_distance, min_fare, max_fare, boroughs. /trips also takes sort, order, page, limits.
* If the backend is not reachable, sample data is used so the UI can be built early.
*/
const BASE = window.API_BASE || "http://localhost:5000/api";
let mock = false;
export const isMock = () => mock;

function toQuery(filters, extra = {}) { 
    const p = new URLSearchParams();
    Object.entries({ ...filters, ...extra }).forEach(([K, v]) => {
        if (v !== "" && v != null) p.set(K, v);
    });
     return p.toString();
}

function seeded(text) { 
    let h = 1779033703;
    for (const ch of text) h = Math.imul(h ^ ch.charCodeAt(0), 3432918353);
    let a = h >>> 0;
    return () => { 
       a = (a + 0x6d2b79f5) >>> 0;
       let t = Math.imul(a ^ (a >>> 15), 1 | a);
       t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
       return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

async function get(path, filters, extra, sample) {
    const query = toQuery(filters, extra);
    if (!mock) {
        try { 
            const res = await fetch(`${BASE}${path}?${query}`);
            if (!res.ok) throw new Error(res.status);
            return await res.json();
        } catch { 
            mock = true;
        }
    }
    return sample(seeded(query));
}

const ZONES = ["Upper East Side South", "Midtwon Center", "JFK Airport", "Penn Station", "Times Sq/Theatre District", "LaGuardia Aiport", "Upper West Side South", "Murrary Hill"];
const BOROUGHS = ["Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island", "EWR"];

export const getSummary = (f) => get("/summary", f, {}, (r) => ({  
    trips: Math.round(200000 + r() * 2000000),
    avg_fare: 17 + r() * 4,
    avg_distance: 3 + r() * 1.5,
    avg_speed: 10 + r() * 4,
}));

export const getHourly = (f) => get("/hourly", f, {}, (r) =>
    Array.from({ length: 24 }, (_, hour) => { 
        const wave = Math.exp(-((hour - 18) ** 2) / 14) + 0.6 * Math.exp(-((hour - 8.5) **2) / 8) + 0.1;
        return { hour, trips: Math.round(wave * 90000 * (0.9 + r() * 0.2)) };
    }));

    export const getBoroughs = (f) => get("/boroughs", f, {}, (r) =>
        BOROUGHS.map((borough, i) => ({ borough, trips: Math.round((900000 / (i * i * 2 + 1)) * (0.9 + r() * 0.2)) })));

    export const getTopZones = (f) => get("/zones/top", f, {}, (r) =>
        ZONES.map((zone, i) => ({ zone, trips: Math.round((120000 - i * 11000) * (0.9 + r() *0.2)) })));

    export const getFareDistance = (f) => get("/fare-distance", f, {}, (r) =>
    Array.from({ length: 150 }, () => { 
        const distance = +(0.3 + r() *r() * 18).toFixed(1);
        return { distance, fare: +(3 + 2.9 * distance + (r() - 0.5) * 8).toFixed(2) };
    }));

    export const getTrips = (f, { sort, order, page, limit }) => get("/trips", f, { sort, order, page, limit }, (r) => {
    const rows = Array.from({ length: limit }, (_, i) => { 
        const distance = +(0.4 + r() * 10).toFixed(1);
        const duration = Math.round(4 + distance * (3 + r() * 3));
        const fare = +(3 + 2.9 * distance + r() * 4).toFixed(2);
        return { 
            pickup_time: '2019-01-${String(1 + ((page * 7 + i) % 28)).padstart(2, "0")} ${String(Math.floor(r() *24)).padstart(2, "0")}:${string(Math.floor(r() * 60)).padstart(2, "0")}',
            pickup_zone: ZONES[Math.floor(r() *ZONES.length)],
            dropoff_zone: ZONES[Math.floor(r() * ZONES.length)],
            distance, duration_min: duration, fare,
            cost_per_mile: +(fare / distance).toFixed(2),
            speed: +(distance / (duration / 60)).toFixed(1),
        };
    });
    rows.sort((a, b) => (a[sort] > b[sort] ? 1 : -1) * (order === "asc" ? 1 : -1));
    return { total: 4800, rows };
});