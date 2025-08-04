# Frontend-Backend Separation Guide

This guide explains the modern separated architecture using React + TypeScript for the frontend and FastAPI for the backend, with integrated MCP (Model Context Protocol) server support.

## Architecture Overview

The application now offers multiple frontend options with a shared backend:

1. **Backend** (`/backend/`) - FastAPI API server with integrated MCP server
   - RESTful API endpoints for all functionality
   - Embedded MCP server for external tool integration
   - Comprehensive logging and monitoring
   - Database management with SQLAlchemy
2. **Frontend** (`/frontendReact/`) - Modern React SPA
   - TypeScript, Vite, and Tailwind CSS
   - Real-time data with React Query
   - Responsive design with comprehensive UI components
   - Full type safety and error handling

## Key Changes

### Frontend (React + TypeScript)

- **Location**: `/frontendReact/` directory
- **Technology**: 
  - React 18 with TypeScript for type safety
  - Vite for fast development and building
  - Tailwind CSS for responsive styling
  - React Query for efficient data fetching
  - React Hook Form for form management
  - Axios for HTTP requests with interceptors

### Backend (FastAPI + MCP)

- **Location**: `/backend/` directory
- **Key Features**:
  - RESTful API with comprehensive endpoints
  - Integrated MCP server for external tool access
  - Multi-framework AI service support
  - Real-time cost tracking and analytics
  - File-based context management
  - Structured logging with web viewer
  - Database migrations with Alembic

## Running the Separated Architecture

### Development Mode

1. **Backend Only**:
   ```bash
   python backend/main.py
   ```

2. **Full Stack Development**:
   ```bash
   # Terminal 1 - Backend with MCP server
   python backend/main.py
   
   # Terminal 2 - React development server
   cd frontendReact
   npm install
   npm run dev
   ```

### Docker Mode (Recommended)

```bash
# Run both frontend and backend
docker-compose -f docker-compose.separated.yml up --build

# Production deployment with environment-specific configs
docker-compose -f docker-compose.separated.yml --profile production up --build
```

## Access Points

- **React Frontend**: http://localhost:3001  
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8000/mcp
- **Log Viewer**: http://localhost:8000/logs

## MCP Integration

The backend includes an embedded MCP (Model Context Protocol) server:

- `GET /mcp` - MCP server tool discovery
- `POST /mcp` - MCP tool execution
- **Available Tools**:
  - `generate_story_semantic_kernel` - Story generation with Semantic Kernel
  - `generate_story_langchain` - Story generation with LangChain
  - `generate_story_langgraph` - Story generation with LangGraph

**Note**: The `compare_frameworks` tool has been removed. See [FRAMEWORK_COMPARISON.md](FRAMEWORK_COMPARISON.md) for details.

## Benefits of This Architecture

1. **Clear Separation** - Frontend and backend can be developed and deployed independently
2. **Better Scaling** - Each service can be scaled based on its specific needs
3. **Modern Development** - React with TypeScript for robust frontend development
4. **Type Safety** - Full TypeScript support across the entire frontend
5. **Performance** - Vite for fast development and optimized production builds
6. **Real-time Features** - React Query for efficient data synchronization
7. **MCP Integration** - Built-in support for external tool integration

## Migration Notes

### For Existing Code

- All existing API endpoints remain unchanged and are fully REST-compliant
- MCP server is embedded and starts automatically with the backend
- React frontend communicates via standard JSON API calls
- Database models have been expanded for comprehensive data tracking

### For New Features

1. Create REST API endpoint in backend with proper TypeScript types
2. Add React component with TypeScript interfaces
3. Use React Query for data fetching and caching
4. Add MCP tool if external integration is needed

## Example: Adding a New Feature

1. **Backend** - Create REST endpoint:
   ```python
   @router.get("/api/feature")
   async def get_feature(db: Session = Depends(get_db)):
       data = await get_feature_data(db)
       return {"feature": data}
   ```

2. **Types** - Define TypeScript interfaces:
   ```typescript
   // types/index.ts
   interface Feature {
     id: string;
     title: string;
     description: string;
   }
   ```

3. **Frontend** - Create React component:
   ```tsx
   // components/FeatureComponent.tsx
   const FeatureComponent: React.FC = () => {
     const { data, loading } = useApiQuery(
       () => api.get('/api/feature')
     );
     
     if (loading) return <div>Loading...</div>;
     
     return (
       <div className="feature-content">
         <h3>{data.feature.title}</h3>
         <p>{data.feature.description}</p>
       </div>
     );
   };
   ```

4. **MCP Tool** (if needed for external access):
   ```python
   @mcp.tool()
   async def get_feature_data():
       """Get feature information via MCP."""
       return await get_feature_data()
   ```

## Deployment Considerations

1. **React Frontend** can be deployed to any static hosting (CDN, S3, Netlify, Vercel)
2. **Backend** can be deployed to any Python hosting (AWS ECS, Google Cloud Run, Heroku)
3. Configure CORS properly for production domains
4. Use environment variables for API endpoints
5. **MCP Server** is embedded and deploys with the backend automatically

## Rollback Plan

If you need to run legacy configurations:

1. Use the original `docker-compose.yml` for basic deployment
2. Run `python backend/main.py` for backend-only deployment
3. The separated architecture is now the recommended approach

The modern React frontend provides the best user experience and development workflow.