/**
 * Header nav — hamburger overlay + click-to-expand submenus (no hover toggle).
 */
(function () {
	'use strict';

	document.documentElement.classList.add('luci-nav-click-only');

	var nav = document.getElementById('luci-topnav-items');
	var topnavToggle = document.querySelector('.luci-topnav-toggle');
	var headerShell = document.getElementById('luci-hcs-header') || document.querySelector('.luci-header-shell');
	var openDropdown = null;
	var suppressDocumentCloseUntil = 0;
	var mobileNavMq = window.matchMedia('(max-width: 991px)');

	var backdrop = document.createElement('button');
	backdrop.type = 'button';
	backdrop.className = 'luci-mobile-nav-backdrop';
	backdrop.setAttribute('hidden', '');
	backdrop.setAttribute('aria-label', 'Close menu');
	document.body.appendChild(backdrop);

	function suppressDocumentClose() {
		suppressDocumentCloseUntil = Date.now() + 400;
	}

	function shouldIgnoreDocumentClose() {
		return Date.now() < suppressDocumentCloseUntil;
	}

	function isMobileNav() {
		return mobileNavMq.matches;
	}

	function syncMobileNavTop() {
		if (!headerShell) {
			return;
		}
		var rect = headerShell.getBoundingClientRect();
		document.documentElement.style.setProperty(
			'--luci-mobile-nav-top',
			Math.max(0, Math.round(rect.bottom)) + 'px'
		);
	}

	function setBackdropVisible(visible) {
		if (visible && isMobileNav()) {
			backdrop.removeAttribute('hidden');
		} else {
			backdrop.setAttribute('hidden', '');
		}
	}

	function setMobileNavOpen(open) {
		if (!topnavToggle || !nav) {
			return;
		}

		if (open && isMobileNav()) {
			syncMobileNavTop();
		}

		nav.classList.toggle('is-open', open);
		topnavToggle.classList.toggle('is-active', open);
		topnavToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
		topnavToggle.setAttribute(
			'aria-label',
			open
				? topnavToggle.getAttribute('data-label-close') || 'Close products menu'
				: topnavToggle.getAttribute('data-label-open') || 'Open products menu'
		);
		document.body.classList.toggle('luci-mobile-nav-open', open && isMobileNav());
		setBackdropVisible(open);

		if (!open) {
			closeAllDropdowns();
		}
	}

	if (topnavToggle && nav) {
		topnavToggle.setAttribute(
			'data-label-open',
			topnavToggle.getAttribute('aria-label') || 'Open products menu'
		);
		topnavToggle.setAttribute('data-label-close', 'Close products menu');

		topnavToggle.addEventListener('click', function (event) {
			event.preventDefault();
			event.stopPropagation();
			suppressDocumentClose();
			setMobileNavOpen(!nav.classList.contains('is-open'));
		});
	}

	backdrop.addEventListener('click', function (event) {
		event.preventDefault();
		suppressDocumentClose();
		setMobileNavOpen(false);
	});

	if (!nav) {
		return;
	}

	var dropdowns = nav.querySelectorAll('.luci-nav-dropdown');

	function setPanelOpen(panel, open) {
		if (!panel) {
			return;
		}
		if (open) {
			panel.removeAttribute('hidden');
			panel.classList.add('is-visible');
			panel.setAttribute('aria-hidden', 'false');
		} else {
			panel.setAttribute('hidden', '');
			panel.classList.remove('is-visible');
			panel.setAttribute('aria-hidden', 'true');
		}
	}

	function closeDropdown(menu) {
		if (!menu) {
			return;
		}
		var panel = menu.querySelector('.luci-nav-dropdown__panel');
		var trigger = menu.querySelector('.luci-nav-dropdown__trigger');
		setPanelOpen(panel, false);
		menu.classList.remove('is-open');
		if (trigger) {
			trigger.setAttribute('aria-expanded', 'false');
		}
		if (openDropdown === menu) {
			openDropdown = null;
		}
	}

	function closeAllDropdowns() {
		dropdowns.forEach(function (menu) {
			closeDropdown(menu);
		});
	}

	function openDropdownMenu(menu) {
		if (openDropdown && openDropdown !== menu) {
			closeDropdown(openDropdown);
		}
		var panel = menu.querySelector('.luci-nav-dropdown__panel');
		var trigger = menu.querySelector('.luci-nav-dropdown__trigger');
		if (!panel || !trigger) {
			return;
		}
		setPanelOpen(panel, true);
		menu.classList.add('is-open');
		trigger.setAttribute('aria-expanded', 'true');
		openDropdown = menu;
	}

	function toggleDropdown(menu, event) {
		event.preventDefault();
		event.stopPropagation();
		suppressDocumentClose();

		if (isMobileNav() && !nav.classList.contains('is-open')) {
			setMobileNavOpen(true);
		}

		if (menu.classList.contains('is-open')) {
			closeDropdown(menu);
		} else {
			openDropdownMenu(menu);
		}
	}

	dropdowns.forEach(function (menu) {
		var trigger = menu.querySelector('.luci-nav-dropdown__trigger');
		if (!trigger) {
			return;
		}

		trigger.addEventListener('click', function (event) {
			toggleDropdown(menu, event);
		});

		trigger.addEventListener('keydown', function (event) {
			if (event.key === 'Enter' || event.key === ' ') {
				toggleDropdown(menu, event);
			}
		});

		/* Narrow viewport + mouse: block hover from fighting click state */
		menu.addEventListener(
			'mouseenter',
			function (event) {
				if (!isMobileNav()) {
					return;
				}
				event.stopPropagation();
			},
			true
		);
	});

	document.addEventListener('click', function (event) {
		if (shouldIgnoreDocumentClose()) {
			return;
		}
		if (nav.contains(event.target)) {
			return;
		}
		if (openDropdown) {
			closeDropdown(openDropdown);
		}
		if (nav.classList.contains('is-open') && topnavToggle && !topnavToggle.contains(event.target)) {
			setMobileNavOpen(false);
		}
	});

	document.addEventListener('keydown', function (event) {
		if (event.key === 'Escape') {
			if (openDropdown) {
				closeDropdown(openDropdown);
			}
			if (nav.classList.contains('is-open') && topnavToggle) {
				setMobileNavOpen(false);
			}
		}
	});

	function onMobileMqChange() {
		document.documentElement.classList.toggle('luci-nav-mobile', isMobileNav());
		if (!isMobileNav()) {
			setMobileNavOpen(false);
			setBackdropVisible(false);
		}
	}

	onMobileMqChange();
	if (mobileNavMq.addEventListener) {
		mobileNavMq.addEventListener('change', onMobileMqChange);
	} else if (mobileNavMq.addListener) {
		mobileNavMq.addListener(onMobileMqChange);
	}

	window.addEventListener('resize', function () {
		if (document.body.classList.contains('luci-mobile-nav-open')) {
			syncMobileNavTop();
		}
	});
})();
