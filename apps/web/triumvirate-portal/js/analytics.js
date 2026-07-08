/**
 * Analytics and Monitoring Setup
 * Provides tracking, error logging, and performance monitoring
 */

// Configuration
const config = {
  // Google Analytics 4
  ga4: {
    measurementId: 'G-XXXXXXXXXX', // Replace with your GA4 Measurement ID
    enabled: false // Set to true when you have a GA4 ID
  },
  
  // Performance monitoring
  performance: {
    enabled: true,
    sampleRate: 1.0 // 100% sampling
  },
  
  // Error tracking
  errorTracking: {
    enabled: true,
    sampleRate: 1.0
  }
};

// Initialize Google Analytics 4
function initializeGA4() {
  if (!config.ga4.enabled || !config.ga4.measurementId) {
    console.log('📊 Analytics: Disabled (no measurement ID configured)');
    return;
  }

  // Load gtag script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${config.ga4.measurementId}`;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  window.gtag = gtag;
  
  gtag('js', new Date());
  gtag('config', config.ga4.measurementId, {
    send_page_view: true,
    anonymize_ip: true // Privacy-friendly
  });

  console.log('✅ Google Analytics 4 initialized');
}

// Track custom events
function trackEvent(eventName, eventParams = {}) {
  if (typeof gtag !== 'undefined') {
    gtag('event', eventName, eventParams);
  }
  
  // Also log to console in development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('📊 Event:', eventName, eventParams);
  }
}

// Track page views (for SPAs)
function trackPageView(path, title) {
  if (typeof gtag !== 'undefined') {
    gtag('config', config.ga4.measurementId, {
      page_path: path,
      page_title: title
    });
  }
}

// Performance monitoring
function initializePerformanceMonitoring() {
  if (!config.performance.enabled) return;

  // Web Vitals tracking
  if ('PerformanceObserver' in window) {
    // Largest Contentful Paint (LCP)
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        
        trackEvent('web_vitals', {
          metric_name: 'LCP',
          value: Math.round(lastEntry.renderTime || lastEntry.loadTime),
          metric_rating: lastEntry.renderTime < 2500 ? 'good' : lastEntry.renderTime < 4000 ? 'needs-improvement' : 'poor'
        });
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      console.warn('LCP observer not supported');
    }

    // First Input Delay (FID)
    try {
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const delay = entry.processingStart - entry.startTime;
          trackEvent('web_vitals', {
            metric_name: 'FID',
            value: Math.round(delay),
            metric_rating: delay < 100 ? 'good' : delay < 300 ? 'needs-improvement' : 'poor'
          });
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
    } catch (e) {
      console.warn('FID observer not supported');
    }

    // Cumulative Layout Shift (CLS)
    try {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });

      // Report CLS on page unload
      window.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
          trackEvent('web_vitals', {
            metric_name: 'CLS',
            value: Math.round(clsValue * 1000) / 1000,
            metric_rating: clsValue < 0.1 ? 'good' : clsValue < 0.25 ? 'needs-improvement' : 'poor'
          });
        }
      });
    } catch (e) {
      console.warn('CLS observer not supported');
    }
  }

  // Navigation Timing API
  window.addEventListener('load', () => {
    setTimeout(() => {
      const perfData = window.performance.timing;
      const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
      const connectTime = perfData.responseEnd - perfData.requestStart;
      const renderTime = perfData.domComplete - perfData.domLoading;

      trackEvent('performance', {
        page_load_time: pageLoadTime,
        connection_time: connectTime,
        render_time: renderTime
      });

      console.log('⚡ Performance:', {
        pageLoad: `${pageLoadTime}ms`,
        connection: `${connectTime}ms`,
        render: `${renderTime}ms`
      });
    }, 0);
  });
}

// Error tracking
function initializeErrorTracking() {
  if (!config.errorTracking.enabled) return;

  // Global error handler
  window.addEventListener('error', (event) => {
    if (Math.random() > config.errorTracking.sampleRate) return;

    trackEvent('exception', {
      description: `${event.message} at ${event.filename}:${event.lineno}:${event.colno}`,
      fatal: false,
      error_type: 'javascript_error'
    });

    console.error('❌ JavaScript Error:', event.message);
  });

  // Unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    if (Math.random() > config.errorTracking.sampleRate) return;

    trackEvent('exception', {
      description: `Unhandled Promise Rejection: ${event.reason}`,
      fatal: false,
      error_type: 'promise_rejection'
    });

    console.error('❌ Unhandled Rejection:', event.reason);
  });
}

// Track user interactions
function initializeInteractionTracking() {
  // Track external links
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (link && link.hostname !== window.location.hostname) {
      trackEvent('outbound_link', {
        link_url: link.href,
        link_domain: link.hostname
      });
    }
  });

  // Track file downloads
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (link && link.href.match(/\.(pdf|zip|doc|docx|xls|xlsx|ppt|pptx)$/i)) {
      trackEvent('file_download', {
        file_url: link.href,
        file_name: link.href.split('/').pop()
      });
    }
  });

  // Track scroll depth
  let maxScroll = 0;
  const scrollThresholds = [25, 50, 75, 90, 100];
  const trackedThresholds = new Set();

  window.addEventListener('scroll', () => {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (window.scrollY / scrollHeight) * 100;

    if (scrollPercent > maxScroll) {
      maxScroll = scrollPercent;
    }

    scrollThresholds.forEach(threshold => {
      if (scrollPercent >= threshold && !trackedThresholds.has(threshold)) {
        trackedThresholds.add(threshold);
        trackEvent('scroll_depth', {
          percent: threshold
        });
      }
    });
  });
}

// Initialize all tracking
function initializeAnalytics() {
  console.log('📊 Initializing analytics and monitoring...');
  
  initializeGA4();
  initializePerformanceMonitoring();
  initializeErrorTracking();
  initializeInteractionTracking();
  
  console.log('✅ Analytics and monitoring initialized');
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAnalytics);
} else {
  initializeAnalytics();
}

// Export for manual use
window.triumvirateAnalytics = {
  trackEvent,
  trackPageView,
  config
};
