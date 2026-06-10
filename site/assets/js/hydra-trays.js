/**
 * Hydra-style utility trays (Sign In) — touch-safe toggles.
 */
(function () {
	'use strict';

	var header = document.getElementById('luci-hcs-header');
	if (!header) {
		return;
	}

	var activeTray = null;
	var suppressDocumentCloseUntil = 0;
	var lastTouchToggleAt = 0;
	var coarsePointer = window.matchMedia('(pointer: coarse)').matches;
	var fineHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

	function suppressDocumentClose() {
		suppressDocumentCloseUntil = Date.now() + 650;
	}

	function shouldIgnoreDocumentClose() {
		return Date.now() < suppressDocumentCloseUntil;
	}

	function bindTap(el, handler) {
		if (!el) {
			return;
		}

		function onActivate(event) {
			if (event.type === 'touchend') {
				lastTouchToggleAt = Date.now();
			} else if (Date.now() - lastTouchToggleAt < 500) {
				return;
			}
			handler(event);
		}

		el.addEventListener('touchend', onActivate, { passive: false });
		el.addEventListener('click', onActivate);
	}

	function initTray(root, toggleSelector) {
		var panel = root.querySelector('.tray-dropdown');
		var toggle = root.querySelector(toggleSelector || '.tray-toggle');

		if (!panel || !toggle) {
			return;
		}

		function closeTray() {
			panel.hidden = true;
			root.classList.remove('is-open');
			toggle.setAttribute('aria-expanded', 'false');
			if (activeTray === root) {
				activeTray = null;
			}
		}

		function openTray() {
			if (activeTray && activeTray !== root) {
				var otherPanel = activeTray.querySelector('.tray-dropdown');
				var otherToggle = activeTray.querySelector('.tray-toggle');
				if (otherPanel) {
					otherPanel.hidden = true;
				}
				activeTray.classList.remove('is-open');
				if (otherToggle) {
					otherToggle.setAttribute('aria-expanded', 'false');
				}
			}

			panel.hidden = false;
			root.classList.add('is-open');
			toggle.setAttribute('aria-expanded', 'true');
			activeTray = root;
		}

		bindTap(toggle, function (event) {
			event.preventDefault();
			event.stopPropagation();
			suppressDocumentClose();
			if (activeTray === root) {
				closeTray();
			} else {
				openTray();
			}
		});

		root.querySelectorAll('.tray-close').forEach(function (btn) {
			bindTap(btn, function (event) {
				event.preventDefault();
				suppressDocumentClose();
				closeTray();
			});
		});

		if (fineHover && !coarsePointer) {
			document.addEventListener('click', function (event) {
				if (shouldIgnoreDocumentClose()) {
					return;
				}
				if (activeTray === root && !root.contains(event.target)) {
					closeTray();
				}
			});
		}

		document.addEventListener('keydown', function (event) {
			if (event.key === 'Escape' && activeTray === root) {
				closeTray();
			}
		});
	}

	var accountTray = header.querySelector('.luci-account-tray, .account-tray');
	if (accountTray) {
		initTray(accountTray);
	}
})();
