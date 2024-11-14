let token = "";

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `grant_type=password&username=${username}&password=${password}`
    });

    if (response.ok) {
        const data = await response.json();
        token = data.access_token; // Обновите токен
        localStorage.setItem('token', token); // Сохраните токен
        document.getElementById('login-form').style.display = 'none'; // Скрыть форму входа
        document.getElementById('main-app').style.display = 'block'; // Показать основное приложение
        loadNotes(); // Загрузите заметки
    } else {
        const errorData = await response.json();
        console.error("Login failed:", errorData.detail);
        alert("Login failed: " + errorData.detail);
    }
}

function loadNotes() {
    fetch("http://127.0.0.1:8000/notes", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => response.json())
    .then(data => {
        const notesList = document.getElementById("notes-list");
        notesList.innerHTML = "";
        data.forEach(note => {
            const noteElement = document.createElement("div");
            noteElement.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content}</p>
                <button onclick="editNote(${note.id})">Edit</button>
                <button onclick="deleteNote(${note.id})">Delete</button>
            `;
            notesList.appendChild(noteElement);
        });
    });
}

function showAddNoteForm() {
    document.getElementById("note-form").style.display = "block";
    document.getElementById("note-title").value = ""; // Очищаем поля
    document.getElementById("note-content").value = "";
}

function hideNoteForm() {
    document.getElementById("note-form").style.display = "none";
}

function saveNote() {
    const title = document.getElementById("note-title").value;
    const content = document.getElementById("note-content").value;
    const noteId = document.getElementById("note-form").getAttribute("data-id"); // Получите id заметки

    const method = noteId ? "PUT" : "POST"; // Если id существует, используем PUT
    const url = noteId ? `http://127.0.0.1:8000/notes/${noteId}` : "http://127.0.0.1:8000/notes"; // Укажите URL

    fetch(url, {
        method: method,
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, content }),
    })
    .then(response => {
        if (response.ok) {
            hideNoteForm();
            loadNotes();
            // Очистить поля и сбросить ID
            document.getElementById("note-title").value = "";
            document.getElementById("note-content").value = "";
            document.getElementById("note-form").removeAttribute("data-id");
        } else {
            console.error("Failed to save note:", response.statusText);
        }
    });
}


// Функция редактирования заметки
function editNote(noteId) {
    fetch(`http://127.0.0.1:8000/notes/${noteId}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => response.json())
    .then(note => {
        document.getElementById("note-title").value = note.title;
        document.getElementById("note-content").value = note.content;
        document.getElementById("note-form").style.display = "block"; // Показать форму
        document.getElementById("note-form").setAttribute("data-id", noteId); // Сохранить id для обновления
    });
}

// Функция удаления заметки
function deleteNote(noteId) {
    if (confirm("Are you sure you want to delete this note?")) {
        fetch(`http://127.0.0.1:8000/notes/${noteId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        })
        .then(response => {
            if (response.ok) {
                loadNotes(); // Обновите список заметок
            } else {
                console.error("Failed to delete note:", response.statusText);
            }
        });
    }
}

