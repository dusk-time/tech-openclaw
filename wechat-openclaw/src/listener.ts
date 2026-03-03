/**
 * WeChat Message Listener
 * 
 * Handles message listening and event emission for WeChat PC.
 */

import { EventEmitter } from 'events';

export class WeChatListener extends EventEmitter {
  private wx: any = null;
  private config: any;
  private running: boolean = false;
  private pollInterval: number = 1000; // 1 second
  private processedMessages: Set<string> = new Set();
  
  constructor(config: any = {}) {
    super();
    this.config = config;
  }
  
  /**
   * Start listening for messages
   */
  async start(onMessage: (message: any) => void): Promise<void> {
    console.log('[WeChat] Starting listener...');
    
    try {
      const WeChat = await import('wxauto');
      this.wx = new WeChat();
      
      // Add listening chats from config
      const listenList = this.config?.listenList || [];
      for (const chatName of listenList) {
        try {
          if (this.wx.ChatWith(chatName)) {
            this.wx.AddListenChat(who=chatName, savepic=True, savevoice=True);
            console.log(`[WeChat] Added listener for: ${chatName}`);
          }
        } catch (error) {
          console.warn(`[WeChat] Failed to add listener for ${chatName}:`, error);
        }
      }
      
      this.running = true;
      
      // Start polling
      this.pollMessages(onMessage);
      
      console.log('[WeChat] Listener started successfully');
    } catch (error) {
      console.error('[WeChat] Failed to start listener:', error);
      throw error;
    }
  }
  
  /**
   * Poll for new messages
   */
  private async pollMessages(onMessage: (message: any) => void): Promise<void> {
    const poll = async () => {
      if (!this.running || !this.wx) {
        return;
      }
      
      try {
        const messages = this.wx.GetListenMessage();
        
        if (messages) {
          for (const chat of messages) {
            const chatName = chat.who;
            const chatMessages = messages.get(chat);
            
            if (chatMessages) {
              for (const msg of chatMessages) {
                // Skip duplicate messages
                const msgId = this.getMessageId(msg);
                if (this.processedMessages.has(msgId)) {
                  continue;
                }
                
                // Skip non-text messages if configured
                if (!this.shouldProcessMessage(msg)) {
                  continue;
                }
                
                // Mark as processed
                this.processedMessages.add(msgId);
                
                // Normalize and emit
                const normalizedMessage = this.normalizeMessage(msg, chatName);
                if (normalizedMessage) {
                  onMessage(normalizedMessage);
                }
              }
            }
          }
        }
      } catch (error) {
        // Silent fail for polling - log at debug level
        console.debug('[WeChat] Poll error:', error);
      }
      
      // Schedule next poll
      if (this.running) {
        setTimeout(poll, this.pollInterval);
      }
    };
    
    poll();
  }
  
  /**
   * Get unique message ID
   */
  private getMessageId(msg: any): string {
    return `${msg.sender}-${msg.time}-${msg.content || ''}`;
  }
  
  /**
   * Determine if message should be processed
   */
  private shouldProcessMessage(msg: any): boolean {
    const content = msg.content || msg.text || '';
    
    // Skip empty messages
    if (!content && !msg.type?.includes('image')) {
      return false;
    }
    
    // Skip system messages
    if (content?.includes('[系统消息]') || content?.includes('[撤回消息]')) {
      return false;
    }
    
    return true;
  }
  
  /**
   * Normalize message to standard format
   */
  private normalizeMessage(msg: any, chatName: string): any {
    try {
      const isGroup = msg.sender !== chatName;
      
      return {
        id: this.getMessageId(msg),
        type: msg.type || 'text',
        chat: chatName,
        chatName: chatName,
        sender: msg.sender,
        senderName: msg.sender,
        senderNickName: msg.senderNickName || msg.sender,
        content: msg.content || msg.text || '',
        timestamp: msg.time ? new Date(msg.time).getTime() : Date.now(),
        isSelf: msg.isSelf || false,
        isGroup: isGroup,
        roomId: msg.roomid || null,
        raw: msg
      };
    } catch (error) {
      console.error('[WeChat] Failed to normalize message:', error);
      return null;
    }
  }
  
  /**
   * Stop listening
   */
  async stop(): Promise<void> {
    console.log('[WeChat] Stopping listener...');
    this.running = false;
    this.processedMessages.clear();
    console.log('[WeChat] Listener stopped');
  }
}
