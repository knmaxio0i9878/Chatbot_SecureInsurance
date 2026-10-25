function toggleChat() {
    const chat = document.getElementById("chatbot");
    chat.style.display = chat.style.display === "block" ? "none" : "block";
}

async function askQuestion() {
    const input = document.getElementById("question");
    const messages = document.getElementById("chat-messages");

    const question = input.value.trim();

    if (!question) return;

    messages.innerHTML += `<div><b>You:</b> ${question}</div>`;
    input.value = "";

    const response = await fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
    });

    const data = await response.json();

    messages.innerHTML += `<div class="bot"><b>AI:</b> ${data.answer}</div>`;
    messages.scrollTop = messages.scrollHeight;
}