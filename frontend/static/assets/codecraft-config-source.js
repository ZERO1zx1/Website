window.CODECRAFT_CONFIG = Object.assign({
  API_BASE_URL: location.port === "8000" ? "" : "http://localhost:8000",
  SUPABASE_URL: "",
  SUPABASE_ANON_KEY: ""
}, window.CODECRAFT_CONFIG || {});

