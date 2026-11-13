const form = document.querySelector("#chat-form");
const input = document.querySelector("#question-input");
const sendButton = form.querySelector('button[type="submit"]');
const conversation = document.querySelector("#conversation");

// The backend runs locally on this address by default (see app.py).
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

function addMessage(label, content, className) {
  const article = document.createElement("article");
  article.className = `message ${className}`;

  const heading = document.createElement("span");
  heading.className = "message-label";
  heading.textContent = label;

  const body = document.createElement(typeof content === "string" ? "p" : "div");
  if (typeof content === "string") {
    body.textContent = content;
  } else {
    body.className = "answer-content";
    renderMarkdown(content.answer, body);
  }

  article.append(heading, body);

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
        const fullDescription = `${page}${source.snippet || ""}`.replace(/\s+/g, " ").trim();
        snippet.textContent = fullDescription;
        snippet.title = fullDescription;
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

function renderMarkdown(markdown, container) {
  const lines = String(markdown || "").replace(/\r\n?/g, "\n").split("\n");
  let paragraphLines = [];
  let listElement = null;

  const flushParagraph = () => {
    if (!paragraphLines.length) return;
    const paragraph = document.createElement("p");
    appendInlineMarkdown(paragraphLines.join(" ").trim(), paragraph);
    container.append(paragraph);
    paragraphLines = [];
  };

  const flushList = () => {
    listElement = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      const heading = document.createElement(headingMatch[1].length <= 2 ? "h3" : "h4");
      appendInlineMarkdown(headingMatch[2], heading);
      container.append(heading);
      continue;
    }

    const bulletMatch = line.match(/^[-*+]\s+(.+)$/);
    const numberMatch = line.match(/^\d+[.)]\s+(.+)$/);
    if (bulletMatch || numberMatch) {
      flushParagraph();
      const tagName = bulletMatch ? "ul" : "ol";
      if (!listElement || listElement.tagName.toLowerCase() !== tagName) {
        flushList();
        listElement = document.createElement(tagName);
        container.append(listElement);
      }
      const item = document.createElement("li");
      appendInlineMarkdown((bulletMatch || numberMatch)[1], item);
      listElement.append(item);
      continue;
    }

    flushList();
    paragraphLines.push(line);
  }

  flushParagraph();
}

function appendInlineMarkdown(text, parent) {
  const tokenPattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let lastIndex = 0;

  for (const match of text.matchAll(tokenPattern)) {
    parent.append(document.createTextNode(text.slice(lastIndex, match.index)));
    const token = match[0];
    const isBold = token.startsWith("**");
    const isCode = token.startsWith("`");
    const element = document.createElement(isBold ? "strong" : isCode ? "code" : "em");
    element.textContent = token.slice(isBold || isCode ? (isBold ? 2 : 1) : 1, isBold ? -2 : -1);
    parent.append(element);
    lastIndex = match.index + token.length;
  }

  parent.append(document.createTextNode(text.slice(lastIndex)));
}

function getSafeSourceUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
  } catch {
    return "#";
  }
}
