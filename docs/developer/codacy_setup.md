# 🎉 Welcome to Project-AI Codacy Integration! 🎉

Ready to add top-tier code quality checks to your Project-AI repo?  
Set the following environment variables to unlock the power of Codacy:

```bash
export CODACY_API_TOKEN=your_real_api_token_here
export CODACY_ORGANIZATION_PROVIDER=gh
export CODACY_USERNAME=IAmSoThirsty
export CODACY_PROJECT_NAME=Project-AI
```

> 🛠️ **Pro tip:**  
> Replace `your_real_api_token_here` with your actual Codacy API token (it’s a secret, don’t share!).

That’s it!  
Your Project-AI code will be under the watchful eye of Codacy—like a helpful, code-loving AI sidekick.

Happy coding! 🚀

---

## 🍃 Codacy Coverage Reporter

Enhance your code quality with coverage reporting!  
Download and run the Codacy Coverage Reporter in your CI pipeline to automatically send coverage data to Codacy:

```bash
curl -Ls https://coverage.codacy.com/get.sh | bash
```

Read more: [Codacy Coverage Reporter documentation](https://docs.codacy.com/coverage-reporter/)