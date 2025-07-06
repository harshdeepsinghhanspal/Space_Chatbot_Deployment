const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMessage = userInput.value.trim();
  if (!userMessage) return;

  addMessage("user", userMessage);
  userInput.value = "";

  try {
    const response = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userMessage })
    });

    const data = await response.json();
    addMessage("bot", data.response);
  } catch (err) {
    addMessage("bot", "❌ Failed to fetch response.");
    console.error(err);
  }
});

function addMessage(sender, text) {
  const message = document.createElement("div");
  message.classList.add("message", sender);

  const content = document.createElement("span");
  message.appendChild(content);
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (sender === "bot") {
    typeWriter(text, content); // Keep your nice typewriter effect
  } else {
    content.innerHTML = formatText(text); // Instantly show user's message
  }
}

function typeWriter(text, element, i = 0) {
  const parser = new DOMParser();
  const formatted = formatText(text);
  const doc = parser.parseFromString(formatted, 'text/html');
  const htmlContent = doc.body.innerHTML;

  let current = "";
  const interval = setInterval(() => {
    current += htmlContent[i];
    element.innerHTML = current;
    chatBox.scrollTop = chatBox.scrollHeight;
    i++;
    if (i >= htmlContent.length) {
      clearInterval(interval);

      // ✅ Append copy button only after typing completes
      const copyBtn = document.createElement("button");
      copyBtn.innerText = "📋 Copy";
      copyBtn.classList.add("copy-btn");
      copyBtn.onclick = () => {
        navigator.clipboard.writeText(element.innerText).then(() => {
          copyBtn.innerText = "✅ Copied!";
          setTimeout(() => (copyBtn.innerText = "📋 Copy"), 1500);
        });
      };
      element.parentElement.appendChild(copyBtn);
    }
  }, 5);
}


function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>')
    .replace(/\n/g, "<br>");
}

document.getElementById("clear-chat").addEventListener("click", () => {
  // Add fade-out class to each message
  const messages = chatBox.querySelectorAll(".message");
  messages.forEach((msg, index) => {
    setTimeout(() => {
      msg.classList.add("fade-out");
    }, index * 30); // staggered animation
  });

  // Wait for animation to complete before clearing
  setTimeout(() => {
    chatBox.innerHTML = "";
  }, 400); // match animation duration (0.4s)
});