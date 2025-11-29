"""
Learning path generator and manager.
"""
import openai
import json
import os
from app.core.network_utils import is_online


# Offline template-based learning paths for common topics
OFFLINE_TEMPLATES = {
    "programming": {
        "beginner": """# Learning Path: Programming (Beginner)

## Core Concepts to Master
1. Basic syntax and data types
2. Variables and operators
3. Control structures (if/else, loops)
4. Functions and basic modularity
5. Introduction to debugging

## Recommended Resources
- **Online**: Codecademy, freeCodeCamp, Khan Academy
- **Books**: "Automate the Boring Stuff" (Python), "Eloquent JavaScript"
- **Practice**: HackerRank, LeetCode (easy problems)

## Practice Projects
1. Calculator application
2. Number guessing game
3. To-do list (console-based)
4. Simple text-based adventure

## Timeline Estimate
- 4-8 weeks of consistent practice (1-2 hours daily)

## Milestones
- [ ] Write first "Hello World" program
- [ ] Complete 10 basic coding exercises
- [ ] Build first small project
- [ ] Understand basic debugging techniques

*Generated offline - connect to internet for AI-personalized paths*""",
        "intermediate": """# Learning Path: Programming (Intermediate)

## Core Concepts to Master
1. Object-oriented programming
2. Data structures (arrays, lists, dictionaries, trees)
3. Algorithms and complexity analysis
4. File handling and I/O
5. Error handling and exceptions
6. Version control (Git)

## Recommended Resources
- **Books**: "Clean Code", "Design Patterns"
- **Online**: Coursera, edX programming courses
- **Practice**: LeetCode (medium), Codewars

## Practice Projects
1. REST API client application
2. Database-backed CRUD app
3. Command-line tools
4. Web scraper

## Timeline Estimate
- 8-16 weeks of practice

## Milestones
- [ ] Implement common data structures
- [ ] Complete 25 medium-difficulty problems
- [ ] Build a full-stack application
- [ ] Contribute to open source

*Generated offline - connect to internet for AI-personalized paths*""",
        "advanced": """# Learning Path: Programming (Advanced)

## Core Concepts to Master
1. System design and architecture
2. Advanced algorithms (graph, dynamic programming)
3. Concurrency and parallelism
4. Performance optimization
5. Security best practices
6. Testing methodologies

## Recommended Resources
- **Books**: "Designing Data-Intensive Applications", "SICP"
- **Online**: MIT OpenCourseWare, Stanford CS courses
- **Practice**: LeetCode (hard), system design interviews

## Practice Projects
1. Distributed system component
2. Compiler or interpreter
3. Real-time application
4. Performance-critical application

## Timeline Estimate
- Ongoing (6+ months)

## Milestones
- [ ] Design and implement a scalable system
- [ ] Master advanced algorithm patterns
- [ ] Lead a significant project
- [ ] Mentor junior developers

*Generated offline - connect to internet for AI-personalized paths*"""
    },
    "python": {
        "beginner": """# Learning Path: Python (Beginner)

## Core Concepts to Master
1. Python syntax and indentation
2. Data types (strings, lists, dicts, tuples)
3. Control flow (if/elif/else, for, while)
4. Functions and scope
5. Modules and packages
6. File I/O basics

## Recommended Resources
- **Official**: Python.org tutorial
- **Books**: "Automate the Boring Stuff with Python"
- **Interactive**: Python Tutor, Codecademy Python
- **Practice**: Exercism Python track

## Practice Projects
1. Password generator
2. Simple calculator
3. File organizer script
4. Basic web scraper (requests + BeautifulSoup)

## Timeline Estimate
- 4-6 weeks (1-2 hours daily)

## Milestones
- [ ] Complete Python basics
- [ ] Write 5 useful scripts
- [ ] Understand pip and virtual environments
- [ ] Build first automation project

*Generated offline - connect to internet for AI-personalized paths*""",
    },
    "data science": {
        "beginner": """# Learning Path: Data Science (Beginner)

## Core Concepts to Master
1. Statistics fundamentals
2. Python for data analysis (NumPy, Pandas)
3. Data visualization (Matplotlib, Seaborn)
4. Basic SQL queries
5. Data cleaning techniques

## Recommended Resources
- **Online**: Kaggle Learn, DataCamp
- **Books**: "Python for Data Analysis" by Wes McKinney
- **Practice**: Kaggle competitions (Getting Started)

## Practice Projects
1. Exploratory data analysis on public datasets
2. Data cleaning pipeline
3. Visualization dashboard
4. Basic predictive model

## Timeline Estimate
- 8-12 weeks

## Milestones
- [ ] Complete basic statistics review
- [ ] Analyze 3 different datasets
- [ ] Create compelling visualizations
- [ ] Build first ML model

*Generated offline - connect to internet for AI-personalized paths*"""
    },
    "web development": {
        "beginner": """# Learning Path: Web Development (Beginner)

## Core Concepts to Master
1. HTML structure and semantics
2. CSS styling and layouts (Flexbox, Grid)
3. JavaScript basics
4. DOM manipulation
5. Responsive design principles
6. Basic accessibility

## Recommended Resources
- **Online**: MDN Web Docs, freeCodeCamp
- **Practice**: Frontend Mentor challenges
- **Tools**: VS Code, browser DevTools

## Practice Projects
1. Personal portfolio page
2. Landing page clone
3. Interactive form
4. Simple JavaScript game

## Timeline Estimate
- 6-10 weeks

## Milestones
- [ ] Build semantic HTML pages
- [ ] Style with modern CSS
- [ ] Add JavaScript interactivity
- [ ] Deploy first website

*Generated offline - connect to internet for AI-personalized paths*"""
    },
    "machine learning": {
        "beginner": """# Learning Path: Machine Learning (Beginner)

## Core Concepts to Master
1. Linear algebra basics
2. Statistics and probability
3. Supervised learning (regression, classification)
4. Model evaluation metrics
5. Feature engineering basics

## Recommended Resources
- **Courses**: Andrew Ng's ML course (Coursera)
- **Books**: "Hands-On ML with Scikit-Learn"
- **Libraries**: scikit-learn, pandas, numpy

## Practice Projects
1. Linear regression on housing data
2. Classification on Iris/Titanic dataset
3. Model comparison study
4. Feature engineering exercise

## Timeline Estimate
- 12-16 weeks

## Milestones
- [ ] Understand math foundations
- [ ] Implement basic algorithms
- [ ] Complete 3 Kaggle competitions
- [ ] Build end-to-end ML pipeline

*Generated offline - connect to internet for AI-personalized paths*"""
    },
    "cybersecurity": {
        "beginner": """# Learning Path: Cybersecurity (Beginner)

## Core Concepts to Master
1. Networking fundamentals (TCP/IP, DNS, HTTP)
2. Operating system security basics
3. Cryptography fundamentals
4. Common vulnerabilities (OWASP Top 10)
5. Security tools introduction

## Recommended Resources
- **Online**: TryHackMe, HackTheBox
- **Certifications**: CompTIA Security+
- **Books**: "The Web Application Hacker's Handbook"

## Practice Projects
1. Set up a home lab
2. CTF challenges
3. Vulnerability assessment
4. Security audit checklist

## Timeline Estimate
- 12-20 weeks

## Milestones
- [ ] Understand network protocols
- [ ] Complete beginner CTF rooms
- [ ] Set up security tools
- [ ] Earn first certification

*Generated offline - connect to internet for AI-personalized paths*"""
    }
}


