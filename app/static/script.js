// Javascript file

function pullTables() {
    const year = document.getElementById('year-select').value;
    fetch("/pull_tables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ year: year})
    })
    .then(res => res.json())
    .then(data => {
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = data.success.join("<br>");

        const tableSelect = document.getElementById("table-select");
        tableSelect.innerHTML = "";
        data.tables.forEach(table => {
            const option = document.createElement("option");
            option.value = table;
            option.textContent = table;
            tableSelect.appendChild(option);
        });

        document.getElementById("table-viewer").style.display = "block";
        viewTable();
    })
}

function viewTable() {
    const tableName = document.getElementById("table-select").value;
    const FSMPyear = document.getElementById("year-select").value;
    fetch("/get_table", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table_name: tableName, FSMPyear: FSMPyear})
    })
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("data-table");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = "<tr><td>No data<td><tr>";
            return;
        }

        // Headers
        const headers = Object.keys(data[0]);
        const headerRow = document.createElement("tr");
        headers.forEach(h => {
            const th = document.createElement("th");
            th.textContent = h;
            headerRow.appendChild(th);            
        });
        table.appendChild(headerRow);

        // Rows
        data.forEach(row => {
            const tr = document.createElement("tr");
            headers.forEach(h => {
                const td = document.createElement("td");
                td.textContent = row[h];
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
    });
}

function goToCalculationPage() {
    window.location.href = "/calculate";
}

async function runAllSteps() {
    const steps = [
        { label: "IAT Modified Total Life" },
        { label: "CP DT Life" },
        { label: "CP Follow-on Life" },
        { label: "Inspection Intervals" },
        { label: "Hours at Next Inspection" },
        { label: "Hours to Next Inspection" }
    ];

    const progressDiv = document.getElementById("progress");
    progressDiv.innerHTML = "";

    for (const step in steps) {
        const stepMsg = document.createElement("div")
        stepMsg.innerText = `Calculating: ${step.label}...`;
        progressDiv.appendChild(stepMsg);

        try {
            const res = await fetch(`/run_step/${step.label}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
            const data = await res.json();

            stepMsg.innerText = data.message || `${step.label} complete!`;
        } catch (error) {
            stepMsg.innertext = `${step.label} calculation failed.`;
            console.error(`Error on ${step.label} calculation`, error);
            break;
        }
    }

    const doneMsg = document.createElement("div");
    doneMsg.innerText = "All calculation steps complete!";
    progressDiv.appendChild(doneMsg);
    
}

function viewCalcTable() {
    const tableName = document.getElementById("calc-table-select").value;
    if (!tableName) return;

    fetch("/get_calc_table", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ table_name: tableName})
    })
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("calc-data-table");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = "<tr><td>No data<td><tr>";
            return;
        }

        // Headers
        const headers = Object.keys(data[0]);
        const headerRow = document.createElement("tr");
        headers.forEach(h => {
            const th = document.createElement("th");
            th.textContent = h;
            headerRow.appendChild(th);            
        });
        table.appendChild(headerRow);

        // Rows
        data.forEach(row => {
            const tr = document.createElement("tr");
            headers.forEach(h => {
                const td = document.createElement("td");
                td.textContent = row[h];
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
    });
}