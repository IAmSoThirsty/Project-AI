/**
 * Sovereign Nexus Interactivity
 * 
 * Manages UI state and simulates real-time jurisdictional telemetry.
 */

document.addEventListener('DOMContentLoaded', () => {
    initRepl();
    simulateTelemetry();
    setupNavigation();
});

/**
 * Simulates a simple REPL typing effect and interactivity
 */
function initRepl() {
    const repl = document.getElementById('repl');
    const commands = [
        "pour 'Nexus Link Established.'",
        "shield ALPHA { detect DRILL }",
        "drink logic = EvaluateTriumvirateQuorum()",
        "return 'SOVEREIGN_STATUS: NOMINAL'"
    ];

    let i = 0;
    setInterval(() => {
        if (i < commands.length) {
            const line = document.createElement('div');
            line.className = 'line';
            line.innerHTML = `<span class="prompt">root@sovereign:~$</span> ${commands[i]}`;
            repl.appendChild(line);
            repl.scrollTop = repl.scrollHeight;
            i++;
        }
    }, 5000);
}

/**
 * Simulates fluctuating telemetry values for the dashboard
 */
function simulateTelemetry() {
    const entropyValue = document.querySelector('.card:nth-child(1) .metric-value');
    const entropyBar = document.querySelector('.card:nth-child(1) div > div');

    setInterval(() => {
        const val = (Math.random() * 0.05).toFixed(3);
        entropyValue.textContent = val;
        entropyBar.style.width = `${Math.min(100, Math.max(5, val * 1000))}%`;

        // Change color based on entropy
        if (val > 0.04) {
            entropyBar.style.backgroundColor = 'var(--accent-rose)';
        } else {
            entropyBar.style.backgroundColor = 'var(--accent-cyan)';
        }
    }, 2000);
}

/**
 * Setup navigation clicks
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Log navigation to terminal
            const repl = document.getElementById('repl');
            const line = document.createElement('div');
            line.className = 'line';
            line.innerHTML = `<span class="prompt">root@sovereign:~$</span> Navigation: Switched to ${item.textContent.trim()}`;
            repl.appendChild(line);
            repl.scrollTop = repl.scrollHeight;
        });
    });
}
