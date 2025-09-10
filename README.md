# Website Reflection

A modern web tool that scans websites and generates comprehensive messaging analysis. Built with Next.js, FastAPI, and AI-powered content analysis.

## 🪞 Core Concept

Website Reflection acts as a "mirror for your website" - it crawls your site, extracts content, and provides a one-page reflection showing what message your site really sends to visitors.

## 🚀 Features

- **Smart Website Crawling**: Respects robots.txt and crawls within limits
- **AI-Powered Analysis**: Uses OpenAI to analyze messaging, clarity, and consistency  
- **Beautiful Mirror-Themed UI**: Dark mode with glass effects and smooth animations
- **Comprehensive Scoring**: Rates clarity, consistency, differentiation, proof, CTA strength, and audience fit
- **Actionable Insights**: Provides "Quick Wins" list with easy improvements
- **Export Options**: Share links and download PDF reports

## 🛠 Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **Tailwind CSS** + **shadcn/ui**
- **Radix UI** (accessible components)
- **Framer Motion** (animations)
- **Inter/Geist Sans** typography

### Backend
- **FastAPI** (Python)
- **Crawl4AI** (LLM-friendly crawler)
- **Trafilatura** (text extraction)
- **OpenAI API** (content analysis)
- **PostgreSQL** (data storage)
- **Redis** (job queue)

### Infrastructure
- **Docker** containers
- **Docker Compose** orchestration

## 🏃‍♂️ Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd WebsiteReflection
   cp .env.example .env
   ```

2. **Add your OpenAI API key** to `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```

3. **Start with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
WebsiteReflection/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/            # Utilities and configurations
│   │   └── styles/         # Global styles
│   ├── public/             # Static assets
│   └── Dockerfile
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml      # Container orchestration
└── README.md
```

## 🎨 Design Philosophy

- **SOLID Principles**: Single responsibility, open/closed, interface segregation
- **DRY**: Don't repeat yourself - reusable components and services
- **KISS**: Keep it simple - clean, readable code
- **Modern UX**: Dark mode, micro-interactions, accessibility-first

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

## 📊 API Endpoints

- `POST /api/reflect` - Start website analysis
- `GET /api/reflect/{job_id}` - Get analysis status/results
- `GET /api/reports/{report_id}` - Get detailed report
- `POST /api/reports/{report_id}/pdf` - Generate PDF export

## 🤝 Contributing

1. Follow the established patterns and principles
2. Write tests for new features
3. Update documentation as needed
4. Use conventional commits

## 📄 License

MIT License - see LICENSE file for details
