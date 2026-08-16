---
name: ruby-mcp-server-generator
description: 'Generate a complete Model Context Protocol server project in Ruby using the official MCP Ruby SDK gem.'
---

# Ruby MCP Server Generator

Generate a complete, production-ready MCP server in Ruby using the official Ruby SDK.

## Project Generation

When asked to create a Ruby MCP server, generate a complete project with this structure:

```
my-mcp-server/
├── Gemfile
├── Rakefile
├── lib/
│   ├── my_mcp_server.rb
│   ├── my_mcp_server/
│   │   ├── server.rb
│   │   ├── tools/
│   │   │   ├── greet_tool.rb
│   │   │   └── calculate_tool.rb
│   │   ├── prompts/
│   │   │   └── code_review_prompt.rb
│   │   └── resources/
│   │       └── example_resource.rb
├── bin/
│   └── mcp-server
├── test/
│   ├── test_helper.rb
│   └── tools/
│       ├── greet_tool_test.rb
│       └── calculate_tool_test.rb
└── README.md
```

## Gemfile Template

```ruby
source 'https://rubygems.org'

gem 'mcp', '~> 0.4.0'

group :development, :test do
  gem 'minitest', '~> 5.0'
  gem 'rake', '~> 13.0'
  gem 'rubocop', '~> 1.50'
end
```

## Rakefile Template

```ruby
require 'rake/testtask'
require 'rubocop/rake_task'

Rake::TestTask.new(:test) do |t|
  t.libs << 'test'
  t.libs << 'lib'
  t.test_files = FileList['test/**/*_test.rb']
end

RuboCop::RakeTask.new

task default: %i[test rubocop]
```

## lib/my_mcp_server.rb Template

```ruby
# frozen_string_literal: true

require 'mcp'
require_relative 'my_mcp_server/server'
require_relative 'my_mcp_server/tools/greet_tool'
require_relative 'my_mcp_server/tools/calculate_tool'
require_relative 'my_mcp_server/prompts/code_review_prompt'
require_relative 'my_mcp_server/resources/example_resource'

module MyMcpServer
  VERSION = '1.0.0'
end
```

## lib/my_mcp_server/server.rb Template

```ruby
# frozen_string_literal: true

module MyMcpServer
  class Server
    attr_reader :mcp_server
    
    def initialize(server_context: {})
      @mcp_server = MCP::Server.new(
        name: 'my_mcp_server',
        version: MyMcpServer::VERSION,
        tools: [
          Tools::GreetTool,
          Tools::CalculateTool
        ],
        prompts: [
          Prompts::CodeReviewPrompt
        ],
        resources: [
          Resources::ExampleResource.resource
        ],
        server_context: server_context
      )
      
      setup_resource_handler
    end
    
    def handle_json(json_string)
      mcp_server.handle_json(json_string)
    end
    
    def start_stdio
      transport = MCP::Server::Transports::StdioTransport.new(mcp_server)
      transport.open
    end
    
    private
    
    def setup_resource_handler
      mcp_server.resources_read_handler do |params|
        Resources::ExampleResource.read(params[:uri])
      end
    end
  end
end
```

## lib/my_mcp_server/tools/greet_tool.rb Template

```ruby
# frozen_string_literal: true

module MyMcpServer
  module Tools
    class GreetTool < MCP::Tool
      tool_name 'greet'
      description 'Generate a greeting message'
      
      input_schema(
        properties: {
          name: {
            type: 'string',
            description: 'Name to greet'
          }
        },
        required: ['name']
      )
      
      output_schema(
        properties: {
          message: { type: 'string' },
          timestamp: { type: 'string', format: 'date-time' }
        },
        required: ['message', 'timestamp']
      )
      
      annotations(
        read_only_hint: true,
        idempotent_hint: true
      )
      
      def self.call(name:, server_context:)
        timestamp = Time.now.iso8601
        message = "Hello, #{name}! Welcome to MCP."
        
        structured_data = {
          message: message,
          timestamp: timestamp
        }
        
        MCP::Tool::Response.new(
          [{ type: 'text', text: message }],
          structured_content: structured_data
        )
      end
    end
  end
end
```

