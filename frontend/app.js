const form = document.querySelector("#chat-form");
const input = document.querySelector("#question-input");
const sendButton = form.querySelector('button[type="submit"]');
const conversation = document.querySelector("#conversation");

// Keep true while the backend is still being built. Set false to use the API.
const USE_MOCK_API = true;
// Update this if the backend runs on a different host or port.
const API_URL = "http://127.0.0.1:5000/api/chat";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (sendButton.disabled) return;

  const question = input.value.trim();
  if (!question) return;

  addMessage("You", question, "user-message");
  input.value = "";
  input.disabled = true;
  sendButton.disabled = true;
  const thinkingMessage = addMessage("InfoBot", "InfoBot is thinking…", "assistant-message loading-message");

  try {
    const result = await getReply(question);
    thinkingMessage.remove();
    addMessage("InfoBot", result, "assistant-message");
  } catch (error) {
    thinkingMessage.remove();
    console.error("InfoBot request failed:", error);
    addMessage(
      "InfoBot",
      error.name === "TypeError"
        ? "I couldn’t connect to the InfoBot service. Please check that the backend is running and try again."
        : error.message,
      "assistant-message",
    );
  } finally {
    input.disabled = false;
    sendButton.disabled = false;
    input.focus();
  }
});

// Uses the agreed contract: { question } -> { answer, sources }.
async function getReply(question) {
  if (USE_MOCK_API) return getMockReply(question);

  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("InfoBot returned an unreadable response. Please try again.");
  }

  if (!data || typeof data !== "object") {
    throw new Error("InfoBot returned an invalid response. Please try again.");
  }

  if (!response.ok) {
    throw new Error(
      data.error?.message || `InfoBot request failed (HTTP ${response.status}).`,
    );
  }

  if (typeof data.answer !== "string") {
    throw new Error("Chat API response is missing a string answer");
  }

  return {
    answer: data.answer,
    sources: Array.isArray(data.sources) ? data.sources : [],
  };
}

async function getMockReply(question) {
  return {
    answer: `This is a sample response to: “${question}”. The connected InfoBot service will provide an answer from GTBIT sources.`,
    sources: [
      {
        title: "Example source — GTBIT website",
        url: "https://www.gtbit.ac.in/",
        snippet: "Demo citation only; this page was not retrieved for your question.",
      },
    ],
  };
}

function addMessage(label, content, className) {
  const article = document.createElement("article");
  article.className = `message ${className}`;

  const heading = document.createElement("span");
  heading.className = "message-label";
  heading.textContent = label;

  const paragraph = document.createElement("p");
  paragraph.textContent = typeof content === "string" ? content : content.answer;

  article.append(heading, paragraph);

  if (typeof content !== "string" && Array.isArray(content.sources) && content.sources.length) {
    const sourceSection = document.createElement("div");
    sourceSection.className = "message-sources";

    const sourceHeading = document.createElement("span");
    sourceHeading.className = "sources-heading";
    sourceHeading.textContent = "Sources";
    sourceSection.append(sourceHeading);

    const sourceList = document.createElement("ul");
    for (const source of content.sources) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = getSafeSourceUrl(source.url);
      link.textContent = source.source_number
        ? `Source ${source.source_number}: ${source.title || source.url}`
        : source.title || source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      item.append(link);

      if (source.snippet || source.page_number) {
        const snippet = document.createElement("p");
        snippet.className = "source-snippet";
        const page = source.page_number ? `Page ${source.page_number}. ` : "";
        snippet.textContent = `${page}${source.snippet || ""}`;
        item.append(snippet);
      }
      sourceList.append(item);
    }
    sourceSection.append(sourceList);
    article.append(sourceSection);
  }

  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
  return article;
}

function getSafeSourceUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
  } catch {
    return "#";
  }
}
