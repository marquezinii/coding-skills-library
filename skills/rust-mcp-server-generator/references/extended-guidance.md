<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

### tests/integration_test.rs

```rust
use rmcp::{
    model::*,
    protocol::*,
    server::{RequestContext, ServerHandler, RoleServer},
};

// Replace with your actual project name in snake_case
// Example: if project is "my-mcp-server", use my_mcp_server
use my_mcp_server::handler::McpHandler;

#[tokio::test]
async fn test_list_tools() {
    let handler = McpHandler::new();
    let context = RequestContext::default();
    
    let result = handler.list_tools(None, context).await.unwrap();
    
    assert!(!result.tools.is_empty());
    assert!(result.tools.iter().any(|t| t.name == "example_tool"));
}

#[tokio::test]
async fn test_call_tool() {
    let handler = McpHandler::new();
    let context = RequestContext::default();
    
    let request = CallToolRequestParam {
        name: "example_tool".to_string(),
        arguments: Some(serde_json::json!({
            "input": "test"
        })),
    };
    
    let result = handler.call_tool(request, context).await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_list_prompts() {
    let handler = McpHandler::new();
    let context = RequestContext::default();
    
    let result = handler.list_prompts(None, context).await.unwrap();
    assert!(!result.prompts.is_empty());
}

#[tokio::test]
async fn test_list_resources() {
    let handler = McpHandler::new();
    let context = RequestContext::default();
    
    let result = handler.list_resources(None, context).await.unwrap();
    assert!(!result.resources.is_empty());
}
```

## Implementation Guidelines

1. **Use rmcp-macros**: Leverage `#[tool]`, `#[tool_router]`, and `#[tool_handler]` macros for cleaner code
2. **Type Safety**: Use `schemars::JsonSchema` for all parameter types
3. **Error Handling**: Return `Result` types with proper error messages
4. **Async/Await**: All handlers must be async
5. **State Management**: Use `Arc<RwLock<T>>` for shared state
6. **Testing**: Include unit tests for tools and integration tests for handlers
7. **Logging**: Use `tracing` macros (`info!`, `debug!`, `warn!`, `error!`)
8. **Documentation**: Add doc comments to all public items

## Example Tool Patterns

### Simple Read-Only Tool

```rust
#[derive(Debug, Deserialize, JsonSchema)]
pub struct GreetParams {
    pub name: String,
}

#[tool(
    name = "greet",
    description = "Greets a user by name",
    annotations(read_only_hint = true, idempotent_hint = true)
)]
async fn greet(params: Parameters<GreetParams>) -> String {
    format!("Hello, {}!", params.inner().name)
}
```

### Tool with Error Handling

```rust
#[derive(Debug, Deserialize, JsonSchema)]
pub struct DivideParams {
    pub a: f64,
    pub b: f64,
}

#[tool(name = "divide", description = "Divides two numbers")]
async fn divide(params: Parameters<DivideParams>) -> Result<f64, String> {
    let p = params.inner();
    if p.b == 0.0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(p.a / p.b)
    }
}
```

### Tool with State

```rust
#[tool(
    name = "increment",
    description = "Increments the counter",
    annotations(destructive_hint = true)
)]
async fn increment(state: &ServerState) -> i32 {
    state.increment().await
}
```

## Running the Generated Server

After generation:

```bash
cd {project-name}
cargo build
cargo test
cargo run
```

For Claude Desktop integration:

```json
{
  "mcpServers": {
    "{project-name}": {
      "command": "path/to/{project-name}/target/release/{project-name}",
      "args": []
    }
  }
}
```

Now generate the complete project based on the user's requirements!
