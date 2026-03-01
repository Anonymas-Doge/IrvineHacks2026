// Panoramic background manager.
// Image: images/down_pano.jpg
// background-size is set so the image is (100% / 0.55) tall — meaning the viewport
// shows exactly 55% of the image at a time (10% overlap between pages).
//   index    (page 0) → background-position-y: 0%   = top    55% of image
//   recipes  (page 1) → background-position-y: 100% = bottom 55% of image
//   all other pages stay at 100%
(function () {
  var DURATION = 600;
  var PAGE_Y = ['0%', '100%', '100%', '100%', '100%'];
  var _page = 0;

  function getEl() {
    return document.getElementById('bgPanorama');
  }

  // Snap to page position instantly (no animation).
  function snapTo(pageIndex) {
    var el = getEl();
    if (!el) return;
    _page = pageIndex;
    el.style.transition = 'none';
    el.getBoundingClientRect(); // force layout flush so 'none' takes effect
    el.style.backgroundPositionY = PAGE_Y[pageIndex] || '100%';
  }

  // Animate to page position. Returns a Promise that resolves when done.
  // Uses ease-in-out for a smooth cinematic pan feel.
  function panTo(pageIndex) {
    return new Promise(function (resolve) {
      var el = getEl();
      if (!el) { resolve(); return; }
      el.style.transition = 'background-position-y ' + DURATION + 'ms ease-in-out';
      el.style.backgroundPositionY = PAGE_Y[pageIndex] || '100%';
      setTimeout(resolve, DURATION);
    });
  }

  window.Panorama = { initPage: snapTo, panTo: panTo };
}());
