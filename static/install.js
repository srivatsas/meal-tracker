let deferredPrompt;
const installBtn = document.getElementById("install-btn");
const iosBanner = document.getElementById("ios-banner");

// Detect Android and listen for install event
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (installBtn) installBtn.style.display = "block";
});

if (installBtn) {
  installBtn.addEventListener("click", () => {
    installBtn.style.display = "none";
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === "accepted") {
        console.log("User accepted install");
      } else {
        console.log("User dismissed install");
      }
      deferredPrompt = null;
    });
  });
}

// Detect iOS Safari
function isIos() {
  return /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
}
function isInStandaloneMode() {
  return ('standalone' in window.navigator) && window.navigator.standalone;
}
if (isIos() && !isInStandaloneMode()) {
  if (iosBanner) iosBanner.style.display = "block";
}
