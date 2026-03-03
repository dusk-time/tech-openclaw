#!/usr/bin/env node

/**
 * Cross-Session Memory Loader
 * 
 * Implements EvoMap capsule: sha256:def136049c982ed785117dff00bb3238ed71d11cf77c019b3db2a8f65b476f06
 * 
 * Features:
 * - Auto-load RECENT_EVENTS.md (24h rolling event feed)
 * - Auto-load memory/YYYY-MM-DD.md (today + yesterday)
 * - Auto-load MEMORY.md (long-term memory, main session only)
 * - Auto-append significant events on exit
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const RECENT_EVENTS_PATH = path.join(WORKSPACE, 'RECENT_EVENTS.md');
const MEMORY_MD_PATH = path.join(WORKSPACE, 'MEMORY.md');

function getTodayStr() {
  return new Date().toISOString().split('T')[0];
}

function getYesterdayStr() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return yesterday.toISOString().split('T')[0];
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`[MemoryLoader] Created directory: ${dirPath}`);
  }
}

function readFileIfExists(filePath) {
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf-8');
    console.log(`[MemoryLoader] Loaded: ${filePath}`);
    return content;
  }
  console.log(`[MemoryLoader] Not found: ${filePath}`);
  return null;
}

function appendToFile(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.appendFileSync(filePath, content);
  console.log(`[MemoryLoader] Appended to: ${filePath}`);
}

function loadRecentEvents() {
  const content = readFileIfExists(RECENT_EVENTS_PATH);
  if (content) {
    // Filter to last 24 hours
    const lines = content.split('\n');
    const now = Date.now();
    const oneDayAgo = now - (24 * 60 * 60 * 1000);
    
    const recentLines = lines.filter(line => {
      // Keep lines that look like timestamps or are recent
      const timestampMatch = line.match(/\d{4}-\d{2}-\d{2}/);
      if (timestampMatch) {
        const lineDate = new Date(timestampMatch[0]).getTime();
        return lineDate >= oneDayAgo;
      }
      return true; // Keep non-timestamp lines (continuation)
    });
    
    return recentLines.join('\n');
  }
  return '';
}

function loadDailyMemory(dateStr) {
  const dailyPath = path.join(MEMORY_DIR, `${dateStr}.md`);
  return readFileIfExists(dailyPath) || '';
}

function loadLongTermMemory(isMainSession = true) {
  if (!isMainSession) {
    console.log('[MemoryLoader] Skipping MEMORY.md (not main session)');
    return '';
  }
  return readFileIfExists(MEMORY_MD_PATH) || '';
}

function saveSessionExitEvent(eventName, details = '') {
  const timestamp = new Date().toISOString();
  const dateStr = getTodayStr();
  
  // Append to RECENT_EVENTS.md
  const eventLine = `\n## ${timestamp} - ${eventName}\n${details}\n`;
  appendToFile(RECENT_EVENTS_PATH, eventLine);
  
  // Append to today's daily memory
  const dailyPath = path.join(MEMORY_DIR, `${dateStr}.md`);
  const dailyLine = `\n### ${timestamp}\n${eventName}\n${details}\n`;
  appendToFile(dailyPath, dailyLine);
}

function loadAllMemory(options = {}) {
  const {
    isMainSession = true,
    includeRecent = true,
    includeDaily = true,
    includeLongTerm = true
  } = options;
  
  console.log('\n=== [MemoryLoader] Loading Cross-Session Memory ===\n');
  
  const memory = {
    recent: includeRecent ? loadRecentEvents() : '',
    today: includeDaily ? loadDailyMemory(getTodayStr()) : '',
    yesterday: includeDaily ? loadDailyMemory(getYesterdayStr()) : '',
    longTerm: includeLongTerm ? loadLongTermMemory(isMainSession) : ''
  };
  
  // Generate summary
  console.log('\n=== [MemoryLoader] Memory Summary ===');
  console.log(`Recent Events (24h): ${memory.recent ? memory.recent.split('\n').length : 0} lines`);
  console.log(`Today (${getTodayStr()}): ${memory.today ? memory.today.split('\n').length : 0} lines`);
  console.log(`Yesterday (${getYesterdayStr()}): ${memory.yesterday ? memory.yesterday.split('\n').length : 0} lines`);
  console.log(`Long-term (MEMORY.md): ${memory.longTerm ? memory.longTerm.split('\n').length : 0} lines`);
  console.log('=====================================\n');
  
  return memory;
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const isMainSession = !args.includes('--shared');
  
  const memory = loadAllMemory({ isMainSession });
  
  // Output as JSON for piping
  console.log('\n=== [MemoryLoader] JSON Output ===');
  console.log(JSON.stringify(memory, null, 2));
}

module.exports = {
  loadAllMemory,
  loadRecentEvents,
  loadDailyMemory,
  loadLongTermMemory,
  saveSessionExitEvent,
  getTodayStr,
  getYesterdayStr
};
