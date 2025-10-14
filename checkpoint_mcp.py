# checkpoint_mcp_server.py
import asyncio
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
from checkpoint_structure import CheckpointADT

# Create server
app = Server("checkpoint-system")

# Global checkpoint - uses default path from CheckpointADT
checkpoint = CheckpointADT()

# Define available tools
@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of available tools"""
    return [
        Tool(
            name="append_step",
            description="Add a new checkpoint step to the reasoning chain",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The query/problem"},
                    "response": {"type": "string", "description": "The reasoning step"}
                },
                "required": ["query", "response"]
            }
        ),
        Tool(
            name="rollback_to_checkpoint",
            description="Rollback to a specific checkpoint ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Checkpoint ID to rollback to"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="rollback_last_checkpoint",
            description="Remove the most recent checkpoint",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="delete_checkpoint",
            description="Delete a specific checkpoint by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Checkpoint ID to delete"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="get_checkpoint",
            description="Get details of a specific checkpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Checkpoint ID to retrieve"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="update_checkpoint",
            description="Update the response of a checkpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Checkpoint ID to update"},
                    "response": {"type": "string", "description": "New response text"}
                },
                "required": ["id", "response"]
            }
        ),
        Tool(
            name="list_all_checkpoints",
            description="List all checkpoint IDs in the chain",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_json",
            description="Update the json file with new information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

# Handle tool calls
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute the requested tool"""
    
    if name == "append_step":
        node_id = checkpoint.append(arguments["query"], arguments["response"])
        return [TextContent(
            type="text",
            text=f"✓ Added checkpoint with ID: {node_id}"
        )]
    
    elif name == "rollback_to_checkpoint":
        success = checkpoint.rollback_to(arguments["id"])
        if success:
            return [TextContent(
                type="text",
                text=f"✓ Rolled back to checkpoint {arguments['id']}"
            )]
        return [TextContent(
            type="text",
            text=f"✗ Failed to rollback to {arguments['id']}"
        )]
    
    elif name == "rollback_last_checkpoint":
        success = checkpoint.rollback_last()
        if success:
            return [TextContent(
                type="text",
                text="✓ Rolled back last checkpoint"
            )]
        return [TextContent(
            type="text",
            text="✗ Failed to rollback (no checkpoints exist)"
        )]
    
    elif name == "delete_checkpoint":
        success = checkpoint.delete_node_by_id(arguments["id"])
        if success:
            return [TextContent(
                type="text",
                text=f"✓ Deleted checkpoint {arguments['id']}"
            )]
        return [TextContent(
            type="text",
            text=f"✗ Failed to delete checkpoint {arguments['id']}"
        )]
    
    elif name == "get_checkpoint":
        result = checkpoint.get(arguments["id"])
        if result:
            query, response = result
            return [TextContent(
                type="text",
                text=json.dumps({
                    "id": arguments["id"],
                    "query": query,
                    "response": response
                }, indent=2)
            )]
        return [TextContent(
            type="text",
            text=f"✗ Checkpoint {arguments['id']} not found"
        )]
    
    elif name == "update_checkpoint":
        success = checkpoint.update(arguments["id"], arguments["response"])
        if success:
            return [TextContent(
                type="text",
                text=f"✓ Updated checkpoint {arguments['id']}"
            )]
        return [TextContent(
            type="text",
            text=f"✗ Failed to update checkpoint {arguments['id']}"
        )]
    
    elif name == "list_all_checkpoints":
        ids = []
        for node in checkpoint.traverse_forward():
            ids.append(node.id)
        return [TextContent(
            type="text",
            text=json.dumps({
                "checkpoint_ids": ids,
                "total": len(ids)
            }, indent=2)
        )]
    elif name == "update_json":
        checkpoint.update_json()
        return [TextContent(
            type="text",
            text=f"Json has been updated!"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# Run the server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="checkpoint-system",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
