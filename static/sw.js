/**
 * Integration Quest - Service Worker
 * Minimal service worker for PWA installation
 */

const CACHE_NAME = 'integration-quest-v1';

// Install event - skip waiting to activate immediately
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

// Activate event - claim all clients
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Fetch event - pass through to network (no offline caching)
self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request));
});
