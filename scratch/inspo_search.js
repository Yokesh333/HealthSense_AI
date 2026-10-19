const fetch = globalThis.fetch;

async function searchInspo() {
  const queries = [
    { name: 'find_components', arguments: { type: 'features', industry: 'health', style: 'dark-mode' } },
    { name: 'find_components', arguments: { type: 'stat', industry: 'health' } },
    { name: 'find_components', arguments: { type: 'features', style: 'minimalism', vibe: 'technical' } }
  ];

  for (const q of queries) {
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
          params: { name: q.name, arguments: q.arguments }
        })
      });
      const text = await res.text();
      console.log(`--- ${q.name} ${JSON.stringify(q.arguments)} ---`);
      console.log(text.substring(0, 1500));
    } catch (err) {
      console.error(err);
    }
  }
}

searchInspo();
