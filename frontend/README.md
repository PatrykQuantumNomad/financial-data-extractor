# Financial Data Extractor - Frontend

Next.js 15 frontend application for the Financial Data Extractor platform.

## Tech Stack

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS 4.0** - Styling
- **shadcn/ui** - UI component library
- **SWR** - Data fetching and caching (for future use)
- **Axios** - HTTP client

## Features

- **Company Dashboard** - View all companies and navigate to their financial statements
- **Financial Statement Tables** - Display 10-year compiled views of Income Statements, Balance Sheets, and Cash Flow Statements
- **Document Viewer** - Browse scraped and classified PDF documents by company and fiscal year
- **Extraction Controls** - Trigger data extraction tasks and monitor their progress
- **Real-time Task Status** - Monitor Celery task progress with live updates

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create a `.env` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:3030
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```bash
src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (company list)
│   ├── companies/          # Company detail pages
│   └── extraction/         # Extraction management page
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── dashboard/          # Dashboard components
│   ├── statements/         # Financial statement components
│   ├── documents/          # Document viewer components
│   ├── extraction/        # Extraction task components
│   └── layout/             # Layout components (navbar, etc.)
└── lib/
    ├── api/                # API client functions
    ├── types/              # TypeScript type definitions
    └── utils/              # Utility functions
```

## API Integration

The frontend consumes the FastAPI backend at `/api/v1`. The API client is configured in `src/lib/api/client.ts` and organized by resource:

- `companiesApi` - Company CRUD operations
- `documentsApi` - Document listing and retrieval
- `statementsApi` - Compiled financial statement retrieval
- `tasksApi` - Celery task triggering and status checking

## Key Components

### Financial Statement Table

Displays compiled financial data in a table format with:

- Sticky header row
- Horizontal scrolling for multiple years
- Support for hierarchical line items (indentation)
- Restated data indicators
- Currency formatting

### Task Status Monitor

Real-time polling of Celery task status with:

- Status badges (PENDING, STARTED, SUCCESS, FAILURE)
- Error message display
- Automatic refresh on completion
