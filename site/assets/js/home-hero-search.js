/**
 * Homepage domain search — submit to secureserver.net find URL.
 */
(function () {
	'use strict';

	var config = window.luciHomeHero || {};

	function normalizeDomain(value) {
		var domain = (value || '').trim().toLowerCase();
		domain = domain.replace(/^https?:\/\//, '').replace(/^www\./, '');
		domain = domain.split('/')[0].split('?')[0];
		return domain;
	}

	function buildUrl(domain) {
		var base = config.searchBase || '';
		if (!base) {
			return '';
		}
		if (!domain) {
			return base;
		}
		var sep = base.indexOf('?') === -1 ? '?' : '&';
		return base + sep + 'domainToCheck=' + encodeURIComponent(domain);
	}

	document.querySelectorAll('.luci-home-hero__search, .luci-meet-domain-search').forEach(function (form) {
		form.addEventListener('submit', function (event) {
			var input = form.querySelector('input[name="domainToCheck"]');
			var domain = input && input.value ? normalizeDomain(input.value) : '';
			var url = buildUrl(domain);
			if (!url) {
				return;
			}
			event.preventDefault();
			window.location.href = url;
		});
	});
})();
