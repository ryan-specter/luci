/**
 * Legacy Hydra tray buttons opened empty panels — navigate to hub pages instead.
 */
(function () {
	'use strict';

	var hubs = (window.luciNavHubs && window.luciNavHubs.hubs) || {};

	function hubUrl(trayId) {
		if (hubs[trayId]) {
			return hubs[trayId];
		}
		return '/' + trayId.replace(/^\/+|\/+$/g, '') + '/';
	}

	document.querySelectorAll('.luci-product-tray .tray-toggle[data-luci-tray]').forEach(function (btn) {
		if (btn.tagName !== 'BUTTON') {
			return;
		}
		var trayId = btn.getAttribute('data-luci-tray');
		if (!trayId) {
			return;
		}
		btn.addEventListener('click', function (event) {
			event.preventDefault();
			event.stopPropagation();
			window.location.href = hubUrl(trayId);
		});
	});

	/* Home wrapped in tray-menu — ensure link works */
	document.querySelectorAll('.topnav-item#home .tray-toggle.topnav-nontray-btn').forEach(function (link) {
		link.addEventListener('click', function (event) {
			event.stopPropagation();
		});
	});
})();
