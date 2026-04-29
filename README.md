<div align="center">
  <h1>🛡️ PGWarden</h1>
  <p><strong>Advanced, centralized PostgreSQL monitoring and schema tracking for zero-downtime operations.</strong></p>
</div>

<br />

PGWarden is an open-source, robust solution designed to monitor multiple PostgreSQL databases simultaneously from a single pane of glass. It not only tracks performance metrics, locks, and active sessions in real-time, but also keeps a complete and versioned history of your schema (tables, columns, and indexes) changes over time.

---

## ✨ Features

- **Multi-Server Monitoring:** Connect and monitor several PostgreSQL servers and their databases dynamically.
- **Metric Collection:** Continuous polling of deep metrics like index usage, sequential scans, live/dead tuples, and vacuum stats.
- **Schema Versioning:** Keeps a historical audit trail of changes applied to your tables, columns, and indexes. 
- **Session & Lock Tracking:** See exactly what is hanging or taking too long with real-time session and lock capture.
- **FastAPI Backend:** A sleek, fully typed, asynchronous API to query metrics and register new targets.
- **Modern Web UI:** A beautiful frontend visualizing the raw time-series data and mapping out your database schema evolution.
- **Built on TimescaleDB:** Leverages TimescaleDB hypertables for highly efficient time-series metric storage and fast analytics queries.

## 🚀 Getting Started

PGWarden uses Docker and Docker Compose to make deployment seamless. 

### Prerequisites
- Docker
- Docker Compose

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pedrohgoncalvess/pgwarden.git
   cd pgwarden
   ```

2. **Set up the Environment Variables**
   Create a `.env` file referencing the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```
   *Make sure you define a strong `ENCRYPTION_KEY`. This key will be used by the API and the Collector to securely encrypt and decrypt the credentials of your monitored remote servers!*

3. **Start the Application**
   Run the full stack (TimescaleDB, Backend API + bundled Web UI, Collector, Migrations) with one command:
   ```bash
   docker compose up -d --build
   ```

4. **Access the Dashboards**
   The Web UI and the API are served by the same container on the same port (the SPA is baked into the api image at build time and served alongside `/v1/*`):

   | What                | URL                                               |
   |---------------------|---------------------------------------------------|
   | Web UI              | http://localhost:8080                             |
   | REST API base       | http://localhost:8080/v1                          |
   | Swagger / API docs  | http://localhost:8080/docs                        |
   | OpenAPI schema      | http://localhost:8080/openapi.json                |

   If you set `API_PORT` in `.env`, swap `8080` for that value. Default login (override via `PGWARDEN_EMAIL` / `PGWARDEN_PASSWORD` in `.env`):

   ```text
   email:    admin@pgwarden.com
   password: admin
   ```

5. **Working on the frontend**
   The compose stack ships a built bundle. To iterate on the UI with HMR, run the Vite dev server alongside the dockerized api:
   ```bash
   cd frontend
   npm install
   npm run dev   # serves http://localhost:5173
   ```
   The dev server proxies `/v1/*` to the api on `http://localhost:8080`, so it's same-origin (no CORS) just like the production bundle.

## ⚙️ Architecture

PGWarden is composed of several independent but heavily integrated services:

- **Database (TimescaleDB/PostgreSQL):** Stores both the application state (registered servers, auth, configuration) and the collected time-series metrics.
- **Collector:** A continuous, asynchronous python worker that spans out to all registered target databases, polls their states based on a configurable interval, and pushes the data back to the central database.
- **Migrations Service:** Automatically manages the central schema structure upon startup.
- **REST API + Web UI:** A FastAPI service handling authentication, target registration, config loading, and data serving. The React SPA is built as a stage of the api image and served by FastAPI itself at `/`, so the api and the dashboard share one container, one port, and one origin (no CORS, no reverse proxy).

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request, report Bugs, or suggest new Features. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open-source and available under the standard MIT License.
