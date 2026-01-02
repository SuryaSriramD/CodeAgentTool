# Error Handling & Loading States - Implementation Guide

## Overview

This document describes the comprehensive error handling and loading state management implemented across the CodeAgent Scanner frontend application.

## Components Created

### 1. **Error Display Components** (`components/ui/error-display.tsx`)

Two main error display components:

#### `ErrorDisplay`

Full-page error display with retry and navigation options.

```tsx
<ErrorDisplay
  error={error}
  title="Custom Title"
  message="Custom message"
  onRetry={() => refetch()}
  showHomeButton={true}
/>
```

#### `InlineError`

Inline error message for smaller contexts.

```tsx
<InlineError error={error} message="Custom message" onRetry={() => refetch()} />
```

### 2. **Loading Components** (`components/ui/loading-spinner.tsx`)

#### `LoadingSpinner`

Reusable loading spinner with customizable size.

```tsx
<LoadingSpinner size="lg" text="Loading data..." />
```

#### `LoadingOverlay`

Overlay loading state over existing content.

```tsx
<LoadingOverlay isLoading={isLoading} text="Processing...">
  <YourContent />
</LoadingOverlay>
```

### 3. **Empty State Component** (`components/ui/empty-state.tsx`)

Display when no data is available.

```tsx
<EmptyState
  icon={FileText}
  title="No reports found"
  description="Start by creating your first scan"
  action={{ label: "New Scan", onClick: handleNewScan }}
/>
```

### 4. **Network Status Monitor** (`components/network-status.tsx`)

Real-time network connection monitoring with automatic reconnection detection.

- Displays toast notification when connection is lost
- Auto-detects when connection is restored
- Periodic health checks every 30 seconds

### 5. **Error Boundary** (`components/error-boundary.tsx`)

React error boundary to catch and handle React rendering errors.

- Prevents entire app crash
- Shows user-friendly error message
- Provides "Try Again" and "Go to Dashboard" options

## Utilities

### Error Utilities (`lib/error-utils.ts`)

#### `APIError` Class

Custom error class for API errors with status codes.

#### Helper Functions:

- `getErrorMessage(error)` - Extract error message from any error type
- `getUserFriendlyErrorMessage(error)` - Convert technical errors to user-friendly messages
- `isNetworkError(error)` - Check if error is network-related
- `isTimeoutError(error)` - Check if error is timeout-related

#### Retry with Backoff:

```tsx
const result = await retryWithBackoff(() => apiCall(), {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2,
  onRetry: (attempt, error) => console.log(`Retry ${attempt}`),
});
```

#### Timeout Wrapper:

```tsx
const result = await withTimeout(
  slowApiCall(),
  5000,
  "Request timed out after 5 seconds"
);
```

## Enhanced API Client

### `fetchWithErrorHandling` Function

Centralized fetch wrapper with:

- Automatic error parsing from API responses
- Network error detection
- User-friendly error messages
- Status code extraction

```typescript
const response = await fetchWithErrorHandling(url, options);
```

### Updated Functions:

- `getHealth()` - Health check with error handling
- `getTools()` - Tools list with error handling
- More functions can be updated to use this pattern

## React Query Configuration

Enhanced default options in `app/providers.tsx`:

```typescript
{
  queries: {
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes
    retry: 2, // Retry failed requests twice
    refetchOnWindowFocus: false, // Prevent unnecessary refetches
  },
  mutations: {
    retry: 1, // Retry failed mutations once
  },
}
```

## Integration in Pages

### Dashboard Page

```tsx
const { data, isLoading, error } = useDashboardStats();

if (isLoading) return <LoadingSpinner text="Loading dashboard..." />;
if (error) return <ErrorDisplay error={error} onRetry={() => refetch()} />;
```

### Reports Page

```tsx
const { data, isLoading, error, refetch } = useReports(filters);

if (isLoading) return <LoadingSpinner />;
if (error) return <InlineError error={error} onRetry={refetch} />;
if (!data?.items.length) return <EmptyState title="No reports" />;
```

### Job Detail Page

```tsx
const { jobInfo, isLoading, error } = useJobStatus(jobId);

if (isLoading) return <LoadingOverlay isLoading={true} />;
if (error) return <ErrorDisplay error={error} />;
```

## Error Message Mapping

### Network Errors

- "Unable to connect to the server. Please check your connection and try again."

### Timeout Errors

- "The request took too long to complete. Please try again."

### 404 Errors

- "The requested resource was not found."

### 401/403 Errors

- "You don't have permission to access this resource."

### 500 Errors

- "A server error occurred. Please try again later."

## Best Practices

### 1. Always Handle Loading States

```tsx
if (isLoading) return <LoadingSpinner text="Loading..." />;
```

### 2. Always Handle Errors

```tsx
if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
```

### 3. Always Handle Empty States

```tsx
if (!data?.length) return <EmptyState title="No data" />;
```

### 4. Use Toast Notifications for Actions

```tsx
toast({
  title: "Success",
  description: "Operation completed successfully",
});
```

### 5. Provide Retry Mechanisms

```tsx
<Button onClick={() => refetch()}>
  <RefreshCw className="mr-2 h-4 w-4" />
  Try Again
</Button>
```

### 6. Show Progress for Long Operations

```tsx
<LoadingSpinner text="Scanning repository... This may take a few minutes" />
```

## Testing Error Scenarios

### Test Network Errors

1. Stop the backend server
2. Try to access any page
3. Should show network error message

### Test Timeout Errors

1. Use `withTimeout()` with short duration
2. Should show timeout error message

### Test 404 Errors

1. Navigate to invalid job/report ID
2. Should show "Resource not found" message

### Test React Errors

1. Throw error in component render
2. Error boundary should catch and display fallback UI

## Monitoring

### Network Status

- Real-time connection monitoring
- Automatic reconnection detection
- Toast notifications for connection state changes

### Error Logging

All errors are logged to console with context:

```typescript
console.error("[Component] Error occurred:", error);
```

## Future Enhancements

1. **Error Reporting Service**

   - Integrate with Sentry or similar service
   - Automatic error reporting to monitoring service

2. **Offline Support**

   - Cache API responses
   - Queue mutations for when online

3. **Advanced Retry Strategies**

   - Exponential backoff per endpoint
   - Circuit breaker pattern
   - Rate limiting awareness

4. **User Feedback**

   - Allow users to report errors
   - Include diagnostic information
   - Send to support team

5. **Performance Monitoring**
   - Track slow API calls
   - Monitor component render times
   - Alert on performance degradation

## Summary

The application now has comprehensive error handling:

- ✅ User-friendly error messages
- ✅ Automatic retry mechanisms
- ✅ Network status monitoring
- ✅ Loading state management
- ✅ Empty state handling
- ✅ Error boundaries
- ✅ Toast notifications
- ✅ Graceful degradation

All components follow consistent patterns for error and loading states, providing a robust and reliable user experience.
