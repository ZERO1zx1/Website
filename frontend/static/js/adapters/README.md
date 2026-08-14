# Frontend data adapters

`app.js` uses a small adapter contract so the same HTML/CSS/JavaScript UI can run in a frontend-only preview or with the authenticated Flask/Supabase backend. Views must consume normalized objects and must not know API route paths.

## Runtime modes

The browser selects `mockAdapter` when the HTML shell is rendered with `data-backend="mock"`. This mode is deterministic and is intended for design review without credentials. In normal backend mode, `codehavenApiAdapter` is selected. It sends the JWT from the browser session in the `Authorization: Bearer` header and normalizes API responses before the view layer renders them.

## Adapter contract

```javascript
{
  getUser: async () => {},
  getDashboard: async () => {},
  getLearningPath: async (courseId) => {},
  getProblems: async (query) => {},
  getProblem: async (problemId) => {},
  submitCode: async (payload) => {},
  getSubmission: async (submissionId) => {},
  streamSubmission: async (submissionId, onUpdate) => {}
}
```

`getProblem()` loads the editor detail response, including starter code, hints and visible test cases. `submitCode()` creates a pending submission through `POST /api/submissions`. The editor then polls `getSubmission()` until the backend reports `accepted`, `partial_accepted`, `rejected` or `error`. The queue worker and sandbox are backend responsibilities; the browser only renders pending and result states.

The adapter is the only browser layer that knows API paths, authentication headers, token persistence, SSE parsing and response normalization. `streamSubmission()` consumes the server-sent event stream from `/api/submissions/<id>/stream`; if an intermediary does not support SSE, the view falls back to status polling. Views must render loading, populated, empty, error and unauthorized states without direct route knowledge. Dynamic values must be escaped before insertion into HTML, and a live adapter failure must not silently replace authenticated data with mock data.
