console.log("dashboard.js loaded");

const token = localStorage.getItem("token");

const statusEl = document.getElementById("status");
const titleEl = document.getElementById("title");

/* ---------------- ADMIN DOM ---------------- */
const adminView = document.getElementById("adminView");
const normalView = document.getElementById("normalView"); // may still exist in your HTML

const studentsListEl = document.getElementById("studentsList");
const studentMsgEl = document.getElementById("studentMsg");

const teachersListEl = document.getElementById("teachersList");
const teacherMsgEl = document.getElementById("teacherMsg");

const classroomsListEl = document.getElementById("classroomsList");
const classroomMsgEl = document.getElementById("classroomMsg");

// caches for search + filtering + instant re-render
let cachedStudents = [];
let cachedTeachers = [];
let cachedClassrooms = [];

/* ---------------- HELPERS ---------------- */

function authHeaders(extra = {}) {
  const t = localStorage.getItem("token");
  return {
    ...extra,
    ...(t ? { Authorization: `Bearer ${t}` } : {}),
  };
}

async function requestJson(url, options = {}) {
  const res = await fetch(url, options);
  let data = null;

  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const msg = data?.detail || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}

function showTab(tabId) {
  document.querySelectorAll(".panel").forEach((p) => (p.style.display = "none"));
  const el = document.getElementById(tabId);
  if (el) el.style.display = "block";
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

function esc(x) {
  return String(x ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function buildIndexes() {
  // students per classroom.id
  const studentsByClassroom = new Map();
  for (const s of cachedStudents) {
    const key = s.classroom_id;
    studentsByClassroom.set(key, (studentsByClassroom.get(key) || 0) + 1);
  }

  // classrooms per teacher.id
  const classroomsByTeacher = new Map();
  for (const c of cachedClassrooms) {
    const key = c.teacher_id;
    classroomsByTeacher.set(key, (classroomsByTeacher.get(key) || 0) + 1);
  }

  return { studentsByClassroom, classroomsByTeacher };
}

/* ---------------- EDIT PANEL (shared) ---------------- */

const editPanel = document.getElementById("editPanel");
const editTitleEl = document.getElementById("editTitle");
const editForm = document.getElementById("editForm");
const editFieldsEl = document.getElementById("editFields");
const editCancelBtn = document.getElementById("editCancelBtn");
const editMsgEl = document.getElementById("editMsg");

function showEditPanel(title, fieldsHtml, onSave) {
  editTitleEl.innerText = title;
  editFieldsEl.innerHTML = fieldsHtml;
  editMsgEl.innerText = "";
  editPanel.style.display = "block";

  editForm.onsubmit = async (e) => {
    e.preventDefault();
    editMsgEl.innerText = "";
    try {
      await onSave();
      editMsgEl.innerText = "Updated ✅";
      setTimeout(() => (editMsgEl.innerText = ""), 1200);
      editPanel.style.display = "none";
    } catch (err) {
      editMsgEl.innerText = err.message || "Update failed";
    }
  };
}

function hideEditPanel() {
  editPanel.style.display = "none";
  editFieldsEl.innerHTML = "";
  editMsgEl.innerText = "";
}

if (editCancelBtn) editCancelBtn.addEventListener("click", hideEditPanel);

/* ---------------- STUDENTS (ADMIN) ---------------- */

function renderStudents(students) {
  studentsListEl.innerHTML = "";

  if (!students || students.length === 0) {
    studentsListEl.innerHTML = "<li>No students yet.</li>";
    return;
  }

  for (const s of students) {
    const li = document.createElement("li");
    li.innerText = `#${s.id} ${s.name} (age ${s.age}) classroom_id=${s.classroom_id} enrolled=${s.is_enrolled}`;

    const editBtn = document.createElement("button");
    editBtn.innerText = "Edit";
    editBtn.style.marginLeft = "10px";

    editBtn.addEventListener("click", () => {
      showEditPanel(
        `Edit student #${s.id}`,
        `
          <label>Name</label><br>
          <input type="text" id="editStudentName" value="${esc(s.name)}" required><br><br>

          <label>Age</label><br>
          <input type="number" id="editStudentAge" value="${esc(s.age)}" required><br><br>

          <label>Enrolled</label><br>
          <select id="editStudentEnrolled">
            <option value="true" ${s.is_enrolled ? "selected" : ""}>true</option>
            <option value="false" ${!s.is_enrolled ? "selected" : ""}>false</option>
          </select><br><br>

          <label>Classroom ID</label><br>
          <input type="number" id="editStudentClassroomId" value="${esc(s.classroom_id)}" required><br><br>
        `,
        async () => {
          const payload = {
            name: document.getElementById("editStudentName").value,
            age: Number(document.getElementById("editStudentAge").value),
            is_enrolled: document.getElementById("editStudentEnrolled").value === "true",
            classroom_id: Number(document.getElementById("editStudentClassroomId").value),
          };

          const updated = await requestJson(`/students/${s.id}`, {
            method: "PUT",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(payload),
          });

          cachedStudents = cachedStudents.map((x) => (x.id === updated.id ? updated : x));
          applyStudentFilter();
        }
      );
    });

    const delBtn = document.createElement("button");
    delBtn.innerText = "Delete";
    delBtn.style.marginLeft = "10px";

    delBtn.addEventListener("click", async () => {
      studentMsgEl.innerText = "";
      try {
        await requestJson(`/students/${s.id}`, {
          method: "DELETE",
          headers: authHeaders(),
        });

        studentMsgEl.innerText = `Deleted student ${s.id}`;
        await loadStudents();
      } catch (err) {
        studentMsgEl.innerText = err.message || "Network error deleting student";
      }
    });

    li.appendChild(editBtn);
    li.appendChild(delBtn);
    studentsListEl.appendChild(li);
  }
}

function applyStudentFilter() {
  const filterEl = document.getElementById("studentFilter");
  const f = filterEl ? filterEl.value : "all";

  let list = [...cachedStudents];
  if (f === "enrolled") list = list.filter((s) => s.is_enrolled === true);
  if (f === "not_enrolled") list = list.filter((s) => s.is_enrolled === false);

  renderStudents(list);
}

async function loadStudents() {
  studentMsgEl.innerText = "";
  try {
    const data = await requestJson("/students", { headers: authHeaders() });
    cachedStudents = data;
    applyStudentFilter();
  } catch (err) {
    studentMsgEl.innerText = err.message || "Network error loading students";
  }
}

async function addStudent(e) {
  e.preventDefault();
  studentMsgEl.innerText = "";

  const name = document.getElementById("studentName").value;
  const age = Number(document.getElementById("studentAge").value);
  const is_enrolled = document.getElementById("studentEnrolled").value === "true";
  const classroom_id = Number(document.getElementById("studentClassroomId").value);

  const payload = { name, age, is_enrolled, classroom_id };

  try {
    const data = await requestJson("/students", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    });

    studentMsgEl.innerText = `Added student #${data.id}`;
    e.target.reset();
    await loadStudents();
  } catch (err) {
    studentMsgEl.innerText = err.message || "Network error adding student";
  }
}

async function searchStudentById() {
  const msg = document.getElementById("studentSearchMsg");
  msg.innerText = "";

  const id = Number(document.getElementById("studentSearchId").value);
  if (!id) {
    msg.innerText = "Enter a valid student ID.";
    return;
  }

  if (!cachedStudents.length) await loadStudents();

  const found = cachedStudents.find((s) => s.id === id);
  msg.innerText = found
    ? `Found: #${found.id} ${found.name}, age ${found.age}, classroom_id=${found.classroom_id}, enrolled=${found.is_enrolled}`
    : `No student found with ID ${id}.`;
}

/* ---------------- TEACHERS (ADMIN) ---------------- */

function renderTeachers(teachers) {
  teachersListEl.innerHTML = "";

  if (!teachers || teachers.length === 0) {
    teachersListEl.innerHTML = "<li>No teachers yet.</li>";
    return;
  }

  const { classroomsByTeacher } = buildIndexes();

  for (const t of teachers) {
    const assignedCount = classroomsByTeacher.get(t.id) || 0;
    const badge = assignedCount > 0 ? `assigned(${assignedCount})` : "unassigned";

    const li = document.createElement("li");
    li.innerText = `#${t.id} ${t.name} (${t.email}) — ${badge}`;

    const editBtn = document.createElement("button");
    editBtn.innerText = "Edit";
    editBtn.style.marginLeft = "10px";

    editBtn.addEventListener("click", () => {
      showEditPanel(
        `Edit teacher #${t.id}`,
        `
          <label>Name</label><br>
          <input type="text" id="editTeacherName" value="${esc(t.name)}" required><br><br>

          <label>Email</label><br>
          <input type="email" id="editTeacherEmail" value="${esc(t.email)}" required><br><br>
        `,
        async () => {
          const payload = {
            name: document.getElementById("editTeacherName").value,
            email: document.getElementById("editTeacherEmail").value,
          };

          const updated = await requestJson(`/teachers/${t.id}`, {
            method: "PUT",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(payload),
          });

          cachedTeachers = cachedTeachers.map((x) => (x.id === updated.id ? updated : x));
          applyTeacherFilter();
        }
      );
    });

    const delBtn = document.createElement("button");
    delBtn.innerText = "Delete";
    delBtn.style.marginLeft = "10px";

    delBtn.addEventListener("click", async () => {
      teacherMsgEl.innerText = "";
      try {
        await requestJson(`/teachers/${t.id}`, {
          method: "DELETE",
          headers: authHeaders(),
        });

        teacherMsgEl.innerText = `Deleted teacher ${t.id}`;
        await loadTeachers();
      } catch (err) {
        teacherMsgEl.innerText = err.message || "Network error deleting teacher";
      }
    });

    li.appendChild(editBtn);
    li.appendChild(delBtn);
    teachersListEl.appendChild(li);
  }
}

function applyTeacherFilter() {
  const filterEl = document.getElementById("teacherFilter");
  const f = filterEl ? filterEl.value : "all";

  const { classroomsByTeacher } = buildIndexes();

  let list = [...cachedTeachers];
  if (f === "assigned") list = list.filter((t) => (classroomsByTeacher.get(t.id) || 0) > 0);
  if (f === "unassigned") list = list.filter((t) => (classroomsByTeacher.get(t.id) || 0) === 0);

  renderTeachers(list);
}

async function loadTeachers() {
  teacherMsgEl.innerText = "";
  try {
    const data = await requestJson("/teachers", { headers: authHeaders() });
    cachedTeachers = data;
    applyTeacherFilter();
  } catch (err) {
    teacherMsgEl.innerText = err.message || "Network error loading teachers";
  }
}

async function addTeacher(e) {
  e.preventDefault();
  teacherMsgEl.innerText = "";

  const name = document.getElementById("teacherName").value;
  const email = document.getElementById("teacherEmail").value;

  const payload = { name, email };

  try {
    const data = await requestJson("/teachers", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    });

    teacherMsgEl.innerText = `Added teacher #${data.id}`;
    e.target.reset();
    await loadTeachers();
  } catch (err) {
    teacherMsgEl.innerText = err.message || "Network error adding teacher";
  }
}

async function searchTeacherById() {
  const msg = document.getElementById("teacherSearchMsg");
  msg.innerText = "";

  const id = Number(document.getElementById("teacherSearchId").value);
  if (!id) {
    msg.innerText = "Enter a valid teacher ID.";
    return;
  }

  if (!cachedTeachers.length) await loadTeachers();

  const found = cachedTeachers.find((t) => t.id === id);
  msg.innerText = found
    ? `Found: #${found.id} ${found.name} (${found.email})`
    : `No teacher found with ID ${id}.`;
}

/* ---------------- CLASSROOMS (ADMIN) ---------------- */

function renderClassrooms(classrooms) {
  classroomsListEl.innerHTML = "";

  if (!classrooms || classrooms.length === 0) {
    classroomsListEl.innerHTML = "<li>No classrooms yet.</li>";
    return;
  }

  const { studentsByClassroom } = buildIndexes();

  for (const c of classrooms) {
    const count = studentsByClassroom.get(c.id) || 0;
    const status =
      count >= c.capacity ? "FULL" : count >= 0.8 * c.capacity ? "ALMOST FULL" : "AVAILABLE";

    const li = document.createElement("li");
    li.innerText = `#${c.id} ${c.name} grade=${c.grade} capacity=${c.capacity} teacher_id=${c.teacher_id} students=${count} → ${status}`;

    const editBtn = document.createElement("button");
    editBtn.innerText = "Edit";
    editBtn.style.marginLeft = "10px";

    editBtn.addEventListener("click", () => {
      showEditPanel(
        `Edit classroom #${c.id}`,
        `
          <label>Name</label><br>
          <input type="text" id="editClassroomName" value="${esc(c.name)}" required><br><br>

          <label>Grade</label><br>
          <input type="number" id="editClassroomGrade" value="${esc(c.grade)}" required><br><br>

          <label>Capacity</label><br>
          <input type="number" id="editClassroomCapacity" value="${esc(c.capacity)}" required><br><br>

          <label>Teacher ID</label><br>
          <input type="number" id="editClassroomTeacherId" value="${esc(c.teacher_id)}" required><br><br>
        `,
        async () => {
          const payload = {
            name: document.getElementById("editClassroomName").value,
            grade: Number(document.getElementById("editClassroomGrade").value),
            capacity: Number(document.getElementById("editClassroomCapacity").value),
            teacher_id: Number(document.getElementById("editClassroomTeacherId").value),
          };

          const updated = await requestJson(`/classrooms/${c.id}`, {
            method: "PUT",
            headers: authHeaders({ "Content-Type": "application/json" }),
            body: JSON.stringify(payload),
          });

          cachedClassrooms = cachedClassrooms.map((x) => (x.id === updated.id ? updated : x));
          applyClassroomFilter();
        }
      );
    });

    const delBtn = document.createElement("button");
    delBtn.innerText = "Delete";
    delBtn.style.marginLeft = "10px";

    delBtn.addEventListener("click", async () => {
      classroomMsgEl.innerText = "";
      try {
        await requestJson(`/classrooms/${c.id}`, {
          method: "DELETE",
          headers: authHeaders(),
        });

        classroomMsgEl.innerText = `Deleted classroom ${c.id}`;
        await loadClassrooms();
      } catch (err) {
        classroomMsgEl.innerText = err.message || "Network error deleting classroom";
      }
    });

    li.appendChild(editBtn);
    li.appendChild(delBtn);
    classroomsListEl.appendChild(li);
  }
}

function applyClassroomFilter() {
  const filterEl = document.getElementById("classroomFilter");
  const f = filterEl ? filterEl.value : "all";

  const { studentsByClassroom } = buildIndexes();

  let list = [...cachedClassrooms];

  if (f !== "all") {
    list = list.filter((c) => {
      const count = studentsByClassroom.get(c.id) || 0;
      if (f === "full") return count >= c.capacity;
      if (f === "almost") return count < c.capacity && count >= 0.8 * c.capacity;
      if (f === "available") return count < 0.8 * c.capacity;
      return true;
    });
  }

  renderClassrooms(list);
}

async function loadClassrooms() {
  classroomMsgEl.innerText = "";
  try {
    const data = await requestJson("/classrooms", { headers: authHeaders() });
    cachedClassrooms = data;
    applyClassroomFilter();
  } catch (err) {
    classroomMsgEl.innerText = err.message || "Network error loading classrooms";
  }
}

async function addClassroom(e) {
  e.preventDefault();
  classroomMsgEl.innerText = "";

  const name = document.getElementById("classroomName").value;
  const grade = Number(document.getElementById("classroomGrade").value);
  const capacity = Number(document.getElementById("classroomCapacity").value);
  const teacher_id = Number(document.getElementById("classroomTeacherId").value);

  const payload = { name, grade, capacity, teacher_id };

  try {
    const data = await requestJson("/classrooms", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    });

    classroomMsgEl.innerText = `Added classroom #${data.id}`;
    e.target.reset();
    await loadClassrooms();
  } catch (err) {
    classroomMsgEl.innerText = err.message || "Network error adding classroom";
  }
}

