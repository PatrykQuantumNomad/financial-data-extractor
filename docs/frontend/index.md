---
layout: default
title: Frontend
description: Next.js 15 frontend architecture, components, React Query, and testing
nav_order: 5
has_children: true
---

# Frontend Documentation

The Financial Data Extractor frontend is built with **Next.js 15**, **React 19**, and **TypeScript**, providing a modern, type-safe user interface for viewing and managing financial data extraction.

## Architecture Overview

The frontend uses **Next.js App Router** with:

- **Server Components** - For initial rendering and SEO
- **Client Components** - For interactivity and React Query hooks
- **React Query** - Data fetching, caching, and synchronization
- **shadcn/ui** - Accessible component library
- **Tailwind CSS 4.0** - CSS-first styling

## Key Features

- **Server Components**: Streaming SSR with Suspense boundaries
- **React Query Integration**: Automatic caching and background updates
- **Type Safety**: Full TypeScript support
- **Component Library**: shadcn/ui with Tailwind CSS
- **Comprehensive Testing**: Unit tests (100+) and integration tests

## Documentation

### Architecture

- **[Frontend Architecture](architecture.html)** - Next.js 15 architecture, component structure, and data fetching
- **[Frontend Testing](../testing/frontend.html)** - Vitest setup, React Testing Library, unit and integration tests
- **[DevTools](devtools.html)** - React Query DevTools and development tools

## Technology Stack

- **Next.js 15** - React framework with App Router
- **React 19** - Latest React features
- **TypeScript** - Type safety
- **Tailwind CSS 4.0** - Utility-first CSS
- **shadcn/ui** - Component library
- **React Query** - Data fetching and caching
- **Vitest** - Fast test runner
- **React Testing Library** - Component testing

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

See the [Frontend README](../../frontend/README.md) for detailed setup instructions.
