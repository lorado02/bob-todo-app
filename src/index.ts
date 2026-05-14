#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { simpleGit, SimpleGit } from "simple-git";
import { Octokit } from "@octokit/rest";
import { z } from "zod";
import * as fs from "fs/promises";
import * as path from "path";

// Initialize GitHub client if token is provided
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const octokit = GITHUB_TOKEN ? new Octokit({ auth: GITHUB_TOKEN }) : null;

// Git operation schemas
const InitRepoSchema = z.object({
  path: z.string().describe("Path to initialize git repository"),
});

const CreateFileSchema = z.object({
  path: z.string().describe("Path where to create the file"),
  content: z.string().describe("Content of the file"),
  message: z.string().describe("Commit message"),
});

const CommitSchema = z.object({
  path: z.string().describe("Repository path"),
  message: z.string().describe("Commit message"),
  files: z.array(z.string()).optional().describe("Specific files to commit (optional, commits all if not specified)"),
});

const CreateBranchSchema = z.object({
  path: z.string().describe("Repository path"),
  branchName: z.string().describe("Name of the new branch"),
  checkout: z.boolean().optional().describe("Whether to checkout the new branch"),
});

const GetStatusSchema = z.object({
  path: z.string().describe("Repository path"),
});

const CreateGitignoreSchema = z.object({
  path: z.string().describe("Path where to create .gitignore"),
  templates: z.array(z.string()).describe("Templates to include (e.g., ['Python', 'Node'])"),
});

// Define available tools
const tools: Tool[] = [
  {
    name: "git_init",
    description: "Initialize a new git repository in the specified directory",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Path to initialize git repository",
        },
      },
      required: ["path"],
    },
  },
  {
    name: "git_create_file",
    description: "Create a file and optionally commit it",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Path where to create the file",
        },
        content: {
          type: "string",
          description: "Content of the file",
        },
        message: {
          type: "string",
          description: "Commit message",
        },
      },
      required: ["path", "content", "message"],
    },
  },
  {
    name: "git_commit",
    description: "Create a commit with staged or specified files",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Repository path",
        },
        message: {
          type: "string",
          description: "Commit message",
        },
        files: {
          type: "array",
          items: { type: "string" },
          description: "Specific files to commit (optional, commits all if not specified)",
        },
      },
      required: ["path", "message"],
    },
  },
  {
    name: "git_create_branch",
    description: "Create a new git branch",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Repository path",
        },
        branchName: {
          type: "string",
          description: "Name of the new branch",
        },
        checkout: {
          type: "boolean",
          description: "Whether to checkout the new branch",
        },
      },
      required: ["path", "branchName"],
    },
  },
  {
    name: "git_status",
    description: "Get the status of the git repository",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Repository path",
        },
      },
      required: ["path"],
    },
  },
  {
    name: "create_gitignore",
    description: "Create a .gitignore file with common templates for specified languages/frameworks",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Path where to create .gitignore",
        },
        templates: {
          type: "array",
          items: { type: "string" },
          description: "Templates to include (e.g., ['Python', 'Node'])",
        },
      },
      required: ["path", "templates"],
    },
  },
];

// Gitignore templates
const gitignoreTemplates: Record<string, string> = {
  Python: `# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# Virtual Environment
venv/
ENV/
env/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Database
*.db
*.sqlite
*.sqlite3`,
  
  Node: `# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs
lib-cov

# Coverage directory
coverage
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Output of 'npm pack'
*.tgz

# Yarn
.yarn-integrity
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*`,

  OS: `# OS
.DS_Store
Thumbs.db`,
};

// Create MCP server
const server = new Server(
  {
    name: "github-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "git_init": {
        const { path: repoPath } = InitRepoSchema.parse(args);
        const git: SimpleGit = simpleGit(repoPath);
        await git.init();
        
        return {
          content: [
            {
              type: "text",
              text: `Successfully initialized git repository at ${repoPath}`,
            },
          ],
        };
      }

      case "git_create_file": {
        const { path: filePath, content, message } = CreateFileSchema.parse(args);
        const dir = path.dirname(filePath);
        await fs.mkdir(dir, { recursive: true });
        await fs.writeFile(filePath, content, "utf-8");
        
        const git: SimpleGit = simpleGit(path.dirname(filePath));
        await git.add(path.basename(filePath));
        await git.commit(message);
        
        return {
          content: [
            {
              type: "text",
              text: `Successfully created file ${filePath} and committed with message: ${message}`,
            },
          ],
        };
      }

      case "git_commit": {
        const { path: repoPath, message, files } = CommitSchema.parse(args);
        const git: SimpleGit = simpleGit(repoPath);
        
        if (files && files.length > 0) {
          await git.add(files);
        } else {
          await git.add(".");
        }
        
        const result = await git.commit(message);
        
        return {
          content: [
            {
              type: "text",
              text: `Successfully created commit: ${result.commit}\nMessage: ${message}\nFiles changed: ${result.summary.changes}`,
            },
          ],
        };
      }

      case "git_create_branch": {
        const { path: repoPath, branchName, checkout } = CreateBranchSchema.parse(args);
        const git: SimpleGit = simpleGit(repoPath);
        
        if (checkout) {
          await git.checkoutLocalBranch(branchName);
        } else {
          await git.branch([branchName]);
        }
        
        return {
          content: [
            {
              type: "text",
              text: `Successfully created branch ${branchName}${checkout ? " and checked it out" : ""}`,
            },
          ],
        };
      }

      case "git_status": {
        const { path: repoPath } = GetStatusSchema.parse(args);
        const git: SimpleGit = simpleGit(repoPath);
        const status = await git.status();
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(status, null, 2),
            },
          ],
        };
      }

      case "create_gitignore": {
        const { path: repoPath, templates } = CreateGitignoreSchema.parse(args);
        
        let content = "# Generated .gitignore\n\n";
        for (const template of templates) {
          if (gitignoreTemplates[template]) {
            content += `${gitignoreTemplates[template]}\n\n`;
          }
        }
        
        // Always add OS template
        if (!templates.includes("OS")) {
          content += `${gitignoreTemplates.OS}\n`;
        }
        
        const gitignorePath = path.join(repoPath, ".gitignore");
        await fs.writeFile(gitignorePath, content, "utf-8");
        
        return {
          content: [
            {
              type: "text",
              text: `Successfully created .gitignore at ${gitignorePath} with templates: ${templates.join(", ")}`,
            },
          ],
        };
      }

      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error executing ${name}: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("GitHub MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});

// Made with Bob
