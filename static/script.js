// Get DOM elements
const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Event listener for the send button
sendButton.addEventListener("click", sendMessage);

// Event listener for the Enter key
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});





// Function to handle user message
async function sendMessage() {
  const message = userInput.value.trim();

  if (message) {
    displayMessage(message, "user");
    userInput.value = "";

    displayMessage("typing", "bot");
    try {
      const response = await sendPostRequest(message);
      console.log(response.data);
      const botResponse = response.data.message;
      const sources = response.data.sources;
      const citations = response.data.citations;
      displayMessage(botResponse, "bot");
      // displaySources(sources, citations);
    } catch (error) {
      console.error(error);
      displayMessage(error.message, "bot");
    }
  }
}

// Function to send POST request
function sendPostRequest(message) {
  return axios.post("http://127.0.0.1:5001/chat", { message });
}

// Function to display chat messages
function displayMessage(message, sender) {
  if (message === "typing" && sender === "bot") {
    const messageElement = document.createElement("div");
    messageElement.setAttribute("id", "typing");
    messageElement.classList.add("message", "bot");
    const messageBubble = document.createElement("div");
    messageBubble.classList.add("message-bubble");
    messageBubble.innerHTML = `
      <div class="typing-indicator">
        <div></div>
        <div></div>
        <div></div>
      </div>
    `;
    messageElement.appendChild(messageBubble);

    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } else {
    if (document.getElementById("typing") != null) {
      document.getElementById("typing").remove();
    }
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender === "user" ? "user" : "bot");
    const messageBubble = document.createElement("div");
    messageBubble.classList.add("message-bubble");
    messageBubble.innerHTML = message;

    messageElement.appendChild(messageBubble);

    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

// Function to display log message
// function displaySources(sources, citations) {
//   const table = document.getElementById("table-list");
//   table.innerHTML = "";
//   sources.forEach((source, idx) => {
//     const newRow = document.createElement("tr");
//     newRow.innerHTML = `<tr>
//                             <th scope="row">${citations[idx]}</th>
//                             <td>${source}</tr>`;
//     table.appendChild(newRow);
//   });
// }

// Initial bot message
setTimeout(() => {
  displayMessage(
    "Hello, I am an assistant trained on US Professional Services documentation. I will do my best to answer any questions you may have. How can I help you today?",
    "bot"
  );
}, 500);
