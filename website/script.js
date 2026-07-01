document.addEventListener('DOMContentLoaded', () => {
    const terminalBody = document.getElementById('terminal-typing');
    const originalText = terminalBody.innerHTML;
    
    // Simple typewriter effect for the terminal
    terminalBody.innerHTML = '';
    let i = 0;
    
    // Strip HTML tags for the typing effect, or handle them.
    // For simplicity, we just fade it in with a slight delay
    setTimeout(() => {
        terminalBody.innerHTML = originalText;
        terminalBody.style.opacity = 0;
        
        let opacity = 0;
        const fade = setInterval(() => {
            if (opacity >= 1) clearInterval(fade);
            terminalBody.style.opacity = opacity;
            opacity += 0.05;
        }, 50);
    }, 500);
});