async function searchClassroomById() {
  const msg = document.getElementById("classroomSearchMsg");
  msg.innerText = "";

  const id = Number(document.getElementById("classroomSearchId").value);
  if (!id) {
    msg.innerText = "Enter a valid classroom ID.";
    return;
  }

  if (!cachedClassrooms.length) await loadClassrooms();

  const found = cachedClassrooms.find((c) => c.id === id);
  msg.innerText = found
    ? `Found: #${found.id} ${found.name}, grade=${found.grade}, capacity=${found.capacity}, teacher_id=${found.teacher_id}`
    : `No classroom found with ID ${id}.`;
}

/* ---------------- TEACHER VIEW (NON-ADMIN) ---------------- */

const teacherView = document.getElementById("teacherView");
const teacherClassroomsEl = document.getElementById("teacherClassrooms");
const teacherStudentsSection = document.getElementById("teacherStudentsSection");
const teacherStudentsEl = document.getElementById("teacherStudents");
const teacherViewMsgEl = document.getElementById("teacherViewMsg");
const teacherAddStudentForm = document.getElementById("teacherAddStudentForm");

let currentTeacherClassroomId = null;

async function loadTeacherClassrooms() {
  if (!teacherClassroomsEl) return;

  teacherClassroomsEl.innerHTML = "";
  if (teacherStudentsEl) teacherStudentsEl.innerHTML = "";
  if (teacherStudentsSection) teacherStudentsSection.style.display = "none";
  if (teacherViewMsgEl) teacherViewMsgEl.innerText = "";

  try {
    const classrooms = await requestJson("/my/classrooms", {
      headers: authHeaders(),
    });

    if (classrooms.length === 0) {
      teacherClassroomsEl.innerHTML = "<li>No classrooms assigned.</li>";
      return;
    }

    for (const c of classrooms) {
      const li = document.createElement("li");
      li.innerText = `${c.name} (Grade ${c.grade}, Capacity ${c.capacity})`;

      const btn = document.createElement("button");
      btn.innerText = "View students";
      btn.style.marginLeft = "10px";
      btn.addEventListener("click", () => loadTeacherStudents(c.id));

      li.appendChild(btn);
      teacherClassroomsEl.appendChild(li);
    }
  } catch (err) {
    teacherClassroomsEl.innerHTML = `<li>${err.message}</li>`;
  }
}

