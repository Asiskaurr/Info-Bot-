const chatLauncher = document.querySelector("#chat-launcher");
const chatPanel = document.querySelector("#chat-panel");
const chatGreeting = document.querySelector("#chat-greeting");

chatLauncher.addEventListener("click", () => {
  const isOpen = chatLauncher.getAttribute("aria-expanded") === "true";
  const open = !isOpen;

  chatPanel.hidden = !open;
  chatGreeting.hidden = open;
  chatLauncher.setAttribute("aria-expanded", String(open));
  chatLauncher.setAttribute("aria-label", open ? "Close InfoBot chat" : "Open InfoBot chat");
  chatLauncher.title = open ? "Close InfoBot chat" : "Open InfoBot chat";
});
