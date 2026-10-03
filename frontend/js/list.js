const studentsTable = document.querySelector("#students-table");
const filterForm = document.querySelector("#filters");
const statusLine = document.querySelector("#status");

const COLUMN_LABELS = [
    "ФИО",
    "Группа",
    "ИСУ id",
    "Общежитие",
    "Комната",
    "Срок заселения",
    "Иностранец",
    "Действия"
];

const FILTER_NAMES = ["full_name", "group", "dormitory", "room", "is_foreign", "living"];
const BOOLEAN_FILTERS = ["is_foreign", "living"];

function fillDormitoryFilter() {
    const select = filterForm.elements.dormitory;

    Object.keys(DORMITORIES).forEach(function (code) {
        const option = document.createElement("option");
        option.value = code;
        option.textContent = DORMITORIES[code];
        select.appendChild(option);
    });
}

function parseFilterValue(name, value) {
    if (BOOLEAN_FILTERS.indexOf(name) !== -1 && (value === "true" || value === "false")) {
        return value === "true";
    }

    return value;
}

function readFilters() {
    const params = new URLSearchParams(window.location.search);
    const filters = {};

    FILTER_NAMES.forEach(function (name) {
        const value = (params.get(name) || "").trim();
        filterForm.elements[name].value = value;

        if (value !== "") {
            filters[name] = parseFilterValue(name, value);
        }
    });

    return filters;
}

function describeError(error) {
    const parts = [error.message];

    for (let i = 0; i < error.details.length; i++) {
        parts.push(error.details[i].message);
    }

    return parts.join(". ");
}

function createCell(text, label) {
    const td = document.createElement("td");
    td.textContent = text;

    if (label) {
        td.dataset.label = label;
    }

    return td;
}

function createLink(text, href) {
    const a = document.createElement("a");
    a.textContent = text;
    a.href = href;
    return a;
}

function createActionsCell(student) {
    const td = document.createElement("td");
    td.dataset.label = COLUMN_LABELS[7];

    td.appendChild(createLink("Подробнее", "student-info.html?id=" + student.isu_id));
    td.appendChild(createLink("Редактировать", "student-form.html?id=" + student.isu_id));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Удалить";
    deleteButton.dataset.id = student.isu_id;
    td.appendChild(deleteButton);

    return td;
}

function showMessageRow(text) {
    const tbody = studentsTable.querySelector("tbody");
    const row = document.createElement("tr");
    const cell = createCell(text, "");

    cell.colSpan = COLUMN_LABELS.length;
    row.appendChild(cell);

    tbody.innerHTML = "";
    tbody.appendChild(row);
}

function showStudents(students) {
    const tbody = studentsTable.querySelector("tbody");

    if (students.length === 0) {
        showMessageRow("Студенты не найдены");
        return;
    }

    tbody.innerHTML = "";

    for (let i = 0; i < students.length; i++) {
        const student = students[i];
        const row = document.createElement("tr");

        row.appendChild(createCell(student.full_name, COLUMN_LABELS[0]));
        row.appendChild(createCell(student.group, COLUMN_LABELS[1]));
        row.appendChild(createCell(student.isu_id, COLUMN_LABELS[2]));
        row.appendChild(createCell(getDormitoryName(student.dormitory), COLUMN_LABELS[3]));
        row.appendChild(createCell(student.room, COLUMN_LABELS[4]));
        row.appendChild(createCell(formatPeriod(student.check_in, student.check_out), COLUMN_LABELS[5]));
        row.appendChild(createCell(student.is_foreign ? "да" : "нет", COLUMN_LABELS[6]));
        row.appendChild(createActionsCell(student));

        tbody.appendChild(row);
    }
}

async function loadStudents() {
    try {
        showStudents(await getStudents(currentFilters));
    } catch (error) {
        showMessageRow("Не удалось загрузить список");
        statusLine.textContent = describeError(error);
    }
}

async function onTableClick(event) {
    if (event.target.tagName !== "BUTTON") {
        return;
    }

    if (!confirm("Удалить студента?")) {
        return;
    }

    statusLine.textContent = "";

    try {
        await deleteStudent(event.target.dataset.id);
    } catch (error) {
        statusLine.textContent = describeError(error);
    }

    await loadStudents();
}

fillDormitoryFilter();
const currentFilters = readFilters();

studentsTable.addEventListener("click", onTableClick);
loadStudents();
