# Free AI coding toolchain for Saltwater

## Current repository integration

Repository: `Joshuaogri/saltwater`  
Development branch: `main` only.

- **ChatGPT:** implementation coordinator; edits main, runs focused tests and verifies evidence.
- **Gemini:** independent engineering reviewer. The existing workflow is `.github/workflows/gemini-saltwater-project-review.yml`, using the repository Actions secret `GEMINI_API_KEY`. It is read-only and must not receive Neon credentials.
- **Gemini Code Assist:** free individual IDE assistant. Install its VS Code extension and sign in with a personal Google account: https://codeassist.google/
- **GitHub Copilot Free:** optional second-opinion assistant in VS Code/GitHub. Free usage is limited; do not enable paid usage: https://github.com/features/copilot/plans
- **OpenCode:** free, open-source coding-agent client. Install locally from https://opencode.ai/ and configure only a provider/model with a confirmed free allowance. The client itself is free; provider usage is not automatically free.
- **Cline:** optional alternative to OpenCode, not required alongside it. Its extension is free, but model/provider usage may cost money: https://cline.bot/

## Zero-cost policy

1. No paid plans, paid API models, billing activation, paid credits, paid trials or automatic overage.
2. Before using an API key, verify the exact model is on the provider's free tier and that billing is disabled or spending is otherwise technically blocked.
3. Gemini API free-tier prompts may be handled under Google's free-tier data terms. Do not send secrets, credentials, private user data or production connection details. Use the IDE assistant's applicable data controls and review provider terms before sharing proprietary source.
4. OpenCode and Cline are free clients, not free inference. Do not configure a paid model. This user's 4 GB RAM computer is not a suitable target for large local coding models.
5. Never store API keys in the repository. Use local environment variables or GitHub Actions secrets only where the relevant free allowance and data handling have been checked.
6. Do not install all assistants. Gemini Code Assist plus the existing Gemini reviewer is the primary second-opinion setup; Copilot Free and OpenCode are optional additions.

## Working method

1. State the active BP explicitly in each task.
2. ChatGPT inspects current main and identifies the smallest implementation task.
3. Gemini independently reviews the active BP and reports evidence, defects and focused fixes.
4. ChatGPT compares the review with source/tests, implements only justified changes on main and runs targeted tests.
5. GitHub Actions provides repeatable checks. Production Neon remains read-only unless the user explicitly approves a measured change.

## What still requires the account owner

The repository can contain shared agent instructions, but it cannot silently install VS Code extensions or grant third-party GitHub app access. The user must install Gemini Code Assist/Copilot/OpenCode on their computer and complete provider sign-in. Do not claim those desktop tools are connected until their installation and sign-in are confirmed.
