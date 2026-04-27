function sendDemoNotification() {
    if (!("Notification" in window)) {
        alert("Browser does not support notifications.");
        return;
    }

    if (Notification.permission === "granted") {
        new Notification("Medicine Reminder", {
            body: "Time to take your medicine.",
            icon: "/static/icon.png",
        });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then((permission) => {
            if (permission === "granted") {
                new Notification("Medicine Reminder", {
                    body: "Notifications enabled successfully!",
                });
            }
        });
    }
}

function voiceReminder(message) {
    if (!("speechSynthesis" in window)) {
        alert("Voice reminder is not supported in this browser.");
        return;
    }
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.rate = 1;
    speechSynthesis.speak(utterance);
}

function showEmergency(name, phone) {
    const target = document.getElementById("emergencyInfo");
    if (!name || !phone) {
        target.innerHTML = "<div class='alert alert-warning'>Please add emergency contact first.</div>";
        return;
    }
    target.innerHTML = `<div class='alert alert-danger'><strong>${name}</strong><br>${phone}</div>`;
}

async function loadHealthChart() {
    const canvas = document.getElementById("healthChart");
    if (!canvas) return;

    const response = await fetch("/health/data");
    const data = await response.json();
    new Chart(canvas, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: "Sugar",
                    data: data.sugar,
                    borderColor: "#0d6efd",
                    tension: 0.2,
                },
                {
                    label: "Weight",
                    data: data.weight,
                    borderColor: "#198754",
                    tension: 0.2,
                },
            ],
        },
    });
}

async function loadReportChart() {
    const canvas = document.getElementById("reportChart");
    if (!canvas) return;

    const response = await fetch("/report");
    const data = await response.json();
    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Taken", "Missed"],
            datasets: [{
                data: [data.taken, data.missed],
                backgroundColor: ["#198754", "#dc3545"],
            }],
        },
    });

    const text = document.getElementById("reportText");
    if (text) {
        text.textContent = `This week: ${data.taken} doses taken, ${data.missed} missed.`;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadHealthChart();
    await loadReportChart();
});
