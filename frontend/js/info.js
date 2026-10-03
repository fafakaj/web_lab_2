async function showStudent() {
    const id = getIdFromUrl();
    const main = document.querySelector("main");

    if (id === null) {
        main.textContent = "Студент не найден";
        return;
    }

    let student;

    try {
        student = await getStudent(id);
    } catch (error) {
        const notFound = error.status === 404 || error.status === 422;
        main.textContent = notFound ? "Студент не найден" : error.message;
        return;
    }

    document.querySelector("#info-full_name").textContent = student.full_name;
    document.querySelector("#info-group").textContent = student.group;
    document.querySelector("#info-isu_id").textContent = student.isu_id;
    document.querySelector("#info-dormitory").textContent = getDormitoryName(student.dormitory);
    document.querySelector("#info-room").textContent = student.room;
    document.querySelector("#info-period").textContent = formatPeriod(student.check_in, student.check_out);
    document.querySelector("#info-is_foreign").textContent = student.is_foreign ? "да" : "нет";
    document.querySelector("#info-notes").textContent = student.notes === "" ? "—" : student.notes;

    document.querySelector("#edit-link").href = "student-form.html?id=" + student.isu_id;
}

showStudent();
