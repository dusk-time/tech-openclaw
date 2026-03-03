#!/usr/bin/env node
/**
 * WeChat Tool for OpenClaw
 * 
 * This tool allows OpenClaw agents to send WeChat messages via Python wxauto.
 * Usage: Use the message tool with channel="wechat" or call these functions directly.
 */

const { spawn } = require('child_process');
const path = require('path');

const PYTHON_PATH = process.env.PYTHON_PATH || 'python';
const SCRIPT_DIR = __dirname;
const MESSENGER_SCRIPT = path.join(SCRIPT_DIR, 'wechat_messenger.py');

class WeChatTool {
  constructor() {
    this.name = 'wechat';
    this.description = 'Send and receive WeChat messages via wxauto';
  }
  
  /**
   * Execute Python script and get result
   */
  async execute(args) {
    return new Promise((resolve, reject) => {
      const child = spawn(PYTHON_PATH, [MESSENGER_SCRIPT, ...args], {
        cwd: SCRIPT_DIR,
        encoding: 'utf-8',
        timeout: 30000
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(stderr || `Exit code: ${code}`));
        }
      });
      
      child.on('error', reject);
    });
  }
  
  /**
   * Send a message
   */
  async send(to, message) {
    try {
      const result = await this.execute(['--send', to, message]);
      return { success: true, output: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Send an image
   */
  async sendImage(to, imagePath) {
    try {
      const result = await this.execute(['--send-image', to, imagePath]);
      return { success: true, output: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Get chat list
   */
  async getChats(listenList = []) {
    try {
      const args = ['--chats', ...listenList];
      const result = await this.execute(args);
      // Parse chat list from output
      const chats = [];
      const lines = result.split('\n');
      for (const line of lines) {
        const match = line.match(/^\s*-\s*(.+?)\s*\((.+?)\)\s*$/);
        if (match) {
          chats.push({ name: match[1], id: match[2] });
        }
      }
      return { success: true, chats };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Export for use as OpenClaw tool
module.exports = {
  name: 'wechat',
  description: 'Send and receive WeChat messages',
  actions: {
    send: {
      parameters: {
        type: 'object',
        properties: {
          to: { type: 'string', description: 'Contact or group name' },
          message: { type: 'string', description: 'Message content' }
        },
        required: ['to', 'message']
      },
      handler: async (params) => {
        const tool = new WeChatTool();
        return tool.send(params.to, params.message);
      }
    },
    sendImage: {
      parameters: {
        type: 'object',
        properties: {
          to: { type: 'string', description: 'Contact or group name' },
          path: { type: 'string', description: 'Image file path' }
        },
        required: ['to', 'path']
      },
      handler: async (params) => {
        const tool = new WeChatTool();
        return tool.sendImage(params.to, params.path);
      }
    }
  }
};

// CLI interface
if (require.main === module) {
  const tool = new WeChatTool();
  const command = process.argv[2];
  
  if (command === 'send') {
    const to = process.argv[3];
    const message = process.argv[4];
    if (!to || !message) {
      console.error('Usage: node wechat.js send <to> <message>');
      process.exit(1);
    }
    tool.send(to, message).then(console.log).catch(console.error);
  } else if (command === 'send-image') {
    const to = process.argv[3];
    const path = process.argv[4];
    if (!to || !path) {
      console.error('Usage: node wechat.js send-image <to> <path>');
      process.exit(1);
    }
    tool.sendImage(to, path).then(console.log).catch(console.error);
  } else {
    console.error('Usage: node wechat.js <command> [args]');
    console.error('Commands: send, send-image');
    process.exit(1);
  }
}