async function loadTeacherStudents(classroomId) {
  currentTeacherClassroomId = classroomId;
  if (teacherStudentsEl) teacherStudentsEl.innerHTML = "";
  if (teacherStudentsSection) teacherStudentsSection.style.display = "block";
  if (teacherViewMsgEl) teacherViewMsgEl.innerText = "";

  try {
    const students = await requestJson(`/my/classrooms/${classroomId}/students`, {
      headers: authHeaders(),
    });

    if (!students || students.length === 0) {
      teacherStudentsEl.innerHTML = "<li>No students yet.</li>";
      return;
    }

    for (const s of students) {
      const li = document.createElement("li");
      li.innerText = `${s.name} (age ${s.age}) enrolled=${s.is_enrolled}`;

      const delBtn = document.createElement("button");
      delBtn.innerText = "Delete";
      delBtn.style.marginLeft = "10px";

      delBtn.addEventListener("click", async () => {
        if (teacherViewMsgEl) teacherViewMsgEl.innerText = "";
        try {
          await requestJson(`/my/students/${s.id}`, {
            method: "DELETE",
            headers: authHeaders(),
          });
          await loadTeacherStudents(currentTeacherClassroomId);
        } catch (err) {
          if (teacherViewMsgEl) teacherViewMsgEl.innerText = err.message;
        }
      });

      li.appendChild(delBtn);
      teacherStudentsEl.appendChild(li);
    }
  } catch (err) {
    teacherStudentsEl.innerHTML = `<li>${err.message}</li>`;
  }
}

