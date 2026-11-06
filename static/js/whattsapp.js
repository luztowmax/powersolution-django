
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("whatsapp-toggle");
    const chatBox = document.getElementById("whatsapp-chat");
    const close = document.getElementById("close-whatsapp");

    if (!toggle || !chatBox || !close) return;

    function setChatOpen(isOpen) {
        chatBox.hidden = !isOpen;
        toggle.setAttribute("aria-expanded", String(isOpen));
    }

    toggle.addEventListener("click", function () {
        setChatOpen(chatBox.hidden);
    });

    close.addEventListener("click", function () {
        setChatOpen(false);
    });

    // Show the chat invitation after five seconds.
    // Do not automatically open the user's WhatsApp application.
    setTimeout(function () {
        if (chatBox.hidden) {
            setChatOpen(true);
        }
    }, 5000);
});
