/**
 * Domain transfer: DCC transfer-in URLs + legacy secureserver.net form fix.
 */
(function () {
	'use strict';

	var config = window.luciDomainTransfer || {};

	function normalizeDomain(value) {
		var domain = (value || '').trim().toLowerCase();
		domain = domain.replace(/^https?:\/\//, '').replace(/^www\./, '');
		domain = domain.split('/')[0].split('?')[0];
		return domain;
	}

	function buildDccUrl(domain, form) {
		var base =
			(form && form.getAttribute('data-dcc-base')) ||
			config.dccBase ||
			'https://dcc.secureserver.net/domains/transfer-in';
		var plid =
			(form && form.getAttribute('data-plid')) || config.plid || config.progId || '';
		var itc =
			(form && form.getAttribute('data-itc')) || config.itc || 'slp_rstdstore';
		var path = base.replace(/\/$/, '') + '/' + encodeURIComponent(domain) + '/configuration';
		var params = new URLSearchParams();

		if (plid) {
			params.set('plid', String(plid));
			params.set('prog_id', String(plid));
		}
		if (itc) {
			params.set('itc', itc);
		}

		var query = params.toString();
		return query ? path + '?' + query : path;
	}

	function bindLuciForm(form) {
		if (form.dataset.luciTransferBound === '1') {
			return;
		}
		form.dataset.luciTransferBound = '1';

		form.addEventListener('submit', function (event) {
			var input = form.querySelector(
				'input[name="domain"], input[name="domainToCheck"], .luci-domain-transfer-input, .search-field'
			);
			var domain = input && input.value ? normalizeDomain(input.value) : '';
			if (!domain) {
				return;
			}

			event.preventDefault();
			window.open(buildDccUrl(domain, form), '_blank', 'noopener,noreferrer');
		});
	}

	function fixLegacyForm(form) {
		if (form.dataset.luciTransferFixed === '1') {
			return;
		}

		var action = form.getAttribute('action') || '';
		if (action.indexOf('secureserver.net/products/domain-transfer') === -1) {
			return;
		}

		form.dataset.luciTransferFixed = '1';
		form.classList.add('luci-domain-transfer-form');
		bindLuciForm(form);
	}

	document
		.querySelectorAll('.luci-domain-transfer-form, .rstore-domain-transfer form, .widget.rstore-domain-transfer form')
		.forEach(function (form) {
			bindLuciForm(form);
			fixLegacyForm(form);
		});
})();