## lib/my_mcp_server/tools/calculate_tool.rb Template

```ruby
# frozen_string_literal: true

module MyMcpServer
  module Tools
    class CalculateTool < MCP::Tool
      tool_name 'calculate'
      description 'Perform mathematical calculations'
      
      input_schema(
        properties: {
          operation: {
            type: 'string',
            description: 'Operation to perform',
            enum: ['add', 'subtract', 'multiply', 'divide']
          },
          a: {
            type: 'number',
            description: 'First operand'
          },
          b: {
            type: 'number',
            description: 'Second operand'
          }
        },
        required: ['operation', 'a', 'b']
      )
      
      output_schema(
        properties: {
          result: { type: 'number' },
          operation: { type: 'string' }
        },
        required: ['result', 'operation']
      )
      
      annotations(
        read_only_hint: true,
        idempotent_hint: true
      )
      
      def self.call(operation:, a:, b:, server_context:)
        result = case operation
                 when 'add' then a + b
                 when 'subtract' then a - b
                 when 'multiply' then a * b
                 when 'divide'
                   return error_response('Division by zero') if b.zero?
                   a / b.to_f
                 else
                   return error_response("Unknown operation: #{operation}")
                 end
        
        structured_data = {
          result: result,
          operation: operation
        }
        
        MCP::Tool::Response.new(
          [{ type: 'text', text: "Result: #{result}" }],
          structured_content: structured_data
        )
      end
      
      def self.error_response(message)
        MCP::Tool::Response.new(
          [{ type: 'text', text: message }],
          is_error: true
        )
      end
    end
  end
end
```

## lib/my_mcp_server/prompts/code_review_prompt.rb Template

```ruby
# frozen_string_literal: true

module MyMcpServer
  module Prompts
    class CodeReviewPrompt < MCP::Prompt
      prompt_name 'code_review'
      description 'Generate a code review prompt'
      
      arguments [
        MCP::Prompt::Argument.new(
          name: 'language',
          description: 'Programming language',
          required: true
        ),
        MCP::Prompt::Argument.new(
          name: 'focus',
          description: 'Review focus area (e.g., performance, security)',
          required: false
        )
      ]
      
      meta(
        version: '1.0',
        category: 'development'
      )
      
      def self.template(args, server_context:)
        language = args['language'] || 'Ruby'
        focus = args['focus'] || 'general quality'
        
        MCP::Prompt::Result.new(
          description: "Code review for #{language} with focus on #{focus}",
          messages: [
            MCP::Prompt::Message.new(
              role: 'user',
              content: MCP::Content::Text.new(
                "Please review this #{language} code with focus on #{focus}."
              )
            ),
            MCP::Prompt::Message.new(
              role: 'assistant',
              content: MCP::Content::Text.new(
                "I'll review the code focusing on #{focus}. Please share the code."
              )
            ),
            MCP::Prompt::Message.new(
              role: 'user',
              content: MCP::Content::Text.new(
                '[paste code here]'
              )
            )
          ]
        )
      end
    end
  end
end
```


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [lib/my_mcp_server/resources/example_resource.rb Template](references/extended-guidance.md#libmy_mcp_serverresourcesexample_resourcerb-template)
- [bin/mcp-server Template](references/extended-guidance.md#binmcp-server-template)
- [test/test_helper.rb Template](references/extended-guidance.md#testtest_helperrb-template)
- [test/tools/greet_tool_test.rb Template](references/extended-guidance.md#testtoolsgreet_tool_testrb-template)
- [test/tools/calculate_tool_test.rb Template](references/extended-guidance.md#testtoolscalculate_tool_testrb-template)
- [README.md Template](references/extended-guidance.md#readmemd-template)
- [Generation Instructions](references/extended-guidance.md#generation-instructions)

