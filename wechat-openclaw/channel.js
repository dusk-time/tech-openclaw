/**
 * WeChat Channel for OpenClaw
 * 
 * This channel connects to the WeChat HTTP service.
 */

const http = require('http');
const EventEmitter = require('events');

class WeChatChannel extends EventEmitter {
  static id = 'wechat';
  static displayName = 'WeChat Personal';
  
  constructor(config = {}) {
    super();
    this.config = {
      serverUrl: config.serverUrl || 'http://127.0.0.1:18788',
      dmPolicy: config.dmPolicy || 'pairing',
      groupPolicy: config.groupPolicy || 'allowlist',
      requireMention: config.requireMention !== false,
      ...config
    };
    
    this.connected = false;
    this.polling = false;
  }
  
  /**
   * Make HTTP request to Python service
   */
  async request(method, path, data = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, this.config.serverUrl);
      
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
      req.setTimeout(10000, () => {
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
   * Initialize the channel
   */
  async initialize() {
    try {
      const status = await this.request('GET', '/status');
      this.connected = status.window_found;
      
      if (this.connected) {
        console.log('[WeChat] Channel initialized');
      } else {
        console.log('[WeChat] Warning: WeChat window not found');
      }
      
      return true;
    } catch (error) {
      console.error('[WeChat] Initialize failed:', error.message);
      return false;
    }
  }
  
  /**
   * Send a message
   */
  async send(options) {
    const { to, message, channel = 'wechat' } = options;
    
    try {
      const result = await this.request('POST', '/send', {
        to,
        message
      });
      
      if (result.status === 'success') {
        return {
          success: true,
          id: Date.now().toString(),
          channel,
          to,
          content: message
        };
      } else {
        throw new Error(result.message || 'Send failed');
      }
    } catch (error) {
      console.error('[WeChat] Send failed:', error.message);
      throw error;
    }
  }
  
  /**
   * Start listening for messages (polling)
   */
  async startListening() {
    if (this.polling) return;
    
    this.polling = true;
    console.log('[WeChat] Starting message polling...');
    
    // WeChat polling would go here
    // For now, this is a placeholder since image-based approach
    // doesn't receive messages automatically
    
    // Emit a test message for demo
    setTimeout(() => {
      this.emit('message', {
        id: Date.now().toString(),
        channel: 'wechat',
        type: 'private',
        chat: { id: 'test', name: 'Test Chat' },
        sender: { id: 'user', name: 'User' },
        content: 'Test message',
        timestamp: Date.now()
      });
    }, 5000);
  }
  
  /**
   * Stop listening
   */
  async stopListening() {
    this.polling = false;
    console.log('[WeChat] Stopped listening');
  }
  
  /**
   * Get channel status
   */
  async getStatus() {
    try {
      const status = await this.request('GET', '/status');
      return {
        connected: this.connected,
        ...status
      };
    } catch (error) {
      return {
        connected: false,
        error: error.message
      };
    }
  }
  
  /**
   * Get capabilities
   */
  getCapabilities() {
    return {
      name: 'wechat',
      displayName: 'WeChat Personal',
      features: [
        'text',
        'images',  // Partial support
        'groups',
        'memory'
      ],
      limits: {
        messageLength: 2000
      },
      configFields: [
        'serverUrl',
        'dmPolicy',
        'groupPolicy',
        'requireMention'
      ]
    };
  }
}

module.exports = WeChatChannel;
