//                                           [2026-03-03 13:45]
//                                          Productivity: Active
/* eslint-env node */
/* global require, module, console, process */

/**
 * Thirsty-lang Interactive Training
 * Learn to code while staying hydrated!
 * 
 * Date: 2026-03-03 15:15 UTC | Status: Active
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const ThirstyInterpreter = require('./index');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const TRAINING_LEVELS = {
  base: {
    name: 'Base Thirsty-lang (Beginner)',
    lessons: [
      {
        title: 'Variable Declaration',
        task: 'Declare a variable named "water" with the value "H2O"',
        hint: 'Use "drink water = \"H2O\""',
        validation: (input) => input.includes('drink water') && input.includes('"H2O"')
      },
      {
        title: 'Output Statement',
        task: 'Output the value of the variable "water"',
        hint: 'Use "pour water"',
        validation: (input) => input.includes('pour water')
      }
    ]
  },
  plus: {
    name: 'Thirsty Plus (Intermediate)',
    lessons: [
      {
        title: 'Numbers and Math',
        task: 'Declare a variable "temp" with value 25',
        hint: 'drink temp = 25',
        validation: (input) => input.includes('drink temp') && input.includes('25')
      }
    ]
  },
  plusplus: {
    name: 'Thirsty Plus Plus (Advanced)',
    lessons: []
  },
  gods: {
    name: 'ThirstOfGods (Master)',
    lessons: []
  }
};

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
      `  /"*._         _"\n   .-*"   "*-.._.-"/\n   <       .-"     (\n    \-._.-"         )\n          """""""""`,
      `  (\_/)\n    ( •_•)\n    / >🍶`,
      `  /\_/\n   ( o.o )\n    > ^ <`
    ];
    this.leaderboardFile = 'hydration_leaderboard.json';
    const dirname = typeof __dirname !== 'undefined' ? __dirname : process.cwd();
    this.HYDRATION_HISTORY_FILE = path.join(dirname, 'hydration_history.json');
    this.loadHydrationHistory();
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
        // Ignore errors
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

  async handleMainMenuChoice(choice) {
    switch (choice) {
      case '1': await this.startLevel('base'); break;
      case '2': await this.startLevel('plus'); break;
      case '3': await this.startLevel('plusplus'); break;
      case '4': await this.startLevel('gods'); break;
      case '5': await this.showChallenges(); break;
      case '6': this.showProgress(); await this.showMainMenu(); break;
      case '7':
        console.log('\n💧 Stay hydrated and keep learning! Goodbye!\n');
        process.exit(0);
      default:
        console.log('Invalid choice. Please try again.');
        await this.showMainMenu();
    }
  }

  async startLevel(levelKey) {
    this.currentLevel = levelKey;
    this.currentLessonIndex = 0;
    console.clear();
    console.log(`\n🌊 Starting Level: ${TRAINING_LEVELS[levelKey].name}\n`);
    await this.runLesson();
  }

  async runLesson() {
    const level = TRAINING_LEVELS[this.currentLevel];
    if (this.currentLessonIndex >= level.lessons.length) {
      console.log('\n🎉 Congratulations! You have completed all lessons in this level!');
      this.streak++;
      this.saveHydrationHistory();
      await this.waitForEnter();
      await this.showMainMenu();
      return;
    }

    const lesson = level.lessons[this.currentLessonIndex];
    console.clear();
    console.log(`\n📖 Lesson ${this.currentLessonIndex + 1}: ${lesson.title}`);
    console.log('═'.repeat(40));
    console.log(`Task: ${lesson.task}`);
    console.log('\n(Type "hint" for help, "menu" to return, or "skip" to skip)');

    await this.getLessonInput(lesson);
  }

  async getLessonInput(lesson) {
    return new Promise((resolve) => {
      rl.question('\n💧> ', async (input) => {
        const trimmed = input.trim();

        if (trimmed.toLowerCase() === 'hint') {
          console.log(`💡 Hint: ${lesson.hint}`);
          await this.getLessonInput(lesson);
          resolve();
          return;
        }

        if (trimmed.toLowerCase() === 'menu') {
          await this.showMainMenu();
          resolve();
          return;
        }

        if (trimmed.toLowerCase() === 'skip') {
          this.currentLessonIndex++;
          await this.runLesson();
          resolve();
          return;
        }

        try {
          const interpreter = new ThirstyInterpreter();
          interpreter.execute(trimmed);

          if (lesson.validation(trimmed)) {
            console.log('\n✅ Excellent! Lesson completed!');
            this.hydrationPoints += 10;
            this.completedLessons[this.currentLevel].push(this.currentLessonIndex);
            this.saveHydrationHistory();
            await this.waitForEnter();
            this.currentLessonIndex++;
            await this.runLesson();
          } else {
            console.log('\n❌ Not quite right. Try again!');
            await this.getLessonInput(lesson);
          }
        } catch (error) {
          console.log(`\n❌ Error: ${error.message}`);
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
      console.log(`${level.name}: ${percentage}% (${completed}/${total})`);
    }
    console.log(`\nHydration Points: ${this.hydrationPoints}`);
    console.log(`Streak: ${this.streak}`);
    if (this.badges.length > 0) {
      console.log('🏅 Badges: ' + this.badges.join(', '));
    }
  }

  async showChallenges() {
    console.log('\n🏆 Daily Challenges:\n');
    for (const quest of this.dynamicQuests) {
      console.log(`  - ${quest.desc} (+${quest.reward} points)`);
    }
    await this.waitForEnter();
    await this.showMainMenu();
  }

  async waitForEnter() {
    return new Promise((resolve) => {
      rl.question('\nPress Enter to continue...', () => resolve());
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
