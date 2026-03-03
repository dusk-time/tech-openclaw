/**
 * WeChat Channel Plugin for OpenClaw
 * 
 * This plugin enables OpenClaw to connect to WeChat PC (Windows) using wxauto.
 * It provides messaging capabilities similar to Telegram Bot API.
 */

import { WeChatChannel } from './channel';
import { WeChatListener } from './listener';
import { WeChatSender } from './sender';

export {
  WeChatChannel,
  WeChatListener,
  WeChatSender
};

export default {
  name: 'wechat',
  version: '1.0.0',
  
  async load(gateway) {
    console.log('[WeChat] Loading WeChat channel plugin...');
    
    // Register the channel
    gateway.registerChannel('wechat', WeChatChannel);
    
    console.log('[WeChat] WeChat channel plugin loaded successfully');
  },
  
  async unload(gateway) {
    console.log('[WeChat] Unloading WeChat channel plugin...');
    // Cleanup logic if needed
    console.log('[WeChat] WeChat channel plugin unloaded');
  }
};
