/**
 * WeChat Tool for OpenClaw
 * 
 * A simple tool wrapper that allows OpenClaw agents to send WeChat messages
 * by calling the Python HTTP service.
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

class WeChatTool {
  constructor() {
    this.name = 'wechat';
    this.description = 'Send WeChat messages via image-based automation';
    this.serverUrl = 'http://127.0.0.1:18788';
    this.server = null;
  }
  
  /**
   * Initialize the tool
   */
  async initialize(config = {}) {
    this.serverUrl = config.serverUrl || this.serverUrl;
    
    // Try to start the Python server if not running
    try {
      const status = await this.request('GET', '/status');
      if (!status.window_found) {
        console.log('[WeChat] WeChat window not found. Make sure WeChat is open.');
      }
    } catch (error) {
      // Server not running, try to start it
      console.log('[WeChat] Starting WeChat server...');
      this.startServer();
    }
  }
  
  /**
   * Start the Python HTTP server
   */
  startServer() {
    const serverScript = path.join(__dirname, 'wechat_server.py');
    
    this.server = spawn('python', [serverScript], {
      cwd: path.dirname(serverScript),
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    this.server.stdout.on('data', (data) => {
      console.log(`[WeChat-Server] ${data}`);
    });
    
    this.server.stderr.on('data', (data) => {
      console.error(`[WeChat-Server] ${data}`);
    });
    
    // Wait for server to start
    return new Promise((resolve) => {
      setTimeout(resolve, 2000);
    });
  }
  
  /**
   * Make HTTP request
   */
  async request(method, endpoint, data = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.serverUrl);
      
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: method,
        headers: {
          'Content-Type': 'application/json'
        }
      };
      
      const req = http.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve(body);
          }
        });
      });
      
      req.on('error', reject);
      req.setTimeout(5000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      if (data) {
        req.write(JSON.stringify(data));
      }
      
      req.end();
    });
  }
  
  /**
   * Send a message
   */
  async send(options) {
    const { to, message } = options;
    
    try {
      const result = await this.request('POST', '/send', {
        to,
        message
      });
      
      if (result.status === 'success') {
        return {
          success: true,
          to,
          message: message.substring(0, 50),
          timestamp: Date.now()
        };
      } else {
        return {
          success: false,
          error: result.message || 'Send failed'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Get status
   */
  async getStatus() {
    try {
      return await this.request('GET', '/status');
    } catch (error) {
      return {
        connected: false,
        error: error.message
      };
    }
  }
  
  /**
   * Calibrate positions
   */
  async calibrate(type, x, y) {
    try {
      return await this.request('POST', `/calibrate/${type}`, { x, y });
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Export for OpenClaw
module.exports = {
  name: 'wechat',
  description: 'Send WeChat messages',
  
  async load(openclaw) {
    console.log('[WeChat] Loading WeChat tool...');
    
    const tool = new WeChatTool();
    await tool.initialize();
    
    // Register tool functions
    openclaw.registerTool('wechat_send', async (params) => {
      return await tool.send(params);
    });
    
    openclaw.registerTool('wechat_status', async () => {
      return await tool.getStatus();
    });
    
    openclaw.registerTool('wechat_calibrate', async (params) => {
      const { type, x, y } = params;
      return await tool.calibrate(type, x, y);
    });
    
    console.log('[WeChat] WeChat tool loaded');
  },
  
  // Direct usage
  WeChatTool
};

// If run directly
if (require.main === module) {
  const tool = new WeChatTool();
  
  const command = process.argv[2];
  
  if (command === 'send') {
    const to = process.argv[3];
    const message = process.argv[4];
    if (!to || !message) {
      console.error('Usage: node wechat_tool.js send <to> <message>');
      process.exit(1);
    }
    
    tool.initialize().then(() => {
      tool.send({ to, message }).then(console.log).catch(console.error);
    });
  } else if (command === 'status') {
    tool.initialize().then(() => {
      tool.getStatus().then(console.log).catch(console.error);
    });
  } else {
    console.log('Usage:');
    console.log('  node wechat_tool.js send <to> <message>');
    console.log('  node wechat_tool.js status');
  }
}