if (teacherAddStudentForm) {
  teacherAddStudentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (teacherViewMsgEl) teacherViewMsgEl.innerText = "";

    if (!currentTeacherClassroomId) {
      if (teacherViewMsgEl) teacherViewMsgEl.innerText = "Select a classroom first.";
      return;
    }

    const payload = {
      name: document.getElementById("tStudentName").value,
      age: Number(document.getElementById("tStudentAge").value),
      is_enrolled: document.getElementById("tStudentEnrolled").value === "true",
      classroom_id: currentTeacherClassroomId,
    };

    try {
      await requestJson("/my/students", {
        method: "POST",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(payload),
      });

      e.target.reset();
      await loadTeacherStudents(currentTeacherClassroomId);
    } catch (err) {
      if (teacherViewMsgEl) teacherViewMsgEl.innerText = err.message;
    }
  });
}

/* ---------------- AUTH CHECK ---------------- */

async function checkLogin() {
  if (!token) {
    logout();
    return;
  }

  try {
    const data = await requestJson("/api/me", {
      headers: authHeaders(),
    });

    statusEl.innerText = "Logged in ✅";
    setTimeout(() => (statusEl.innerText = ""), 1000);

    if (data.is_admin) {
      titleEl.innerText = "Admin dashboard";

      if (teacherView) teacherView.style.display = "none";
      if (normalView) normalView.style.display = "none";
      adminView.style.display = "block";

      showTab("studentsPanel");

      await loadStudents();
      await loadTeachers();
      await loadClassrooms();

      applyStudentFilter();
      applyTeacherFilter();
      applyClassroomFilter();
    } else {
      titleEl.innerText = "Teacher dashboard";

      adminView.style.display = "none";
      if (normalView) normalView.style.display = "none";
      if (teacherView) teacherView.style.display = "block";
      else if (normalView) normalView.style.display = "block"; // fallback if you didn't add teacherView

      await loadTeacherClassrooms();
    }
  } catch {
    logout();
  }
}

