#!/usr/bin/env node

/**
 * Universal HTTP Retry with Exponential Backoff
 * 
 * Implements EvoMap capsule: sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec
 * 
 * Features:
 * - Exponential backoff retry
 * - AbortController timeout control
 * - Connection pool reuse (via keep-alive)
 * - Handles transient network failures, rate limits (429), connection resets
 * 
 * Expected improvement: ~30% API call success rate increase
 */

const https = require('https');
const http = require('http');

// Connection pool (keep-alive agents)
const httpAgent = new http.Agent({
  keepAlive: true,
  maxSockets: 50,
  maxFreeSockets: 10,
  timeout: 60000,
  freeSocketTimeout: 30000
});

const httpsAgent = new https.Agent({
  keepAlive: true,
  maxSockets: 50,
  maxFreeSockets: 10,
  timeout: 60000,
  freeSocketTimeout: 30000
});

// Retry configuration
const DEFAULT_CONFIG = {
  maxRetries: 5,
  initialDelay: 1000,      // 1 second
  maxDelay: 30000,         // 30 seconds
  timeout: 60000,          // 60 seconds
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
  retryableErrors: [
    'ECONNRESET',
    'ECONNREFUSED',
    'ETIMEDOUT',
    'ENOTFOUND',
    'EAI_AGAIN',
    'TimeoutError'
  ]
};

/**
 * Calculate delay with exponential backoff and jitter
 */
function calculateDelay(attempt, config) {
  const exponentialDelay = config.initialDelay * Math.pow(2, attempt);
  const jitter = Math.random() * 0.3 * exponentialDelay; // 30% jitter
  return Math.min(exponentialDelay + jitter, config.maxDelay);
}

/**
 * Check if error is retryable
 */
function isRetryableError(error) {
  if (!error) return false;
  
  // Check error code
  if (config.retryableErrors.includes(error.code)) {
    return true;
  }
  
  // Check if it's a network error
  const networkErrors = ['network', 'socket', 'timeout', 'abort'];
  const errorMessage = (error.message || '').toLowerCase();
  if (networkErrors.some(err => errorMessage.includes(err))) {
    return true;
  }
  
  return false;
}

/**
 * Check if HTTP status code is retryable
 */
function isRetryableStatus(statusCode) {
  return DEFAULT_CONFIG.retryableStatusCodes.includes(statusCode);
}

/**
 * Parse Retry-After header
 */
function parseRetryAfter(response) {
  const retryAfter = response.headers['retry-after'];
  if (!retryAfter) return null;
  
  // Try to parse as seconds
  const seconds = parseInt(retryAfter, 10);
  if (!isNaN(seconds)) {
    return seconds * 1000;
  }
  
  // Try to parse as HTTP date
  const date = new Date(retryAfter);
  if (!isNaN(date.getTime())) {
    return date.getTime() - Date.now();
  }
  
  return null;
}

/**
 * Universal fetch with retry logic
 */
async function fetchWithRetry(url, options = {}, config = {}) {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const {
    maxRetries,
    timeout,
    ...retryConfig
  } = finalConfig;
  
  let lastError = null;
  let attempt = 0;
  
  while (attempt <= maxRetries) {
    try {
      console.log(`[HTTPRetry] Attempt ${attempt + 1}/${maxRetries + 1}: ${url}`);
      
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      const fetchOptions = {
        ...options,
        signal: controller.signal,
        agent: url.startsWith('https') ? httpsAgent : httpAgent
      };
      
      const response = await fetch(url, fetchOptions);
      clearTimeout(timeoutId);
      
      // Check if we should retry based on status code
      if (isRetryableStatus(response.status)) {
        const retryAfterDelay = parseRetryAfter(response);
        
        if (attempt < maxRetries) {
          const delay = retryAfterDelay || calculateDelay(attempt, retryConfig);
          console.log(`[HTTPRetry] Status ${response.status}, retrying in ${Math.round(delay)}ms`);
          await sleep(delay);
          attempt++;
          continue;
        }
      }
      
      return response;
      
    } catch (error) {
      lastError = error;
      
      // Check if error is retryable
      if (isRetryableError(error) && attempt < maxRetries) {
        const delay = calculateDelay(attempt, retryConfig);
        console.log(`[HTTPRetry] Error: ${error.code || error.message}, retrying in ${Math.round(delay)}ms`);
        await sleep(delay);
        attempt++;
        continue;
      }
      
      // Non-retryable error or max retries reached
      throw error;
    }
  }
  
  throw lastError;
}

/**
 * Sleep helper
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Wrapper for web_search tool
 */
async function webSearchWithRetry(query, options = {}) {
  return fetchWithRetry(
    `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}`,
    {
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': process.env.BRAVE_API_KEY || ''
      }
    },
    options
  );
}

/**
 * Wrapper for web_fetch tool
 */
async function webFetchWithRetry(url, options = {}) {
  return fetchWithRetry(url, options);
}

// CLI usage
if (require.main === module) {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node http-retry.js <url>');
    process.exit(1);
  }
  
  fetchWithRetry(url)
    .then(response => response.text())
    .then(content => console.log(content))
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
}

module.exports = {
  fetchWithRetry,
  webSearchWithRetry,
  webFetchWithRetry,
  httpAgent,
  httpsAgent,
  DEFAULT_CONFIG
};
