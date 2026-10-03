const studentForm = document.querySelector("#student-form");
const errorBox = document.querySelector("#form-error");
const submitButton = studentForm.querySelector("button[type='submit']");

const FIELD_NAMES = ["full_name", "group", "isu_id", "dormitory", "room", "check_in", "check_out", "is_foreign", "notes"];

const isuInput = document.querySelector("#isu_id");
const checkInInput = document.querySelector("#check_in");
const checkOutInput = document.querySelector("#check_out");
const livingCheckbox = document.querySelector("#living");

const MAX_STAY_YEARS = 9;

const editId = getIdFromUrl();

function fillDormitories() {
    const select = document.querySelector("#dormitory");

    Object.keys(DORMITORIES).forEach(function (code) {
        const option = document.createElement("option");
        option.value = code;
        option.textContent = DORMITORIES[code];
        select.appendChild(option);
    });
}

function todayIso() {
    const now = new Date();
    return new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())).toISOString().slice(0, 10);
}

function addDays(isoDate, days) {
    const date = new Date(isoDate + "T00:00:00Z");
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
}

function addYears(isoDate, years) {
    const parts = isoDate.split("-").map(Number);
    const date = new Date(Date.UTC(parts[0] + years, parts[1] - 1, parts[2]));

    if (date.getUTCMonth() !== parts[1] - 1) {
        date.setUTCDate(0);
    }

    return date.toISOString().slice(0, 10);
}

function applyCheckOutLimits() {
    if (checkInInput.value === "") {
        checkOutInput.removeAttribute("min");
        checkOutInput.removeAttribute("max");
        return;
    }

    checkOutInput.min = addDays(checkInInput.value, 1);
    checkOutInput.max = addYears(checkInInput.value, MAX_STAY_YEARS);
}

function applyLivingState() {
    checkOutInput.disabled = livingCheckbox.checked;
    checkOutInput.required = !livingCheckbox.checked;

    if (livingCheckbox.checked) {
        checkOutInput.value = "";
        checkOutInput.classList.remove("has-error");
        document.querySelector("#error-check_out").textContent = "";
    }
}

async function fillForm() {
    if (editId === null) {
        return;
    }

    document.querySelector("#form-title").textContent = "Редактирование студента";
    isuInput.readOnly = true;

    let student;

    try {
        student = await getStudent(editId);
    } catch (error) {
        errorBox.textContent = error.status === 404 || error.status === 422 ? "Студент не найден" : error.message;
        return;
    }

    document.querySelector("#full_name").value = student.full_name;
    document.querySelector("#group").value = student.group;
    isuInput.value = student.isu_id;
    document.querySelector("#dormitory").value = student.dormitory;
    document.querySelector("#room").value = student.room;
    checkInInput.value = student.check_in;
    checkOutInput.value = student.check_out === null ? "" : student.check_out;
    livingCheckbox.checked = student.check_out === null;
    applyLivingState();
    applyCheckOutLimits();
    document.querySelector("#is_foreign").checked = student.is_foreign;
    document.querySelector("#notes").value = student.notes;
}

function collectData() {
    const data = {};

    if (editId === null) {
        data.isu_id = isuInput.value;
    }

    data.full_name = document.querySelector("#full_name").value;
    data.group = document.querySelector("#group").value;
    data.dormitory = document.querySelector("#dormitory").value;
    data.room = document.querySelector("#room").value;
    data.check_in = checkInInput.value;
    data.check_out = livingCheckbox.checked ? null : checkOutInput.value;
    data.is_foreign = document.querySelector("#is_foreign").checked;
    data.notes = document.querySelector("#notes").value;

    return data;
}

function clearErrors() {
    errorBox.textContent = "";

    FIELD_NAMES.forEach(function (name) {
        document.querySelector("#error-" + name).textContent = "";
        document.querySelector("#" + name).classList.remove("has-error");
    });
}

function showFieldErrors(details) {
    details.forEach(function (detail) {
        if (FIELD_NAMES.indexOf(detail.field) === -1) {
            errorBox.textContent = detail.message;
            return;
        }

        document.querySelector("#error-" + detail.field).textContent = detail.message;
        document.querySelector("#" + detail.field).classList.add("has-error");
    });
}

function showServerError(error) {
    if ((error.status === 422 || error.status === 409) && error.details.length > 0) {
        showFieldErrors(error.details);
        return;
    }

    errorBox.textContent = error.message;
}

async function onSubmit(event) {
    event.preventDefault();
    clearErrors();
    submitButton.disabled = true;

    try {
        if (editId === null) {
            await createStudent(collectData());
        } else {
            await updateStudent(editId, collectData());
        }
    } catch (error) {
        submitButton.disabled = false;
        showServerError(error);
        return;
    }

    window.location.href = "index.html";
}

function markSubmitted() {
    studentForm.classList.add("was-submitted");
}

studentForm.addEventListener("invalid", markSubmitted, true);
studentForm.addEventListener("submit", markSubmitted);
studentForm.addEventListener("submit", onSubmit);
livingCheckbox.addEventListener("change", applyLivingState);
checkInInput.addEventListener("change", applyCheckOutLimits);

fillDormitories();
checkInInput.max = addYears(todayIso(), 1);
fillForm();
