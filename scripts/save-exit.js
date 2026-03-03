#!/usr/bin/env node

/**
 * Session Exit Hook - Auto-save significant events
 * 
 * Implements EvoMap capsule memory continuity
 * 
 * Usage:
 * - Call at the end of each session to save significant events
 * - Automatically appends to RECENT_EVENTS.md and daily memory
 */

const { saveSessionExitEvent, loadAllMemory } = require('./load-memory');

// Register exit hooks
process.on('exit', () => {
  console.log('[ExitHook] Session ending, saving state...');
  // Note: Can't do async operations in exit handler
  // For async, use beforeExit or explicit calls
});

process.on('beforeExit', (code) => {
  console.log(`[ExitHook] Before exit with code ${code}`);
  // Can do async operations here if needed
});

// Graceful shutdown handlers
process.on('SIGINT', () => {
  console.log('\n[ExitHook] SIGINT received, saving state...');
  saveSessionExitEvent('Session Interrupted', 'User pressed Ctrl+C');
  process.exit(130);
});

process.on('SIGTERM', () => {
  console.log('\n[ExitHook] SIGTERM received, saving state...');
  saveSessionExitEvent('Session Terminated', 'Received SIGTERM signal');
  process.exit(143);
});

// Export for programmatic use
module.exports = {
  saveSessionExitEvent,
  loadAllMemory
};

console.log('[ExitHook] Registered exit handlers');
