# AI Story Generator - React Frontend

A modern React frontend for the AI Story Generator application, built with TypeScript, Webpack, and Tailwind CSS.

## Features

- **Modern React Architecture**: Built with React 18, TypeScript, and modern hooks
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Real-time Data**: Uses React Query for efficient data fetching and caching
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Form Handling**: React Hook Form for efficient form management
- **Notifications**: React Hot Toast for user feedback
- **Routing**: React Router for client-side navigation

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Webpack (powerful bundling and optimization)
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **Form Handling**: React Hook Form
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## Project Structure

```
frontendReact/
├── src/
│   ├── components/       # Reusable components
│   │   └── Layout.tsx   # Main layout component
│   ├── pages/           # Page components
│   │   ├── StoryGenerator.tsx
│   │   ├── Chat.tsx
│   │   ├── StoryHistory.tsx
│   │   ├── CostTracking.tsx
│   │   └── ContextManager.tsx
│   ├── services/        # API services
│   │   └── api.ts      # Axios configuration and API calls
│   ├── hooks/           # Custom React hooks
│   │   └── useApi.ts   # API hooks with error handling
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts    # All type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── package.json        # Dependencies and scripts
├── webpack.config.js   # Webpack configuration
├── tailwind.config.js  # Tailwind configuration
└── Dockerfile          # Docker configuration
```

## Getting Started

### Prerequisites

- **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node.js) or yarn
- **Backend API** running on port 8000

**Check your installation:**
```bash
node --version  # Should show v18.0.0 or higher
npm --version   # Should show npm version
```

### Development Setup

1. **Install dependencies**:
   ```bash
   cd frontendReact
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   The API URL is configured to http://localhost:8000 by default in webpack.config.js

3. **Start development server**:
   ```bash
   npm run dev
   ```
   
   The app will be available at http://localhost:5173

4. **Build for production**:
   ```bash
   npm run build
   ```

### VSCode Setup

Add these configurations to your VSCode:

**Launch Configuration** (add to `.vscode/launch.json`):
```json
{
  "name": "React Frontend",
  "type": "node",
  "request": "launch",
  "cwd": "${workspaceFolder}/frontendReact",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "dev"]
}
```

**Task Configuration** (add to `.vscode/tasks.json`):
```json
{
  "label": "Run React Frontend",
  "type": "shell",
  "command": "npm",
  "args": ["run", "dev"],
  "options": {
    "cwd": "${workspaceFolder}/frontendReact"
  },
  "group": "build",
  "presentation": {
    "echo": true,
    "reveal": "always",
    "panel": "new"
  }
}
```

## Docker Usage

### Development with Docker

```bash
# Build and run with Docker Compose (includes backend)
docker-compose -f docker-compose.separated.yml up frontend-react --build

# Access the app
# React Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

### Production Build

```bash
# Build Docker image
docker build -t ai-story-react ./frontendReact

# Run container
docker run -p 5173:80 ai-story-react
```

## Features Overview

### 1. Story Generation
- **Multi-framework support**: Semantic Kernel, LangChain, LangGraph
- **Real-time generation**: Loading states and progress indicators
- **Copy/Download**: Export stories as text files
- **Character validation**: Form validation with error messages

### 2. Chat Interface
- **Conversation management**: Create, select, and delete conversations
- **Real-time messaging**: Instant message updates
- **Framework switching**: Change AI framework on the fly
- **Message history**: Persistent conversation history

### 3. Story History
- **Search functionality**: Find stories by character names
- **Responsive grid**: Adaptive layout for different screen sizes
- **Story preview**: Quick preview with full story modal
- **Export options**: Download individual stories

### 4. Cost Tracking
- **Usage analytics**: Track requests, tokens, and costs
- **Date filtering**: Custom date range selection
- **Visual summaries**: Statistics cards and tables
- **Framework breakdown**: Usage by AI framework

