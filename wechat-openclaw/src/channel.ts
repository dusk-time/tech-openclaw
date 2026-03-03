/**
 * WeChat Channel Implementation for OpenClaw
 * 
 * This module implements the OpenClaw Channel interface for WeChat.
 * It wraps wxauto to provide message receiving and sending capabilities.
 */

import { EventEmitter } from 'events';
import { WeChatListener } from './listener';
import { WeChatSender } from './sender';

export class WeChatChannel extends EventEmitter {
  static id = 'wechat';
  static displayName = 'WeChat';
  
  private wx: any = null;
  private listener: WeChatListener;
  private sender: WeChatSender;
  private config: any;
  private running: boolean = false;
  
  constructor(config: any) {
    super();
    this.config = config || {};
    this.listener = new WeChatListener(this.config);
    this.sender = new WeChatSender(this.config);
  }
  
  /**
   * Initialize the WeChat channel
   */
  async initialize(): Promise<void> {
    console.log('[WeChat] Initializing WeChat channel...');
    
    try {
      // Import wxauto dynamically (requires Windows)
      const WeChat = await import('wxauto');
      this.wx = new WeChat();
      
      // Verify WeChat is running
      const sessions = this.wx.GetSessionList();
      if (!sessions) {
        console.warn('[WeChat] No WeChat sessions found. Please ensure WeChat PC is running.');
      }
      
      console.log('[WeChat] WeChat channel initialized successfully');
    } catch (error) {
      console.error('[WeChat] Failed to initialize WeChat channel:', error);
      throw error;
    }
  }
  
  /**
   * Start listening for messages
   */
  async startListening(): Promise<void> {
    if (this.running) {
      console.warn('[WeChat] Already listening for messages');
      return;
    }
    
    console.log('[WeChat] Starting message listener...');
    this.running = true;
    
    // Start the listener
    await this.listener.start((message) => {
      this.handleIncomingMessage(message);
    });
    
    console.log('[WeChat] Message listener started');
  }
  
  /**
   * Stop listening for messages
   */
  async stopListening(): Promise<void> {
    if (!this.running) {
      return;
    }
    
    console.log('[WeChat] Stopping message listener...');
    this.running = false;
    await this.listener.stop();
    console.log('[WeChat] Message listener stopped');
  }
  
  /**
   * Handle incoming messages from the listener
   */
  private handleIncomingMessage(message: any): void {
    // Normalize message to OpenClaw format
    const normalizedMessage = this.normalizeMessage(message);
    
    if (normalizedMessage) {
      this.emit('message', normalizedMessage);
    }
  }
  
  /**
   * Normalize wxauto message to OpenClaw message format
   */
  private normalizeMessage(msg: any): any {
    try {
      const isGroup = msg.sender !== msg.chat;
      
      return {
        id: msg.id || Date.now().toString(),
        channel: 'wechat',
        type: isGroup ? 'group' : 'private',
        chat: {
          id: msg.chat,
          name: msg.chatName || msg.chat,
          type: isGroup ? 'group' : 'private'
        },
        sender: {
          id: msg.sender,
          name: msg.senderName || msg.sender,
          isSelf: msg.isSelf || false
        },
        content: msg.content || msg.text || '',
        timestamp: msg.timestamp || Date.now(),
        raw: msg
      };
    } catch (error) {
      console.error('[WeChat] Failed to normalize message:', error);
      return null;
    }
  }
  
  /**
   * Send a message to a chat
   */
  async send(options: {
    to: string;
    message: string;
    chat?: string;
  }): Promise<any> {
    try {
      const result = await this.sender.send(options.to, options.message);
      return result;
    } catch (error) {
      console.error('[WeChat] Failed to send message:', error);
      throw error;
    }
  }
  
  /**
   * Send media (image, file, etc.)
   */
  async sendMedia(options: {
    to: string;
    path: string;
    type: 'image' | 'file' | 'voice';
    caption?: string;
  }): Promise<any> {
    try {
      return await this.sender.sendMedia(options.to, options.path, options.type, options.caption);
    } catch (error) {
      console.error('[WeChat] Failed to send media:', error);
      throw error;
    }
  }
  
  /**
   * Get list of active chats
   */
  async getChatList(): Promise<any[]> {
    try {
      const sessions = this.wx?.GetSessionList() || [];
      return sessions.map((session: any) => ({
        id: session.who,
        name: session.nickname || session.who,
        type: session.type || 'private',
        unread: session.unread || 0
      }));
    } catch (error) {
      console.error('[WeChat] Failed to get chat list:', error);
      return [];
    }
  }
  
  /**
   * Mark messages as read
   */
  async markAsRead(chatId: string): Promise<void> {
    try {
      await this.wx?.ChatWith(chatId);
      // wxauto handles marking as read automatically in some cases
      console.log(`[WeChat] Marked chat ${chatId} as read`);
    } catch (error) {
      console.error('[WeChat] Failed to mark as read:', error);
    }
  }
  
  /**
   * Get channel capabilities
   */
  getCapabilities(): any {
    return {
      name: 'wechat',
      displayName: 'WeChat Personal',
      features: [
        'text',
        'images',
        'files',
        'voice',
        'groups',
        'memory',
        'mentions'
      ],
      mediaTypes: [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'audio/amr',
        'audio/mp3',
        'audio/wav',
        'file/*'
      ],
      limits: {
        messageLength: 5000,
        mediaSizeMb: 25
      },
      configFields: [
        'dmPolicy',
        'allowFrom',
        'groupPolicy',
        'requireMention',
        'avatarDir',
        'memoryEnabled'
      ]
    };
  }
  
  /**
   * Get channel status
   */
  async getStatus(): Promise<any> {
    return {
      connected: this.wx !== null,
      running: this.running,
      chats: await this.getChatList(),
      config: {
        enabled: this.config?.enabled !== false,
        dmPolicy: this.config?.dmPolicy || 'pairing',
        groupPolicy: this.config?.groupPolicy || 'allowlist',
        memoryEnabled: this.config?.memoryEnabled !== false
      }
    };
  }
  
  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    await this.stopListening();
    this.wx = null;
    console.log('[WeChat] Channel cleanup complete');
  }
}
