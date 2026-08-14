# Frontend data adapters

`app.js` uses a small adapter contract so the HTML/CSS/JavaScript UI can run without backend credentials.

## Current mode

The current `mockAdapter` lives in `../app.js` and supplies deterministic dashboard, learning path, problem and user data for frontend review.

## Integration mode

The future `apiAdapter` should implement the same methods and return the same object shapes:

```javascript
{
  getUser: async () => {},
  getDashboard: async () => {},
  getLearningPath: async () => {},
  getProblems: async () => {},
  submitCode: async () => {}
}
```

The adapter is the only browser layer that should know API paths, authentication headers, token refresh and response normalization. Views should continue to consume normalized objects and render loading, empty, error and unauthorized states without direct route knowledge.