/* ---------------- WIRING (ADMIN) ---------------- */

document.getElementById("logoutBtn").addEventListener("click", logout);

document.querySelectorAll(".tabBtn").forEach((btn) => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

document.getElementById("refreshStudentsBtn").addEventListener("click", loadStudents);
document.getElementById("addStudentForm").addEventListener("submit", addStudent);
document.getElementById("searchStudentBtn").addEventListener("click", searchStudentById);

document.getElementById("refreshTeachersBtn").addEventListener("click", loadTeachers);
document.getElementById("addTeacherForm").addEventListener("submit", addTeacher);
document.getElementById("searchTeacherBtn").addEventListener("click", searchTeacherById);

document.getElementById("refreshClassroomsBtn").addEventListener("click", loadClassrooms);
document.getElementById("addClassroomForm").addEventListener("submit", addClassroom);
document.getElementById("searchClassroomBtn").addEventListener("click", searchClassroomById);

// Filter wiring (only if dropdowns exist)
const sf = document.getElementById("studentFilter");
if (sf) sf.addEventListener("change", applyStudentFilter);

const tf = document.getElementById("teacherFilter");
if (tf) tf.addEventListener("change", applyTeacherFilter);

const cf = document.getElementById("classroomFilter");
if (cf) cf.addEventListener("change", applyClassroomFilter);

// Start
checkLogin();
