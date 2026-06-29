document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chatHistory');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Modal elements
    const actionModal = document.getElementById('actionModal');
    const modalCommand = document.getElementById('modalCommand');
    const modalDeny = document.getElementById('modalDeny');
    const modalApprove = document.getElementById('modalApprove');

    let currentActionCallback = null;

    function addMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        let avatarHTML = '';
        if (role === 'assistant') {
            avatarHTML = `<div class="avatar"></div>`;
        }

        // Extremely basic formatting for code blocks in mock
        const formattedText = text.replace(/`([^`]+)`/g, '<code>$1</code>');

        msgDiv.innerHTML = `
            ${avatarHTML}
            <div class="bubble">${formattedText}</div>
        `;
        
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;
        
        addMessage('user', text);
        userInput.value = '';

        // Mock delay for AI reasoning
        setTimeout(() => {
            if (text.toLowerCase().includes("update") || text.toLowerCase().includes("rebuild")) {
                showActionModal("nixos-rebuild switch --flake .#", (approved) => {
                    if (approved) {
                        addMessage('assistant', "I have initiated the system rebuild successfully.");
                    } else {
                        addMessage('assistant', "System update aborted based on your request.");
                    }
                });
            } else if (text.toLowerCase().includes("optimize") || text.toLowerCase().includes("gaming")) {
                addMessage('assistant', "Applying the gaming optimization profile. CPU governor set to `performance`.");
                document.getElementById('profileSelect').value = 'gaming';
            } else {
                addMessage('assistant', "I'm monitoring the system. Your telemetry looks solid. Health score is currently 95.");
            }
        }, 800);
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Action Modal Logic
    function showActionModal(command, callback) {
        modalCommand.textContent = command;
        currentActionCallback = callback;
        actionModal.classList.remove('hidden');
    }

    function closeModal() {
        actionModal.classList.add('hidden');
        currentActionCallback = null;
    }

    modalDeny.addEventListener('click', () => {
        if (currentActionCallback) currentActionCallback(false);
        closeModal();
    });

    modalApprove.addEventListener('click', () => {
        if (currentActionCallback) currentActionCallback(true);
        closeModal();
    });
});
