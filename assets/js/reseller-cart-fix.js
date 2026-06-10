/**
 * Ensure GoDaddy Reseller Store add-to-cart buttons use the plugin AJAX flow.
 *
 * Auto-appended forms use a submit button without data-id, so store.js does not
 * intercept the click and the header cart count never updates.
 */
(function ($) {
	'use strict';

	function productIdFromForm($form) {
		if (typeof rstore !== 'undefined' && rstore.product && rstore.product.id) {
			return rstore.product.id;
		}

		var raw = $form.find('input[name="items"]').val();
		if (!raw) {
			return null;
		}

		try {
			var items = JSON.parse(raw);
			if (items && items[0] && items[0].id) {
				return items[0].id;
			}
		} catch (err) {
			return null;
		}

		return null;
	}

	function enhanceAddToCartButtons() {
		$('.rstore-add-to-cart-form .rstore-add-to-cart').each(function () {
			var $button = $(this);

			if ($button.attr('data-id')) {
				return;
			}

			var $form = $button.closest('.rstore-add-to-cart-form');
			var productId = productIdFromForm($form);

			if (!productId) {
				return;
			}

			$button.attr('data-id', productId);
			if (!$button.attr('data-quantity')) {
				$button.attr('data-quantity', '1');
			}
		});
	}

	$(document).ready(function () {
		enhanceAddToCartButtons();
	});

	// Domain search / dynamic widgets may inject forms after load.
	if (typeof MutationObserver !== 'undefined') {
		var observer = new MutationObserver(function () {
			enhanceAddToCartButtons();
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}
}(jQuery));
