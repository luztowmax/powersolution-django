document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("whatsapp-toggle");
    const chatBox = document.getElementById("whatsapp-chat");
    const closeButton = document.getElementById("close-whatsapp");

    if (!toggle || !chatBox || !closeButton) {
        return;
    }

    function setChatOpen(open) {
        chatBox.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
    }

    toggle.addEventListener("click", function () {
        setChatOpen(chatBox.hidden);
    });

    closeButton.addEventListener("click", function () {
        setChatOpen(false);
    });
});