### 5. Context Management
- **File upload**: Support for multiple file formats
- **Context execution**: Run prompts with file context
- **File management**: Upload, view, and delete context files
- **Execution history**: Track previous prompt executions

## API Integration

The frontend communicates with the backend through a well-defined API layer:

### API Service Layer
- **Centralized configuration**: Single Axios instance with interceptors
- **Error handling**: Automatic error processing and user notifications
- **Type safety**: Full TypeScript support for all API calls
- **Request/Response logging**: Development debugging support

### Custom Hooks
- **useApi**: Generic hook for API calls with loading states
- **useApiQuery**: Automatic data fetching with React Query
- **useApiMutation**: Optimistic updates and error handling

## Styling and UI

### Tailwind CSS
- **Utility-first**: Rapid development with utility classes
- **Responsive design**: Mobile-first responsive components
- **Custom components**: Reusable component classes
- **Consistent spacing**: Systematic spacing and sizing

### Component Design
- **Consistent patterns**: Standardized card, button, and form styles
- **Loading states**: Skeleton screens and spinners
- **Error states**: User-friendly error messages
- **Success feedback**: Toast notifications for actions

## Performance Optimizations

1. **Code Splitting**: Automatic route-based code splitting
2. **React Query**: Intelligent caching and background updates
3. **Optimistic Updates**: Immediate UI updates for better UX
4. **Image Optimization**: Proper image loading and caching
5. **Bundle Analysis**: Webpack's bundle optimization and splitting

## Comparison with Alpine.js Frontend

| Feature | React Frontend | Alpine.js Frontend |
|---------|---------------|-------------------|
| **Learning Curve** | Moderate (React knowledge required) | Minimal (HTML + minimal JS) |
| **Build Process** | Yes (Webpack bundling) | No (direct HTML serving) |
| **TypeScript** | Full support | None |
| **State Management** | React Query + useState | Alpine.js reactivity |
| **Component Reusability** | High (JSX components) | Low (HTML templates) |
| **SEO** | SPA (needs SSR for SEO) | Better (server-rendered HTML) |
| **Bundle Size** | Larger (~200KB gzipped) | Smaller (~50KB) |
| **Development Speed** | Fast (with tooling) | Very fast (no build) |
| **Scalability** | Excellent | Good for small/medium apps |
| **Testing** | Comprehensive testing tools | Limited testing options |

## Deployment

### Development
```bash
# Start all services
npm run dev  # React frontend on :5173
python backend/main.py  # Backend on :8000
```

### Production with Docker
```bash
# Build and deploy
docker-compose -f docker-compose.separated.yml up --build

# Access points:
# - React Frontend: http://localhost:5173
# - Alpine.js Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
```

### Environment Variables
- `API_URL`: Backend API URL (default: http://localhost:8000)
- `APP_NAME`: Application name
- `APP_VERSION`: Application version

Note: Environment variables are now defined in webpack.config.js using DefinePlugin

## Contributing

1. Follow TypeScript best practices
2. Use React Hook Form for form handling
3. Implement proper error boundaries
4. Add loading states for all async operations
5. Use Tailwind CSS for styling
6. Write type-safe API calls
7. Test components with user interactions

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend
   - Verify API URL in webpack.config.js proxy configuration

2. **Build Failures**:
   - Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
   - Check TypeScript errors: `npm run build`

3. **Styling Issues**:
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS rules
   - Verify responsive breakpoints

### Development Tips

- Use React DevTools for debugging
- Enable React Query DevTools in development
- Use Webpack's HMR for fast development
- Check browser console for TypeScript errors
- Use ESLint for code quality

## Future Enhancements

- [ ] Add React Router v6 with nested routes
- [ ] Implement React Suspense for better loading
- [ ] Add React Hook Form with Zod validation
- [ ] Create Storybook for component documentation
- [ ] Add comprehensive testing with Jest
- [ ] Implement PWA features
- [ ] Add internationalization (i18n)
- [ ] Create component library for reusability