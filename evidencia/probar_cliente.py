"""Cliente MCP de prueba: se conecta por stdio al servidor y llama cada pieza."""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main(qué):
    p = StdioServerParameters(command=sys.executable, args=["mcp_server.py"], cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for q in qué:
                print("=====", q)
                try:
                    if q == "list":
                        print("tools:", [t.name for t in (await s.list_tools()).tools])
                        print("resources:", [str(x.uri) for x in (await s.list_resources()).resources])
                        print("templates:", [x.uri_template for x in (await s.list_resource_templates()).resource_templates])
                        print("prompts:", [x.name for x in (await s.list_prompts()).prompts])
                    elif q.startswith("tool:"):
                        _, name, args = q.split(":", 2)
                        res = await s.call_tool(name, json.loads(args))
                        print("isError:", res.is_error if hasattr(res,'is_error') else res.isError)
                        for c in res.content: print(c.text[:900])
                    elif q.startswith("res:"):
                        res = await s.read_resource(q[4:])
                        for c in res.contents: print(c.mime_type if hasattr(c,'mime_type') else c.mimeType, c.text[:600])
                    elif q.startswith("prompt:"):
                        _, name, args = q.split(":", 2)
                        res = await s.get_prompt(name, json.loads(args))
                        for m in res.messages: print(m.role, "|", m.content.text)
                except Exception as e:
                    print("EXCEPCION:", type(e).__name__, e)

asyncio.run(main(sys.argv[1:]))
