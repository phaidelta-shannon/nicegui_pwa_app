self.addEventListener("install", function (e) {
  console.log("Service Worker installed");
});

self.addEventListener("activate", function (e) {
  console.log("Service Worker activated");
});