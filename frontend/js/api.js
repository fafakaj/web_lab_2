const API_URL = "/api/requests";
const QUERY_THRESHOLD = 3;

const DORMITORIES = {
    sg: "Студенческий городок",
    alp: "Общежитие № 2 (Альпийская)",
    bel: "Общежитие № 3 (Белорусская)",
    len: "Общежитие № 4 (Ленсовета)",
    msg: "Межвузовский студенческий городок"
};

class ApiError extends Error {
    constructor(status, message, details) {
        super(message);
        this.status = status;
        this.details = details;
    }
}

function getDormitoryName(code) {
    return DORMITORIES[code] || "—";
}

async function readError(response) {
    try {
        const data = await response.json();
        return new ApiError(response.status, data.error.message, data.error.details);
    } catch (error) {
        return new ApiError(response.status, "Ошибка сервера (код " + response.status + ")", []);
    }
}

async function request(method, url, body) {
    const options = { method: method };

    if (body !== undefined) {
        options.headers = { "Content-Type": "application/json" };
        options.body = JSON.stringify(body);
    }

    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new ApiError(0, "Сервер недоступен. Проверьте, что он запущен, и обновите страницу", []);
    }

    if (!response.ok) {
        throw await readError(response);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function studentUrl(isu) {
    return API_URL + "/" + encodeURIComponent(isu);
}

async function getStudents(filters) {
    const active = {};

    Object.keys(filters).forEach(function (name) {
        if (filters[name] !== "" && filters[name] !== null && filters[name] !== undefined) {
            active[name] = filters[name];
        }
    });

    if (Object.keys(active).length > QUERY_THRESHOLD) {
        return request("QUERY", API_URL, active);
    }

    const query = new URLSearchParams(active).toString();

    return request("GET", query === "" ? API_URL : API_URL + "?" + query);
}

async function getStudent(isu) {
    return request("GET", studentUrl(isu));
}

async function createStudent(data) {
    return request("POST", API_URL, data);
}

async function updateStudent(isu, data) {
    return request("PATCH", studentUrl(isu), data);
}

async function deleteStudent(isu) {
    return request("DELETE", studentUrl(isu));
}

function getIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    if (id === null || id === "") {
        return null;
    }

    return id;
}

function formatDate(isoDate) {
    if (!isoDate) {
        return "";
    }

    const parts = isoDate.split("-");

    if (parts.length !== 3) {
        return isoDate;
    }

    return parts[2] + "." + parts[1] + "." + parts[0];
}

function formatPeriod(from, to) {
    const start = formatDate(from);
    const end = formatDate(to);

    if (start === "" && end === "") {
        return "—";
    }

    if (end === "") {
        return start + " — по настоящее время";
    }

    if (start === "") {
        return end;
    }

    return start + " — " + end;
}
