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

- **Node.js**: `>=22.12.0`
- npm >=10.0.0, yarn, or pnpm

#### Node.js Version Requirements

**To check your Node.js version:**

```bash
node --version
```

**To upgrade Node.js:**

If using [nvm](https://github.com/nvm-sh/nvm):

```bash
# Install Node.js 22 LTS (recommended)
nvm install 22
nvm use 22
```

Or download from [nodejs.org](https://nodejs.org/).

#### Automatic Node.js Version Switching with nvm

This project includes an `.nvmrc` file that specifies the Node.js version (22 LTS).

**To automatically switch Node.js version when entering the project:**

1. Install nvm if you haven't already: [nvm installation guide](https://github.com/nvm-sh/nvm#installing-and-updating)

2. Add this to your shell profile (`.zshrc`, `.bashrc`, or `.bash_profile`):

   ```bash
   # Auto-switch Node.js version when entering directories with .nvmrc
   autoload -U add-zsh-hook
   load-nvmrc() {
     local node_version="$(nvm version)"
     local nvmrc_path="$(nvm_find_nvmrc)"

     if [ -n "$nvmrc_path" ]; then
       local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

       if [ "$nvmrc_node_version" = "N/A" ]; then
         nvm install
       elif [ "$nvmrc_node_version" != "$node_version" ]; then
         nvm use
       fi
     elif [ "$node_version" != "$(nvm version default)" ]; then
       echo "Reverting to nvm default version"
       nvm use default
     fi
   }
   add-zsh-hook chpwd load-nvmrc
   load-nvmrc
   ```

   For bash, use:

   ```bash
   # Auto-switch Node.js version when entering directories with .nvmrc
   autoload_nvm() {
     local node_version="$(nvm version)"
     local nvmrc_path="$(nvm_find_nvmrc)"

     if [ -n "$nvmrc_path" ]; then
       local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

       if [ "$nvmrc_node_version" = "N/A" ]; then
         nvm install
       elif [ "$nvmrc_node_version" != "$node_version" ]; then
         nvm use
       fi
     elif [ "$node_version" != "$(nvm version default)" ]; then
       echo "Reverting to nvm default version"
       nvm use default
     fi
   }
   cd() { builtin cd "$@"; autoload_nvm; }
   autoload_nvm
   ```

3. **Manual switching** (if auto-switch is not set up):

   ```bash
   cd frontend
   nvm use  # Automatically uses version from .nvmrc
   ```

4. **First time setup** (if Node.js 22 is not installed):
   ```bash
   cd frontend
   nvm install  # Installs version from .nvmrc
   nvm use      # Switches to that version
   ```

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
