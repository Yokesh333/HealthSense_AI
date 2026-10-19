const fetch = globalThis.fetch;

async function queryInspo() {
  try {
    const res = await fetch('https://inspomcp.dev/api/mcp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'recommend',
          arguments: {
            brief: 'modern AI healthcare dashboard with clinical data cards, machine learning prediction visualization, explainable AI SHAP charts, biomedical evidence, patient analysis, analytics dashboard, professional medical aesthetic',
            industry: 'health',
            vibe: 'technical',
            color: 'cool'
          }
        }
      })
    });
    const text = await res.text();
    console.log(text);
  } catch (err) {
    console.error(err);
  }
}

queryInspo();
