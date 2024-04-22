const CONFIG = {
  ENABLE_CACHE: true,
  HOSTNAME_WHITELIST: [
    // self.location.hostname,
    "pygame-web.github.io",
  ]
}


// The Util Function to hack URLs of intercepted requests
const getFixedUrl = (req) => {
  var now = Date.now();
  var url = new URL(req.url);

  // 1. fixed http URL
  // Just keep syncing with location.protocol
  // fetch(httpURL) belongs to active mixed content.
  // And fetch(httpRequest) is not supported yet.
  url.protocol = self.location.protocol;

  // 2. add query for caching-busting.
  // Github Pages served with Cache-Control: max-age=600
  // max-age on mutable content is error-prone, with SW life of bugs can even extend.
  // Until cache mode of Fetch API landed, we have to workaround cache-busting with query string.
  // Cache-Control-Bug: https://bugs.chromium.org/p/chromium/issues/detail?id=453190
  if (url.hostname === self.location.hostname) {
    url.search += (url.search ? "&" : "?") + "cache-bust=" + now;
  }
  console.log("[SW] getFixedUrl(): " + req.url + " => " + url.href);
  return url.href;
};

/**
 *  @Lifecycle Activate
 *  New one activated when old isnt being used.
 *
 *  waitUntil(): activating ====> activated
 */
self.addEventListener("activate", (event) => {
  console.log("[SW] activate");
  event.waitUntil(self.clients.claim());

  console.log(`[SW] Caching ${CONFIG.ENABLE_CACHE ? 'enabled' : 'disabled'}`)
  if (CONFIG.ENABLE_CACHE) {
    console.log('[SW] attempting to cache main.wasm')
    caches.open("pwa-cache").then((cache) => {
      cache.addAll([
        'https://pygame-web.github.io/archives/0.9/cpython312/main.data'
      ]);
    })
  }
});

/**
 *  @Functional Fetch
 *  All network requests are being intercepted here.
 *
 *  void respondWith(Promise<Response> r)
 */
self.addEventListener("fetch", (event) => {
  if (!CONFIG.ENABLE_CACHE) return;
  console.log("[SW] fetch " + event.request.url);
  // Skip some of cross-origin requests, like those for Google Analytics.
  if (CONFIG.HOSTNAME_WHITELIST.indexOf(new URL(event.request.url).hostname) > -1) {
    console.log("[SW] whitelisted");
    // Stale-while-revalidate
    // similar to HTTP's stale-while-revalidate: https://www.mnot.net/blog/2007/12/12/stale
    // Upgrade from Jake's to Surma's: https://gist.github.com/surma/eb441223daaedf880801ad80006389f1
    const cached = caches.match(event.request);
    const fixedUrl = getFixedUrl(event.request);
    const fetched = fetch(fixedUrl, { cache: "no-store" });
    const fetchedCopy = fetched.then((resp) => resp.clone());

    // Call respondWith() with whatever we get first.
    // If the fetch fails (e.g disconnected), wait for the cache.
    // If there’s nothing in cache, wait for the fetch.
    // If neither yields a response, return offline pages.
    event.respondWith(
      Promise.race([fetched.catch((_) => cached), cached])
        .then((resp) => {
          if (resp) {
            console.log("[SW] returning cached response: ", resp);
            return resp;
          } else if (fetched) {
            console.log("[SW] returning fetched response: ", fetched);
            return fetched;
          }
        })
        .catch((_) => {
          console.error("[SW] fetch error: ", _);
        }),
    );

    // Update the cache with the version we fetched (only for ok status)
    event.waitUntil(
      Promise.all([fetchedCopy, caches.open("pwa-cache")])
        .then(([response, cache]) => {
          if (response.ok) {
            console.groupCollapsed("[SW] fetch response ok");
            console.log("[SW] updating cache: ", fixedUrl);
            console.log("[SW] response: ", response);
            console.log("[SW] cache: ", cache);
            console.log("[SW] event.request: ", event.request);
            console.groupEnd();
            try {
              cache.put(event.request, response);
            } catch (error) {
              console.error("[SW] cache.put error: ", error);
            }
          }
        })
        .catch((_) => {
          console.error("[SW] fetch error: ", _);
        }),
    );
  }
});
