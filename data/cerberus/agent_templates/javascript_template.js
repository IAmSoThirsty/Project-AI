// Cerberus Hydra Guard Agent - JavaScript Template
// Language: {human_lang} ({human_lang_name})
// Agent ID: {agent_id}
// Spawn Generation: {generation}
// Locked Section: {locked_section}

class CerberusGuardAgent {
    constructor(agentId, humanLang, lockedSection, generation) {
        this.agentId = agentId;
        this.humanLang = humanLang;
        this.lockedSection = lockedSection;
        this.generation = generation;
        this.startTime = new Date();
        this.status = "active";
    }
    
    log(messageKey) {{
        const messages = {{
            "en": {{
                "started": `Agent ${{this.agentId}} started - Protecting ${{this.lockedSection}}`,
                "monitoring": `Monitoring section: ${{this.lockedSection}}`,
                "breach_detected": `BREACH DETECTED in ${{this.lockedSection}}!`,
                "spawning_reinforcements": `Spawning 3 reinforcement agents...`,
            }}
        }};
        const msg = messages[this.humanLang]?.[messageKey] || messageKey;
        console.log(`[${{new Date().toISOString()}}] [${{this.agentId}}] ${{msg}}`);
    }}
    
    monitor() {
        this.log("started");
        setInterval(() => {
            this.log("monitoring");
        }, 5000);
    }
    
    respondToBreach() {
        this.log("breach_detected");
        this.log("spawning_reinforcements");
    }
}

const agent = new CerberusGuardAgent(
    "{agent_id}",
    "{human_lang}",
    "{locked_section}",
    {generation}
);
agent.monitor();
