/**
 * Meta Tags Generator Helper
 * Use this to generate page-specific meta tags for each HTML page
 */

const metaTagsConfig = {
  // Home Page
  home: {
    title: 'The Triumvirate - AI × Humanity × Technology',
    description: 'Exploring the Trinity of AI, Humanity & Technology through ethical AI development, robust security, and transparent knowledge systems. The Triumvirate framework for shaping the future of AGI-Human relations.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'AI ethics, artificial intelligence, AGI, cognitive architecture, security framework, knowledge repository'
  },
  
  // Manifesto Gateway
  manifesto: {
    title: 'The Manifesto Gateway | The Triumvirate',
    description: 'Explore the comprehensive manifesto outlining the vision, principles, and ethical framework for The Triumvirate: AI, Humanity, and Technology in harmony.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/manifesto_gateway.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'AI manifesto, ethical AI principles, technology ethics, AGI guidelines'
  },
  
  // Trinity Deep Dive
  trinity: {
    title: 'Trinity Deep Dive | The Triumvirate',
    description: 'Deep dive into the three pillars of The Triumvirate: Project AI (Cognitive Engine), Cerberus (Security Fortress), and Codex Deus Maximus (Knowledge Repository).',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/trinity_deep_dive.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'trinity framework, AI architecture, security systems, knowledge management'
  },
  
  // Project AI
  projectAI: {
    title: 'Project AI - Cognitive Engine | The Triumvirate',
    description: 'Explore Project AI: An adaptive cognitive architecture with ethical frameworks, context-aware memory systems, and real-time decision-making with moral reasoning.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/project_ai_cognitive_engine.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'cognitive AI, AI architecture, ethical AI, adaptive intelligence, moral reasoning'
  },
  
  // Cerberus
  cerberus: {
    title: 'Cerberus - Security Fortress | The Triumvirate',
    description: 'Cerberus: Multi-layered security architecture with threat detection, response systems, privacy-first design, and quantum-resistant encryption.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/cerberus_security_fortress.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'AI security, cyber security, threat detection, quantum encryption, privacy protection'
  },
  
  // Codex Deus Maximus
  codex: {
    title: 'Codex Deus Maximus - Knowledge Repository | The Triumvirate',
    description: 'Codex Deus Maximus: Distributed knowledge architecture with version-controlled ethical guidelines and transparent decision-making processes.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/codex_deus_maximus_repository.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'knowledge management, AI knowledge base, ethical guidelines, transparent AI'
  },
  
  // Research Center
  research: {
    title: 'Research Center | The Triumvirate',
    description: 'Explore cutting-edge research, white papers, and technical documentation on ethical AI development, security, and knowledge systems.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/research_center.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'AI research, white papers, technical documentation, AI studies'
  },
  
  // Founder Profile
  founder: {
    title: 'Jeremy Karrick - Founder Profile | The Triumvirate',
    description: 'Meet Jeremy Karrick (Thirsty), the visionary behind The Triumvirate framework and founder of ThirstysProjects.com.',
    url: 'https://iamsothirsty.github.io/the_triumvirate/pages/jeremy_karrick_founder_profile.html',
    image: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/og-image.png',
    twitterImage: 'https://iamsothirsty.github.io/the_triumvirate/assets/images/twitter-card.png',
    keywords: 'Jeremy Karrick, Thirsty, AI founder, technology visionary'
  }
};

/**
 * Generate meta tags HTML for a specific page
 * @param {string} pageKey - The key from metaTagsConfig
 * @returns {string} HTML string of meta tags
 */
function generateMetaTags(pageKey) {
  const config = metaTagsConfig[pageKey];
  if (!config) {
    console.error(`No configuration found for page: ${pageKey}`);
    return '';
  }

  const title = escapeAttribute(config.title);
  const description = escapeAttribute(config.description);
  const url = escapeAttribute(config.url);
  const image = escapeAttribute(config.image);
  const twitterImage = escapeAttribute(config.twitterImage || config.image);
  const keywords = escapeAttribute(config.keywords);
  
  return `
    <!-- Primary Meta Tags -->
    <title>${title}</title>
    <meta name="description" content="${description}">
    <meta name="keywords" content="${keywords}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:url" content="${url}">
    <meta property="og:title" content="${title}">
    <meta property="og:description" content="${description}">
    <meta property="og:image" content="${image}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="${url}">
    <meta name="twitter:title" content="${title}">
    <meta name="twitter:description" content="${description}">
    <meta name="twitter:image" content="${twitterImage}">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="${url}">
  `;
}

/**
 * List all available page keys.
 * @returns {string[]}
 */
function listPageKeys() {
  return Object.keys(metaTagsConfig);
}

/**
 * Parse command-line options for CLI usage.
 * @param {string[]} argv
 * @returns {{list:boolean,page:string|null}}
 */
function parseCliArgs(argv) {
  let list = false;
  let page = null;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--list' || arg === '-l') {
      list = true;
    } else if ((arg === '--page' || arg === '-p') && argv[index + 1]) {
      page = argv[index + 1];
      index += 1;
    }
  }

  return { list, page };
}

/**
 * Run as a CLI utility.
 * @param {string[]} argv
 * @returns {number} process exit code
 */
function runCli(argv = process.argv.slice(2)) {
  const args = parseCliArgs(argv);

  if (args.list) {
    console.log('Available page keys:');
    listPageKeys().forEach((key) => console.log(`- ${key}`));
    return 0;
  }

  if (!args.page) {
    console.error('Usage: node js/meta-generator.js --page <key>');
    console.error('       node js/meta-generator.js --list');
    return 1;
  }

  const tags = generateMetaTags(args.page);
  if (!tags) {
    console.error(`Unknown page key: ${args.page}`);
    return 1;
  }

  console.log(tags.trim());
  return 0;
}

/**
 * Basic HTML attribute escaping for generated tags.
 * @param {string} value
 * @returns {string}
 */
function escapeAttribute(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Export for use in build scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { metaTagsConfig, generateMetaTags, listPageKeys, runCli };
}

if (require.main === module) {
  process.exitCode = runCli();
}
