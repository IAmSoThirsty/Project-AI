/**
 * Service Worker Registration
 * Registers and manages the service worker lifecycle
 */

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/the_triumvirate/sw.js', {
      scope: '/the_triumvirate/'
    })
    .then((registration) => {
      console.log('✅ ServiceWorker registered successfully:', registration.scope);

      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, 60000); // Check every minute

      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New service worker available
            console.log('🔄 New version available! Refresh to update.');
            
            // Show update notification to user (optional)
            if (confirm('A new version is available! Reload to update?')) {
              newWorker.postMessage({ type: 'SKIP_WAITING' });
              window.location.reload();
            }
          }
        });
      });
    })
    .catch((error) => {
      console.error('❌ ServiceWorker registration failed:', error);
    });

  // Handle controller change (new service worker activated)
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload();
  });
  });
}

// PWA Install Prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  
  // Show install button/banner (customize as needed)
  console.log('💾 Install prompt available');
  
  // You can create a custom install button and show it here
  showInstallPromotion();
});

window.addEventListener('appinstalled', () => {
  console.log('✅ PWA installed successfully');
  deferredPrompt = null;
});

function showInstallPromotion() {
  // Create a subtle install prompt (can be customized)
  const installBanner = document.createElement('div');
  installBanner.id = 'install-banner';
  installBanner.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(135deg, #1E3A8A, #0891B2);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    z-index: 1000;
    display: flex;
    gap: 12px;
    align-items: center;
    animation: slideIn 0.3s ease-out;
    max-width: 90vw;
  `;
  
  installBanner.innerHTML = `
    <span style="flex: 1; font-weight: 500;">Install The Triumvirate app</span>
    <button id="install-btn" style="
      background: rgba(255,255,255,0.2);
      border: 1px solid rgba(255,255,255,0.3);
      color: white;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s;
    ">Install</button>
    <button id="install-dismiss" style="
      background: transparent;
      border: none;
      color: rgba(255,255,255,0.7);
      cursor: pointer;
      font-size: 20px;
      padding: 4px 8px;
    ">&times;</button>
  `;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateY(100px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(installBanner);
  
  // Install button click handler
  document.getElementById('install-btn').addEventListener('click', async () => {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User response to install prompt: ${outcome}`);
    
    deferredPrompt = null;
    installBanner.remove();
  });
  
  // Dismiss button click handler
  document.getElementById('install-dismiss').addEventListener('click', () => {
    installBanner.remove();
  });
}
