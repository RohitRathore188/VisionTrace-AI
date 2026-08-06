# VisionTrace AI - Frontend

Intelligent Video Search Platform - React Frontend

## Features

✅ **React 18** with TypeScript  
✅ **Vite** - Fast build tool with HMR  
✅ **TailwindCSS** - Utility-first CSS framework  
✅ **Shadcn UI** - Beautiful, accessible components  
✅ **React Router v6** - Client-side routing  
✅ **TanStack Query** - Server state management  
✅ **Zustand** - Client state management  
✅ **Axios** - HTTP client with interceptors  
✅ **Theme Support** - Light/Dark/System themes  
✅ **Responsive Design** - Mobile-first approach  
✅ **Error Boundaries** - Graceful error handling  
✅ **Loading States** - Skeleton loaders & spinners  

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set VITE_API_BASE_URL to your backend URL
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Header, Sidebar, AppLayout)
│   │   ├── theme/           # Theme provider and toggle
│   │   └── ui/              # Reusable UI components (Button, Card, etc.)
│   ├── lib/
│   │   ├── api.ts           # Axios instance with interceptors
│   │   └── utils.ts         # Utility functions
│   ├── pages/               # Page components
│   │   ├── DashboardPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── router/              # React Router configuration
│   │   └── index.tsx
│   ├── styles/              # Global styles
│   │   └── globals.css
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx              # Root component
│   └── main.tsx             # Application entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # TailwindCSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Architecture

### Component Organization

```
components/
├── layout/         # App shell components
├── theme/          # Theme management
└── ui/             # Reusable UI primitives
```

### Routing

Routes are defined in `src/router/index.tsx`:

- `/` → Redirects to `/dashboard`
- `/dashboard` → Dashboard page
- Future routes: `/videos`, `/search`, `/results`, `/history`, `/admin`
- `*` → 404 Not Found page

### State Management

- **Server State**: TanStack Query for API data
- **Client State**: Zustand for global UI state
- **Theme**: React Context for theme management

### API Layer

Axios instance with automatic:
- Request ID injection
- Authorization header injection
- Token refresh on 401
- Error transformation

### Theming

Supports three themes:
- **Light** - Light color scheme
- **Dark** - Dark color scheme
- **System** - Follows OS preference

Theme is persisted to localStorage.

## Styling

### TailwindCSS

Utility-first CSS framework with custom theme:

```tsx
// Example
<div className="bg-background text-foreground">
  <h1 className="text-2xl font-bold">Hello</h1>
</div>
```

### CSS Variables

Theme colors are CSS variables defined in `globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  /* ... */
}
```

### Component Variants

Using `class-variance-authority`:

```tsx
const buttonVariants = cva(
  'base-classes',
  {
    variants: {
      variant: {
        default: 'bg-primary',
        outline: 'border bg-transparent',
      },
    },
  }
)
```

## TypeScript

Full type safety with strict mode enabled:

```tsx
// Type-safe API responses
interface User {
  id: string
  email: string
  role: 'admin' | 'analyst' | 'viewer'
}

// Type-safe props
interface ButtonProps {
  variant?: 'default' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}
```

## Responsive Design

Mobile-first approach with Tailwind breakpoints:

```tsx
// Responsive classes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  {/* Columns adjust based on screen size */}
</div>
```

Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

## Error Handling

### Error Boundary

Catches React errors and displays fallback UI:

```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### API Errors

Axios interceptor transforms all API errors:

```tsx
try {
  await api.get('/endpoint')
} catch (error) {
  if (isApiError(error)) {
    console.error(error.message, error.code)
  }
}
```

## Loading States

### Skeleton Loaders

```tsx
import { Skeleton } from '@/components/ui/skeleton'

<Skeleton className="h-4 w-full" />
```

### Spinners

```tsx
import { LoadingSpinner } from '@/components/ui/loading-spinner'

<LoadingSpinner size="lg" />
```

## Environment Variables

Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_ANALYTICS=false
```

Access in code:

```ts
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## Building for Production

```bash
# Build
npm run build

# Preview build locally
npm run preview
```

Output is in `dist/` directory.

### Deployment

Deploy to:
- **Vercel** (recommended)
- **Netlify**
- **AWS S3 + CloudFront**
- **Nginx** (self-hosted)

## Browser Support

- Chrome 110+
- Firefox 110+
- Edge 110+
- Safari 16+

## Performance

- Code splitting with React Router
- Lazy loading for routes
- Image optimization
- Tree shaking
- Minification

## Next Steps

1. ✅ Foundation complete
2. ⏭️ Add authentication pages
3. ⏭️ Add video upload UI
4. ⏭️ Add search interface
5. ⏭️ Add results display
6. ⏭️ Add video player
7. ⏭️ Add admin dashboard

## Troubleshooting

### Port Already in Use

Change port in `vite.config.ts`:

```ts
export default defineConfig({
  server: {
    port: 3000, // Change port
  },
})
```

### Module Not Found

Clear cache and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

Run type check:

```bash
npm run type-check
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `npm run lint` and `npm run type-check`
4. Submit a pull request

## License

Proprietary - VisionTrace AI Team
