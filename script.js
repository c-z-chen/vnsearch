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
    const fragment = document.createDocumentFragment(); // Memory-only container

    for (const item of nabokovWorks) {
        const lowerText = item.text.toLowerCase();
        let startIdx = lowerText.indexOf(query);

        while (startIdx !== -1) {
            found++;
            
            // 1. Create elements in memory
            const row = document.createElement('tr');
            const snippet = item.text.substring(
                Math.max(0, startIdx - 40),
                Math.min(item.text.length, startIdx + query.length + 60)
            );

            const highlighted = snippet.replace(
                new RegExp(query, 'gi'),
                m => `<mark>${m}</mark>`
            );

            row.innerHTML = `<td>...${highlighted}...</td><td class="meta">${item.title}</td>`;
            fragment.appendChild(row);

            // 2. Limit results to keep it snappy
            if (found >= 200) break; 

            startIdx = lowerText.indexOf(query, startIdx + query.length);
        }
        if (found >= 200) break;
    }

    // 3. One single DOM update
    results.appendChild(fragment);
    count.innerText = `Matches found: ${found}${found >= 200 ? '+' : ''}`;
}