# Schedule your lessons telegram bot

Link: t.me/schedule_your_lessons_bot

Tag: @schedule_your_lessons_bot

---

## Local development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker + Docker Compose
- PostgreSQL (provided via Docker Compose)

### Setup

1. Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

2. Run with Docker Compose:
```bash
docker compose up --build
```

This starts PostgreSQL and the bot. Tables are created automatically on first run.

### Running without Docker

1. Install dependencies:
```bash
uv sync
```

2. Ensure PostgreSQL is running and accessible with the credentials in `.env`.

3. Start the bot:
```bash
uv run bot.py
```

---

## Deployment

The project uses GitHub Actions to deploy to a server via SSH. Pushing to the `deployment` branch triggers an automatic deploy.

### Server setup

1. Install Docker and Docker Compose on your server.

2. Clone the repository:
```bash
git clone https://github.com/DmytroKhylko/schedule-your-lessons.git /opt/schedule-bot
cd /opt/schedule-bot
git checkout deployment
```

3. Create the `.env` file with production values:
```bash
cp .env.example .env
nano .env
```

4. Start the bot for the first time:
```bash
docker compose up --build -d
```

### GitHub Actions secrets

Add the following secrets in your GitHub repository under **Settings > Secrets and variables > Actions**:

| Secret | Description |
|--------|-------------|
| `SSH_HOST` | Server IP address or hostname |
| `SSH_USER` | SSH username on the server |
| `SSH_PRIVATE_KEY` | Private SSH key (the public key must be in the server's `~/.ssh/authorized_keys`) |
| `SSH_PORT` | SSH port on the server (e.g., `22`) |
| `DEPLOY_PATH` | Absolute path to the cloned repo on the server (e.g., `/opt/schedule-bot`) |

### Generating an SSH key pair

```bash
ssh-keygen -t ed25519 -f deploy_key -C "github-actions-deploy"
```

- Copy `deploy_key.pub` contents to your server's `~/.ssh/authorized_keys`
- Copy `deploy_key` contents to the `SSH_PRIVATE_KEY` GitHub secret

### Deploy process

1. Merge your changes into the `deployment` branch.
2. Push to GitHub.
3. GitHub Actions SSHs into the server, pulls the latest code, rebuilds and restarts containers.

To check deploy status: go to the **Actions** tab in your GitHub repository.

To view logs on the server:
```bash
cd /opt/schedule-bot
docker compose logs -f bot
```
