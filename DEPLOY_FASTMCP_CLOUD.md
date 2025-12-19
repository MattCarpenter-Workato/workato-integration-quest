# Deploying Integration Quest to FastMCP Cloud

This guide walks you through deploying Integration Quest to [FastMCP Cloud](https://fastmcp.cloud/), a platform for hosting MCP servers with zero configuration.

## What is FastMCP Cloud?

FastMCP Cloud is a hosting platform specifically designed for MCP (Model Context Protocol) servers. It provides:

- **Zero-config deployment** from GitHub repositories
- **Free tier** for personal servers
- **Built-in authentication** (OAuth, enterprise SSO)
- **ChatMCP interface** for testing your server in the browser
- **Branch deployments** for testing changes safely

## Prerequisites

- A [GitHub](https://github.com/) account
- A fork or clone of this repository pushed to your GitHub account

## Deployment Steps

### Step 1: Fork the Repository

1. Go to [MattCarpenter-Workato/workato-integration-quest](https://github.com/MattCarpenter-Workato/workato-integration-quest)
2. Click the **Fork** button in the top right
3. Select your GitHub account as the destination

### Step 2: Sign Up for FastMCP Cloud

1. Go to [fastmcp.cloud](https://fastmcp.cloud/)
2. Click **Sign Up** or **Get Started**
3. Sign in with your GitHub account
4. Authorize FastMCP Cloud to access your repositories

### Step 3: Create a New Project

1. In FastMCP Cloud dashboard, click **New Project**
2. Select your forked `workato-integration-quest` repository
3. Configure the project:

   | Setting | Value |
   |---------|-------|
   | **Server Entrypoint** | `remote_server.py:mcp` |
   | **Branch** | `main` |

   > The entrypoint format is `filename:variable_name` where `mcp` is the FastMCP instance in `remote_server.py`.

4. Click **Deploy**

### Step 4: Wait for Build

FastMCP Cloud will:

1. Clone your repository
2. Install dependencies from `pyproject.toml`
3. Build and deploy your server
4. Provide a live URL like `https://your-project.fastmcp.app/mcp`

This typically takes 1-2 minutes.

## Connecting to Your Deployed Server

Once deployed, you'll receive a URL for your MCP server. You can connect to it from various clients:

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "integration-quest-cloud": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-project.fastmcp.app/mcp"]
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add integration-quest-cloud -- npx mcp-remote https://your-project.fastmcp.app/mcp
```

### ChatMCP (Browser)

FastMCP Cloud includes a built-in ChatMCP interface. Access it directly from your project dashboard to test your server without any local setup.

## Environment Variables

If you need to configure environment variables (not required for basic deployment):

1. Go to your project settings in FastMCP Cloud
2. Navigate to the **Environment** section
3. Add any required variables

## Troubleshooting

### Build Fails

- Ensure `pyproject.toml` is present and correctly formatted
- Check that all dependencies are listed
- Verify the entrypoint (`remote_server.py:mcp`) is correct

### Server Not Responding

- Check the deployment logs in FastMCP Cloud dashboard
- Verify the server URL is correct
- Ensure your GitHub repository is public or FastMCP has access

### Tools Not Available

- Confirm the deployment completed successfully
- Try redeploying from the dashboard
- Check that `remote_server.py` exports the `mcp` variable

## Updating Your Deployment

FastMCP Cloud automatically redeploys when you push changes to your repository:

1. Make changes locally
2. Commit and push to GitHub
3. FastMCP Cloud detects the changes and rebuilds

You can also manually trigger a redeploy from the dashboard.

## Pricing

FastMCP Cloud offers:

- **Free tier** for personal servers
- **Pay-as-you-go** pricing for teams and higher usage

Check [fastmcp.cloud](https://fastmcp.cloud/) for current pricing details.

## Resources

- [FastMCP Documentation](https://gofastmcp.com/getting-started/quickstart)
- [FastMCP Cloud](https://fastmcp.cloud/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [MCP Protocol](https://modelcontextprotocol.io/)
