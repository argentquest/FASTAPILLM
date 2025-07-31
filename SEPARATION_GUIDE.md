# Frontend-Backend Separation Guide

This guide explains the new separated architecture using Alpine.js + HTMX for the frontend and FastAPI for the backend.

## Architecture Overview

The application now offers multiple frontend options with a shared backend:

1. **Backend** - FastAPI API server that handles all business logic and returns both JSON and HTML fragments
2. **Frontend Options**:
   - **Alpine.js + HTMX** (`/frontend/`) - Lightweight, server-driven frontend with minimal JavaScript
   - **React** (`/frontendReact/`) - Modern SPA with TypeScript, Vite, and Tailwind CSS

## Key Changes

### Frontend (Alpine.js + HTMX)

- **Location**: `/frontend/` directory
- **Technology**: 
  - Alpine.js for client-side state management
  - HTMX for server interactions without writing JavaScript
  - Bootstrap for styling
  - Nginx for serving static files and proxying API requests

### Backend (FastAPI)

- **Location**: Original location with additions in `/backend/` directory
- **New Features**:
  - Template support for returning HTML fragments
  - HTMX-specific routes that return HTML instead of JSON
  - Enhanced CORS configuration for frontend communication

## Running the Separated Architecture

### Development Mode

1. **Backend Only**:
   ```bash
   cd backend
   python main.py
   ```

2. **Frontend with Live Backend**:
   ```bash
   # Terminal 1 - Run backend
   python backend/main.py
   
   # Terminal 2 - Serve frontend (requires a local web server)
   cd frontend
   python -m http.server 3000
   ```

### Docker Mode (Recommended)

```bash
# Run both frontend and backend
docker-compose -f docker-compose.separated.yml up --build

# With PostgreSQL
docker-compose -f docker-compose.separated.yml --profile with-postgres up --build

# With Redis
docker-compose -f docker-compose.separated.yml --profile with-redis up --build
```

## Access Points

- **Alpine.js Frontend**: http://localhost:3000
- **React Frontend**: http://localhost:3001  
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

## HTMX Endpoints

The backend now provides HTMX-specific endpoints that return HTML fragments:

- `POST /htmx/story` - Generate story and return HTML
- `GET /htmx/conversations` - Get conversation list as HTML
- `POST /htmx/chat` - Send chat message and return HTML
- `GET /htmx/cost/usage` - Get cost data as HTML
- `GET /htmx/stories/search` - Search stories and return HTML

## Benefits of This Architecture

1. **Clear Separation** - Frontend and backend can be developed and deployed independently
2. **Better Scaling** - Each service can be scaled based on its specific needs
3. **Modern Development** - Use modern frontend tools while keeping backend focused
4. **Minimal JavaScript** - HTMX reduces the need for complex client-side code
5. **Progressive Enhancement** - Works without JavaScript, enhanced with Alpine.js
6. **SEO Friendly** - Server-rendered HTML content

## Migration Notes

### For Existing Code

- All existing API endpoints remain unchanged
- New HTMX endpoints are added alongside existing JSON APIs
- Frontend HTML files have been updated to use Alpine.js and HTMX
- Static files are now served by Nginx instead of FastAPI

### For New Features

1. Create HTMX endpoint in backend that returns HTML fragment
2. Add Alpine.js component for client-side state if needed
3. Use HTMX attributes to connect frontend to backend

## Example: Adding a New Feature

1. **Backend** - Create HTMX route:
   ```python
   @router.get("/htmx/feature")
   async def get_feature_htmx(request: Request):
       data = await get_feature_data()
       return templates.TemplateResponse(
           "fragments/feature.html",
           {"request": request, "data": data}
       )
   ```

2. **Template** - Create HTML fragment:
   ```html
   <!-- backend/templates/fragments/feature.html -->
   <div class="feature-content">
       <h3>{{ data.title }}</h3>
       <p>{{ data.description }}</p>
   </div>
   ```

3. **Frontend** - Add HTMX trigger:
   ```html
   <div hx-get="/htmx/feature" 
        hx-trigger="load"
        hx-target="#feature-container">
       Loading...
   </div>
   <div id="feature-container"></div>
   ```

## Deployment Considerations

1. **Frontend** can be deployed to any static hosting (CDN, S3, Netlify)
2. **Backend** can be deployed to any Python hosting (AWS ECS, Google Cloud Run, Heroku)
3. Configure CORS properly for production domains
4. Use environment variables for API endpoints

## Rollback Plan

If you need to revert to the monolithic architecture:

1. Use the original `docker-compose.yml`
2. Run `python main.py` from the root directory
3. Access the application at http://localhost:8000

The original code remains intact and functional.