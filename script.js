const input = document.getElementById('q');
const results = document.getElementById('results');
const count = document.getElementById('count');
let debounceTimer;

input.oninput = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(performSearch, 200); // Wait 200ms after typing stops
};

function performSearch() {
    const query = input.value.toLowerCase().trim();
    results.innerHTML = "";
    
    // Safety check: don't search for tiny strings in huge datasets
    if (query.length < 3) { 
        count.innerText = "Type at least 3 characters...";
        return;
    }

    let found = 0;
    const countsByTitle = new Map();
    const fragment = document.createDocumentFragment(); // Memory-only container
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    for (const item of nabokovWorks) {
        const lowerText = item.text.toLowerCase();
        let startIdx = lowerText.indexOf(query);

        while (startIdx !== -1) {
            found++;
            countsByTitle.set(item.title, (countsByTitle.get(item.title) || 0) + 1);
            
            // 1. Create elements in memory
            const row = document.createElement('tr');
            const snippet = item.text.substring(
                Math.max(0, startIdx - 40),
                Math.min(item.text.length, startIdx + query.length + 60)
            );

            const highlighted = snippet.replace(
                new RegExp(escapedQuery, 'gi'),
                m => `<mark>${m}</mark>`
            );

            const structureHtml = item.structure
                ? `<span class="work-structure meta">${item.structure}</span>`
                : "";

            row.innerHTML = `<td>...${highlighted}...</td><td class="work-cell"><span class="work-title">${item.title}</span>${structureHtml}</td>`;
            fragment.appendChild(row);

            // 2. Limit results to keep it snappy
            if (found >= 200) break; 

            startIdx = lowerText.indexOf(query, startIdx + query.length);
        }
        if (found >= 200) break;
    }

    // 3. One single DOM update
    results.appendChild(fragment);

    const breakdown = Array.from(countsByTitle.entries())
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .map(([title, total]) => `${title}: ${total}`)
        .join(', ');

    count.innerText = breakdown
        ? `Matches found: ${found}${found >= 200 ? '+' : ''} (${breakdown})`
        : `Matches found: ${found}${found >= 200 ? '+' : ''}`;
}