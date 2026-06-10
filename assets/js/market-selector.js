/**
 * Region / market tray + footer currency (GoDaddy storefront parity).
 */
(function () {
	'use strict';

	var cfg = window.luciMarket || {};

	function setCookie(name, value) {
		var maxAge = cfg.cookieMaxAge || 31536000;
		var parts = [
			name + '=' + encodeURIComponent(value),
			'path=' + (cfg.cookiePath || '/'),
			'max-age=' + maxAge,
			'SameSite=Lax',
		];
		if (cfg.cookieDomain) {
			parts.push('domain=' + cfg.cookieDomain);
		}
		if (cfg.isSecure) {
			parts.push('Secure');
		}
		document.cookie = parts.join('; ');
	}

	function syncGoDaddyPreference(url) {
		var link = document.createElement('link');
		link.rel = 'stylesheet';
		link.href = url;
		document.head.appendChild(link);
	}

	function reloadSoon() {
		window.setTimeout(function () {
			window.location.reload();
		}, 350);
	}

	var coarsePointer = window.matchMedia('(pointer: coarse)').matches;
	var fineHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
	var lastTouchToggleAt = 0;

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

	/* Market tray */
	var marketRoot = document.querySelector('.luci-market-selector');
	if (marketRoot && cfg.marketCookie) {
		var trigger = marketRoot.querySelector('.luci-market-selector__trigger');
		var panel = marketRoot.querySelector('.luci-market-selector__panel');
		var closeBtn = marketRoot.querySelector('.luci-market-close');
		var suppressDocumentCloseUntil = 0;

		function suppressDocumentClose() {
			suppressDocumentCloseUntil = Date.now() + 650;
		}

		function shouldIgnoreDocumentClose() {
			return Date.now() < suppressDocumentCloseUntil;
		}

		function closePanel() {
			if (!panel || !trigger) {
				return;
			}
			panel.hidden = true;
			marketRoot.classList.remove('open');
			trigger.setAttribute('aria-expanded', 'false');
		}

		function openPanel() {
			if (!panel || !trigger) {
				return;
			}
			panel.hidden = false;
			marketRoot.classList.add('open');
			trigger.setAttribute('aria-expanded', 'true');
		}

		if (trigger && panel) {
			bindTap(trigger, function (event) {
				event.preventDefault();
				event.stopPropagation();
				suppressDocumentClose();
				if (panel.hidden) {
					openPanel();
				} else {
					closePanel();
				}
			});

			if (closeBtn) {
				bindTap(closeBtn, function (event) {
					event.preventDefault();
					suppressDocumentClose();
					closePanel();
				});
			}

			if (fineHover && !coarsePointer) {
				document.addEventListener('click', function (event) {
					if (shouldIgnoreDocumentClose()) {
						return;
					}
					if (!marketRoot.contains(event.target)) {
						closePanel();
					}
				});
			}

			document.addEventListener('keydown', function (event) {
				if (event.key === 'Escape') {
					closePanel();
				}
			});
		}

		marketRoot.querySelectorAll('.luci-market-selector__option').forEach(function (btn) {
			btn.addEventListener('click', function () {
				var market = btn.getAttribute('data-market');
				var currency = btn.getAttribute('data-currency');
				var url = btn.getAttribute('data-preference-url');
				if (!market || !url) {
					return;
				}
				setCookie(cfg.marketCookie, market);
				if (cfg.currencyCookie && currency) {
					setCookie(cfg.currencyCookie, currency);
				}
				syncGoDaddyPreference(url);
				reloadSoon();
			});
		});
	}

	/* Footer currency */
	var currencySelect = document.getElementById('luci-currency-select');
	if (currencySelect && cfg.currencyCookie) {
		currencySelect.addEventListener('change', function () {
			setCookie(cfg.currencyCookie, currencySelect.value);
			reloadSoon();
		});
	}
})();