class LearningPathManager:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key

    def _get_offline_template(self, interest: str, skill_level: str) -> str:
        """Get an offline template for the given interest and skill level."""
        interest_lower = interest.lower().strip()
        skill_lower = skill_level.lower().strip()

        # Try exact match first
        if interest_lower in OFFLINE_TEMPLATES:
            templates = OFFLINE_TEMPLATES[interest_lower]
            if skill_lower in templates:
                return templates[skill_lower]
            # Return first available level if exact level not found
            return next(iter(templates.values()))

        # Try partial match
        for topic, templates in OFFLINE_TEMPLATES.items():
            if topic in interest_lower or interest_lower in topic:
                if skill_lower in templates:
                    return templates[skill_lower]
                return next(iter(templates.values()))

        # Return generic programming template as fallback
        return self._generate_generic_offline_path(interest, skill_level)

    def _generate_generic_offline_path(self, interest: str, skill_level: str) -> str:
        """Generate a generic offline learning path template."""
        return f"""# Learning Path: {interest.title()} ({skill_level.title()})

## Core Concepts to Master
1. Fundamentals and terminology
2. Basic principles and theory
3. Practical applications
4. Tools and technologies
5. Best practices

## Recommended Resources
- Search for "{interest}" tutorials online
- Look for books on "{interest}" at your local library
- Find online courses on platforms like Coursera, Udemy, or edX
- Join communities and forums related to "{interest}"

## Practice Projects
1. Start with a small introductory project
2. Build something practical you can use
3. Contribute to open-source projects
4. Create a portfolio piece

## Timeline Estimate
- {skill_level.title()} level: 4-12 weeks depending on complexity

## Milestones
- [ ] Complete foundational learning
- [ ] Build first project
- [ ] Get feedback from community
- [ ] Apply skills to real-world problem

## Note
*This is a generic offline template. Connect to the internet to generate*
*an AI-personalized learning path tailored to your specific interests.*

## Tips for Offline Learning
- Download documentation for offline access
- Save useful articles and tutorials
- Use offline-capable learning apps
- Practice with local tools and environments"""

    def generate_path(self, interest, skill_level="beginner"):
        """Generate a personalized learning path.

        Uses OpenAI when online, falls back to templates when offline.
        """
        # Check if we're online and have an API key
        if self.api_key and is_online(timeout=2.0):
            try:
                # Build a prompt
                prompt = (
                    f"Create a structured learning path for {interest} "
                    f"at {skill_level} level.\n"
                    "Include:\n"
                    "1. Core concepts to master\n"
                    "2. Recommended resources (tutorials, books, courses)\n"
                    "3. Practice projects\n"
                    "4. Timeline estimates\n"
                    "5. Milestones and checkpoints"
                )

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an educational expert creating learning paths."
                        },
                        {"role": "user", "content": prompt},
                    ],
                )

                return response.choices[0].message.content
            except Exception as api_error:
                # If API fails, fall back to offline template
                offline_note = f"\n\n---\n*Online generation failed: {str(api_error)}*"
                return self._get_offline_template(interest, skill_level) + offline_note

        # Offline mode: use template
        return self._get_offline_template(interest, skill_level)

    def save_path(self, username, interest, path_content):
        """Save a generated learning path"""
        filename = f"learning_paths_{username}.json"
        paths = {}
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                paths = json.load(f)

        paths[interest] = {
            'content': path_content,
            'progress': 0,
            'completed_milestones': []
        }

        with open(filename, 'w') as f:
            json.dump(paths, f)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user"""
        filename = f"learning_paths_{username}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
