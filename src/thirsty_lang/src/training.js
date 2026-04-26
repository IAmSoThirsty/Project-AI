/* eslint-env node */
/* global require, module, console, process */

/**

class TrainingProgram {
  constructor() {
    this.currentLevel = null;
    this.currentLessonIndex = 0;
    this.completedLessons = {
      base: [],
      plus: [],
      plusplus: [],
      gods: []
    };
    this.hydrationPoints = 0;
    this.badges = [];
    this.streak = 0;
    this.dynamicQuests = [
      { desc: "Use 'cascade' in any lesson today!", word: 'cascade', reward: 5 },
      { desc: "Define a function with 'gulp'!", word: 'gulp', reward: 7 },
      { desc: "Unlock the 'overflow' badge!", word: 'overflow', reward: 10 }
    ];
    this.asciiPets = [
      `  /"*._         _"\
   .-*"   "*-.._.-"/\
   <       .-"     (
    \-._.-"         )
          """""""""`,
      `  (\_/)
    ( •_•)
    / >🍶`,
      `  /\_/\
   ( o.o )
    > ^ <`
    ];
    this.leaderboardFile = 'hydration_leaderboard.json';
    let dirname = typeof __dirname !== 'undefined' ? __dirname : process.cwd();
    this.HYDRATION_HISTORY_FILE = path.join(dirname, 'hydration_history.json');
    this.loadHydrationHistory();
  }

  async handleMainMenuChoice(choice) {
    switch (choice) {
      case '1':
        await this.startLevel('base');
        break;
      case '2':
        await this.startLevel('plus');
        break;
      case '3':
        await this.startLevel('plusplus');
        break;
      case '4':
        await this.startLevel('gods');
        break;
      case '5':
        await this.showChallenges();
        break;
      case '6':
        this.showProgress();
        await this.showMainMenu();
        break;
      case '7':
        console.log('\n💧 Stay hydrated and keep learning! Goodbye!\n');
        rl.close();
        return;
      default:
        console.log('Invalid choice. Please try again.');
        await this.showMainMenu();
    }
  }

  async showHydrationMeter() {
    const points = Math.min(this.hydrationPoints, 100);
    const barLength = 20;
    const filled = Math.floor((points / 100) * barLength);
    const bar = '\x1b[36m' + '💧'.repeat(filled) + '\x1b[37m' + '░'.repeat(barLength - filled) + '\x1b[0m';
    let status = 'Thirsty';
    if(points >= 80) status = 'Overflowing!';
    else if (points >= 50) status = 'Hydrated';
    else if (points >= 20) status = 'Getting There';
    console.log(`\nHydration Meter: [${bar}] ${points}/100 (${status})`);
    if (this.badges.length > 0) {
      console.log('🏅 Badges: ' + this.badges.join(', '));
    }
    if (points >= 80) {
      console.log('( 💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧💧 )');
    }
  }

  async showMentor() {
    const tips = [
      '💡 Remember: Every mistake is a step toward mastery!',
      '🌊 Stay hydrated—your brain works best with water!',
      '🚀 Legendary coders ask for help. Don\'t be afraid to use "hint"!',
      '🦄 Try using rare Thirsty-lang words for bonus points!',
      '🏆 Check the leaderboard to see how you rank!'
    ];
    const tip = tips[Math.floor(Math.random() * tips.length)];
    console.log(`\n🤖 Mentor says: ${tip}`);
    await this.waitForEnter();
  }

  async showChallenges() {
    console.clear();
    console.log('\n🏆 Thirsty Challenges (Bonus Tasks)\n');
    console.log('Complete these for extra hydration points and badges!');
    for (const quest of this.dynamicQuests) {
      console.log(`- ${quest.desc} (Reward: +${quest.reward})`);
    }
    await this.showDynamicQuest();
    await this.showPet();
    await this.showLeaderboard();
    await this.showCertificate();
    await this.waitForEnter();
    await this.showMainMenu();
  }

  async showDynamicQuest() {
    const quest = this.dynamicQuests[Math.floor(Math.random() * this.dynamicQuests.length)];
    console.log(`\n🌟 Daily Quest: ${quest.desc} (Reward: +${quest.reward} hydration)`);
    this.currentQuest = quest;
  }

  async updateLeaderboard() {
    let board = [];
    if (fs.existsSync(this.leaderboardFile)) {
      try { board = JSON.parse(fs.readFileSync(this.leaderboardFile, 'utf8')); } catch { }
    }
    const name = process.env.USER || process.env.USERNAME || 'Anonymous';
    const entry = { name, hydration: this.hydrationPoints, date: new Date().toISOString() };
    board = board.filter(e => e.name !== name);
    board.push(entry);
    board.sort((a, b) => b.hydration - a.hydration);
    fs.writeFileSync(this.leaderboardFile, JSON.stringify(board.slice(0, 10), null, 2));
  }

  async showLeaderboard() {
    if (!fs.existsSync(this.leaderboardFile)) { console.log('No leaderboard yet!'); return; }
    const board = JSON.parse(fs.readFileSync(this.leaderboardFile, 'utf8'));
    console.log('\n🏆 Hydration Leaderboard:');
    board.forEach((e, i) => console.log(`${i + 1}. ${e.name} - ${e.hydration} hydration`));
    await this.waitForEnter();
  }

  async randomEvent() {
    if (Math.random() < 0.1) {
      console.log('\n🌧️  Aqua Storm! Double points for this lesson!');
      this.aquaStorm = true;
    } else {
      this.aquaStorm = false;
    }
  }

  async showPet() {
    const pet = this.asciiPets[Math.floor(Math.random() * this.asciiPets.length)];
    console.log(`\n🐾 Your Hydration Pet:\n${pet}`);
    await this.waitForEnter();
  }

  async showCertificate() {
    const name = process.env.USER || process.env.USERNAME || 'Hydration Hero';
    const cert = `\n╔════════════════════════════════════════════════════╗\n║        🏅 CERTIFICATE OF MASTERY 🏅              ║\n║                                                  ║\n║  This certifies that                             ║\n║                                                  ║\n║        ${name.padEnd(30)}║\n║                                                  ║\n║  has achieved Legendary Mastery in               ║\n║  Thirsty-lang Training!                          ║\n║                                                  ║\n║  Date: ${new Date().toLocaleDateString()}${' '.repeat(25)}║\n╚════════════════════════════════════════════════════╝\n`;
    console.log(cert);
    fs.writeFileSync('thirsty_lang_certificate.txt', cert);
    console.log('Certificate saved as thirsty_lang_certificate.txt! Print and display with pride!');
    await this.waitForEnter();
  }

  isStreakMaster() {
    return this.streak >= 3;
  }

  loadHydrationHistory() {
    if (fs.existsSync(this.HYDRATION_HISTORY_FILE)) {
      try {
        const data = JSON.parse(fs.readFileSync(this.HYDRATION_HISTORY_FILE, 'utf8'));
        this.hydrationPoints = data.hydrationPoints || 0;
        this.badges = data.badges || [];
        this.streak = data.streak || 0;
        this.completedLessons = data.completedLessons || this.completedLessons;
      } catch (e) {
        // Ignore errors, start fresh
      }
    }
  }

  saveHydrationHistory() {
    const data = {
      hydrationPoints: this.hydrationPoints,
      badges: this.badges,
      streak: this.streak,
      completedLessons: this.completedLessons
    };
    fs.writeFileSync(this.HYDRATION_HISTORY_FILE, JSON.stringify(data, null, 2));
  }

  async start() {
    this.showWelcome();
    await this.showMainMenu();
  }

  showWelcome() {
    console.clear();
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║        🌊 THIRSTY-LANG INTERACTIVE TRAINING 🌊            ║');
    console.log('║                                                            ║');
    console.log('║        Learn to code while staying hydrated!               ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log('\n');
  }

  async showMainMenu() {
    console.log('\n📚 Select Your Training Level:\n');
    console.log('  1. 💧 Base Thirsty-lang (Beginner)');
    console.log('  2. 💧+ Thirsty Plus (Intermediate)');
    console.log('  3. 💧++ Thirsty Plus Plus (Advanced)');
    console.log('  4. ⚡ ThirstOfGods (Master)');
    console.log('  5. 🏆 Thirsty Challenges (Bonus!)');
    console.log('  6. 📊 View Progress');
    console.log('  7. ❌ Exit\n');

    return new Promise((resolve) => {
      rl.question('Enter your choice (1-7): ', async (answer) => {
        await this.handleMainMenuChoice(answer.trim());
        resolve();
      });
    });
  }
  async randomEvent() {
    if (Math.random() < 0.1) {
      console.log('\n🌧️  Aqua Storm! Double points for this lesson!');
      this.aquaStorm = true;
    } else {
      this.aquaStorm = false;
    }
  }
  async showPet() {
    const pet = this.asciiPets[Math.floor(Math.random() * this.asciiPets.length)];
    console.log(`\n🐾 Your Hydration Pet:\n${pet}`);
    await this.waitForEnter();
  }
  async showCertificate() {
    const name = process.env.USER || process.env.USERNAME || 'Hydration Hero';
    const cert = `\n╔════════════════════════════════════════════════════╗\n║        🏅 CERTIFICATE OF MASTERY 🏅              ║\n║                                                  ║\n║  This certifies that                             ║\n║                                                  ║\n║        ${name.padEnd(30)}║\n║                                                  ║\n║  has achieved Legendary Mastery in               ║\n║  Thirsty-lang Training!                          ║\n║                                                  ║\n║  Date: ${new Date().toLocaleDateString()}${' '.repeat(25)}║\n╚════════════════════════════════════════════════════╝\n`;
    console.log(cert);
    fs.writeFileSync('thirsty_lang_certificate.txt', cert);
    console.log('Certificate saved as thirsty_lang_certificate.txt! Print and display with pride!');
    await this.waitForEnter();
  }
  constructor() {
    this.currentLevel = null;
    this.currentLessonIndex = 0;
    this.completedLessons = {
      base: [],
      plus: [],
      plusplus: [],
      gods: []
    };
    this.hydrationPoints = 0;
    this.badges = [];
    this.streak = 0;
    let dirname = typeof __dirname !== 'undefined' ? __dirname : process.cwd();
    this.HYDRATION_HISTORY_FILE = path.join(dirname, 'hydration_history.json');
    this.loadHydrationHistory();
  }

  isStreakMaster() {
    return this.streak >= 3;
  }

  loadHydrationHistory() {
    if (fs.existsSync(this.HYDRATION_HISTORY_FILE)) {
      try {
        const data = JSON.parse(fs.readFileSync(this.HYDRATION_HISTORY_FILE, 'utf8'));
        this.hydrationPoints = data.hydrationPoints || 0;
        this.badges = data.badges || [];
        this.streak = data.streak || 0;
        this.completedLessons = data.completedLessons || this.completedLessons;
      } catch (e) {
        // Ignore errors, start fresh
      }
    }
  }

  saveHydrationHistory() {
    const data = {
      hydrationPoints: this.hydrationPoints,
      badges: this.badges,
      streak: this.streak,
      completedLessons: this.completedLessons
    };
    fs.writeFileSync(this.HYDRATION_HISTORY_FILE, JSON.stringify(data, null, 2));
  }

  async start() {
    this.showWelcome();
    await this.showMainMenu();
  }

  showWelcome() {
    console.clear();
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║        🌊 THIRSTY-LANG INTERACTIVE TRAINING 🌊            ║');
    console.log('║                                                            ║');
    console.log('║        Learn to code while staying hydrated!               ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log('\n');
  }

  async showMainMenu() {
    console.log('\n📚 Select Your Training Level:\n');
    console.log('  1. 💧 Base Thirsty-lang (Beginner)');
    console.log('  2. 💧+ Thirsty Plus (Intermediate)');
    console.log('  3. 💧++ Thirsty Plus Plus (Advanced)');
    console.log('  4. ⚡ ThirstOfGods (Master)');
    console.log('  5. 🏆 Thirsty Challenges (Bonus!)');
    console.log('  6. 📊 View Progress');
    console.log('  7. ❌ Exit\n');

    return new Promise((resolve) => {
      rl.question('Enter your choice (1-7): ', async (answer) => {
        await this.handleMainMenuChoice(answer.trim());
        resolve();
      });
    });
  }

  async getLessonInput(lesson) {
    return new Promise((resolve) => {
      const startTime = Date.now();
      rl.question('\n> ', async (answer) => {
        const input = answer.trim();

        // --- Unique Language Extensions: Custom Syntax & Rare Words ---
        const customWords = ['gulp', 'stream', 'evaporate', 'hydrate', 'overflow', 'aqua', 'cascade'];
        let customBonus = false;
        for (const word of customWords) {
          if (input.includes(word)) {
            customBonus = true;
            break;
          }
        }

        // --- Secret Commands & AI Mentor ---
        if (input.toLowerCase() === 'hydrate me') {
          this.hydrationPoints += 7;
          this.badges.push('🕵️ Secret Hydrator');
          console.log('🕵️ Secret Hydrator badge unlocked! +7 hydration points!');
          this.saveHydrationHistory();
          await this.waitForEnter();
          await this.runLesson();
          resolve();
          return;
        }
        if (input.toLowerCase() === 'legendary') {
          if (!this.badges.includes('🌈 Legendary Seeker')) {
            this.badges.push('🌈 Legendary Seeker');
            this.hydrationPoints += 20;
            console.log('🌈 Legendary Seeker badge unlocked! +20 hydration points!');
            this.saveHydrationHistory();
          } else {
            console.log('🌈 You are already legendary!');
          }
          await this.waitForEnter();
          await this.runLesson();
          resolve();
          return;
        }
        if (input.toLowerCase() === 'mentor') {
          await this.showMentor();
          await this.runLesson();
          resolve();
          return;
        }

        if (input.toLowerCase() === 'menu') {
          await this.showMainMenu();
          resolve();
          return;
        }

        if (input.toLowerCase() === 'skip') {
          console.log('⏭️  Lesson skipped.');
          this.currentLessonIndex++;
          await this.runLesson();
          resolve();
          return;
        }

        if (input.toLowerCase() === 'hint') {
          console.log('💡 ' + lesson.hint);
          await this.getLessonInput(lesson);
          resolve();
          return;
        }

        // Try to execute the code
            try {
              const interpreter = new ThirstyInterpreter();
              interpreter.execute(input);

              if (lesson.validation(input) || customBonus) {
                const endTime = Date.now();
                const duration = (endTime - startTime) / 1000;
                this.completedLessons[this.currentLevel].push(this.currentLessonIndex);
                let points = 5;
                let bonusMsg = '';
                if (customBonus) {
                  points += 3;
                  bonusMsg = ' 💧 Bonus for rare word!';
                  if (!this.badges.includes('🦄 Aqua Linguist')) {
                    this.badges.push('🦄 Aqua Linguist');
                    bonusMsg += ' 🦄 Aqua Linguist badge!';
                  }
                }
                this.hydrationPoints += points;
                let speedWin = false;
                if (duration < 30) {
                  this.lastSpeedWin = true;
                  speedWin = true;
                } else {
                  this.lastSpeedWin = false;
                }
                // Track last lesson date for daily challenge
                this.lastLessonDate = new Date().toISOString().slice(0, 10);
                if (this.hydrationPoints >= 100 && !this.badges.includes('💎 Legendary Hydrator')) {
                  this.badges.push('💎 Legendary Hydrator');
                  console.log('💎 Legendary Hydrator badge unlocked!');
                }
                this.saveHydrationHistory();

                console.log(`\n✅ Excellent! Lesson completed!${speedWin ? ' ⚡ (Speed Drinker!)' : ''}${bonusMsg}`);
                await this.waitForEnter();
                this.currentLessonIndex++;
                await this.runLesson();
              } else {
                console.log('\n❌ Not quite right.');
                // Provide targeted feedback for common mistakes
                if (!input.includes('drink') && lesson.title.includes('Variable')) {
                  console.log('💡 Tip: Use "drink" to declare a variable.');
                } else if (!input.includes('pour') && lesson.title.includes('Output')) {
                  console.log('💡 Tip: Use "pour" to display a value.');
                } else if (lesson.title.includes('Conditional') && !input.includes('thirsty')) {
                  console.log('💡 Tip: Use "thirsty" for if statements.');
                } else if (lesson.title.includes('Functions') && !input.includes('glass')) {
                  console.log('💡 Tip: Use "glass" to define a function.');
                } else if (lesson.title.includes('Classes') && !input.includes('fountain')) {
                  console.log('💡 Tip: Use "fountain" to define a class.');
                } else if (customWords.some(w => input.includes(w))) {
                  console.log('💡 You used a rare Thirsty-lang word! Try using it in a valid context for bonus points.');
                } else {
                  console.log('💡 Hint: ' + lesson.hint);
                }
                await this.getLessonInput(lesson);
              }
            } catch (error) {
              console.log(`\n❌ Error: ${error.message}`);
              // Suggest possible fixes for common errors
              if (error.message.includes('Unknown statement')) {
                console.log('💡 Tip: Check your syntax. Valid statements are: drink, pour, sip, thirsty, glass, fountain, gulp, stream, evaporate, hydrate, overflow, aqua, cascade.');
              } else if (error.message.includes('Invalid drink statement')) {
                console.log('💡 Tip: Use "drink variable = value".');
              } else if (error.message.includes('Invalid thirsty statement')) {
                console.log('💡 Tip: Use "thirsty variable > value".');
              } else if (error.message.includes('Function not found')) {
                console.log('💡 Tip: Define your function first with "glass name(args)".');
              } else if (error.message.includes('Class not found')) {
                console.log('💡 Tip: Define your class first with "fountain ClassName".');
              } else if (error.message.includes('Unknown expression')) {
                console.log('💡 Tip: Make sure your variable exists or use a valid literal.');
              } else {
                console.log('Try again or type "hint" for help.');
              }
              await this.getLessonInput(lesson);
            }

            resolve();
          });
        });
      }

      showProgress() {
        console.clear();
        console.log('\n📊 Your Training Progress\n');
        console.log('═'.repeat(60));

        for (const [key, level] of Object.entries(TRAINING_LEVELS)) {
          const completed = this.completedLessons[key].length;
          const total = level.lessons.length;
          const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
          const bar = '█'.repeat(Math.floor(percentage / 5)) + '░'.repeat(20 - Math.floor(percentage / 5));

          console.log(`\n${level.name}`);
          console.log(`[${bar}] ${percentage}% (${completed}/${total} lessons)`);
        }

        // Show hydration meter and badges
        this.showHydrationMeter();
        console.log(`Hydration Points: ${this.hydrationPoints}`);
        if (this.badges.length > 0) {
          console.log('🏅 Badges: ' + this.badges.join(', '));
        }
        console.log(`Streak: ${this.streak}`);
        console.log('\n═'.repeat(60));
      }

      async waitForEnter() {
        return new Promise((resolve) => {
          rl.question('\nPress Enter to continue...', () => {
            resolve();
          });
        });
      }
    }

    async function main() {
      const program = new TrainingProgram();
      await program.start();
    }

    if (require.main === module) {
      main();
    }

    module.exports = TrainingProgram;
