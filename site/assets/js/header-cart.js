/**
 * Sync Luci header cart badge with hidden GoDaddy Reseller Store cart widget.
 */
(function ($) {
	'use strict';

	var cartTray = document.getElementById('luci-cart-tray');
	if (!cartTray) {
		return;
	}

	var badge = cartTray.querySelector('.luci-cart-badge');
	var emptyMsg = cartTray.querySelector('.luci-cart-empty');
	var hasItemsMsg = cartTray.querySelector('.luci-cart-has-items');
	var host = cartTray.querySelector('.luci-rstore-cart-host');

	function parseCount(text) {
		if (!text) {
			return 0;
		}
		var match = String(text).match(/\d+/);
		return match ? parseInt(match[0], 10) : 0;
	}

	function countFromHost() {
		if (!host) {
			return 0;
		}

		var selectors = [
			'[data-cart-count]',
			'.cart-count',
			'.rstore-cart-count',
			'.rstore-cart-button .count',
			'.rstore-cart .count',
			'span.count',
		];

		var i;
		for (i = 0; i < selectors.length; i++) {
			var el = host.querySelector(selectors[i]);
			if (el) {
				var attr = el.getAttribute('data-cart-count');
				var n = parseCount(attr || el.textContent);
				if (n > 0) {
					return n;
				}
			}
		}

		var button = host.querySelector('.rstore-cart-button, .rstore-cart a, a[href*="cart.secureserver"]');
		if (button) {
			return parseCount(button.textContent);
		}

		return 0;
	}

	function updateBadge(count) {
		if (!badge) {
			return;
		}
		badge.textContent = String(count);
		badge.setAttribute('data-count', String(count));
		if (count > 0) {
			badge.hidden = false;
		} else {
			badge.hidden = true;
		}

		if (emptyMsg) {
			emptyMsg.hidden = count > 0;
		}
		if (hasItemsMsg) {
			hasItemsMsg.hidden = count <= 0;
		}
	}

	function countFromApi(callback) {
		if (typeof rstore === 'undefined' || !rstore.urls || !rstore.urls.cart_api) {
			callback(0);
			return;
		}

		fetch(rstore.urls.cart_api, { credentials: 'include', mode: 'cors' })
			.then(function (response) {
				if (!response.ok) {
					throw new Error('cart_api');
				}
				return response.json();
			})
			.then(function (data) {
				var count = 0;
				if (data && Array.isArray(data.items)) {
					count = data.items.length;
				} else if (data && typeof data.count === 'number') {
					count = data.count;
				} else if (data && data.cart && Array.isArray(data.cart.items)) {
					count = data.cart.items.length;
				}
				callback(count);
			})
			.catch(function () {
				callback(0);
			});
	}

	function sync() {
		var hostCount = countFromHost();
		if (hostCount > 0) {
			updateBadge(hostCount);
			return;
		}
		countFromApi(updateBadge);
	}

	$(document).ready(sync);

	if (host && typeof MutationObserver !== 'undefined') {
		var observer = new MutationObserver(function () {
			sync();
		});
		observer.observe(host, { childList: true, subtree: true, characterData: true });
	}

	$(document.body).on('rstore_cart_updated rstore_added_to_cart', sync);
}(jQuery));
