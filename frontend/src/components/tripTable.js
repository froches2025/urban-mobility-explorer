 const COLUMNS = [
    ["pickup_time", "Pickup time"],
    ["pickup_zone", "From"],
    ["dropoff_zone", "To"],
    ["distance", "Miles"],
    ["duration_min", "Minutes"],
    ["fare", "Fare ($)"],
    ["cost_per_mile", "$ per mile"],
    ["speed", "Avg mph"],
 ];

 export const PAGE_SIZE = 10;

 // state = { sort, order, page }; onChange(state) is called when the user sorts or pages.
 export function renderTable(container, data, state, onChange) {
    const pages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
    const head = COLUMNS.map(([key, label]) => {
        const active = state.sort === key;
        const arrow = active ? (state.order === "asc" ? " ▲" : " ▼") : "";
        return `<th data-key="${key}" tabindex="0"${active ? ` aria-sort="${state.order === "asc" ? "ascending" : "descending"}"` : ""}>${label}${arrow}</th>`;
    }).join("");
    const body = data.rows
      .map((r) => `<tr>${COLUMNS.map(([key]) => `<td>${r[key]}</td>`).join("")}</tr>`)
      .join("");

      container.innerHTML = `
        <div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body || '<tr><td colspan="8">No trips match these filters. Widen the ranges and apply again.</td></tr>'}</tbody></table></div>
        <div class="pager">
          <button class="ghost" id="prev" ${state.page <= 1 ? "disabled" : ""}>Previous</button>
          <span>Page ${state.page} of ${pages}</span>
          <button class="ghost" id="next" ${state.page >= pages ? "disabled" : ""}>Next</button>
        </div>`;

    container.querySelectorAll("th").forEach((th) => {
        const sortBy = () => { 
            const key = th.dataset.key;
            const order = state.sort === key && state.order === "desc" ? "asc" : "desc";
            onChange({ sort: key, order, page: 1 });
        };
        th.addEventListener("click", sortBy);
        th.addEventListener("keydown", (e) => e.key === "Enter" && sortBy());
    });
     container.querySelector("#prev").addEventListener("click", () => onChange({ ...state, page: state.page - 1 }));
     container.querySelector("#next").addEventListener("click", () => onChange({ ...state, page: state.page + 1 }));
 }