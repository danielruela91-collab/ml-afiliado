/* ─── ML Select · Shared JavaScript ─── */

/* Date formatting — updates all date elements on the page */
(function () {
    var now = new Date();
    var months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    var day = now.getDate();
    var month = months[now.getMonth()];
    var year = now.getFullYear();
    var dd = String(day).padStart(2, '0');
    var mm = String(now.getMonth() + 1).padStart(2, '0');

    var heroDate = document.getElementById('hero-date');
    if (heroDate) heroDate.textContent = day + ' ' + month + ' ' + year;

    var shortDate = dd + '/' + mm + '/' + year;
    var els = ['compare-date', 'disclaimer-date', 'ranking-date'];
    els.forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.textContent = shortDate;
    });
})();

/* Sales counter — reads SALES_PER_DAY from window or defaults to 100 */
(function() {
    var SALES_PER_DAY = window.SALES_PER_DAY || 100;
    var MS_PER_SALE = 86400000 / SALES_PER_DAY;
    var now = new Date();
    var startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var msElapsed = now - startOfDay;
    var currentSales = Math.floor(msElapsed / MS_PER_SALE);

    var counterEls = [
        document.getElementById('sales-count'),
        document.getElementById('sales-count-rank')
    ];

    function renderDigits(el, num) {
        if (!el) return;
        el.innerHTML = String(num).split('').map(function(d) {
            return '<span class="flip-digit">' + d + '</span>';
        }).join('');
    }

    function updateDigits(el, oldNum, newNum) {
        if (!el) return;
        var oldStr = String(oldNum), newStr = String(newNum);
        if (oldStr.length !== newStr.length) { renderDigits(el, newNum); return; }
        var digitEls = el.querySelectorAll('.flip-digit');
        for (var i = 0; i < newStr.length; i++) {
            if (newStr[i] !== oldStr[i]) {
                (function(digitEl, newChar) {
                    digitEl.classList.add('flipping');
                    setTimeout(function() { digitEl.textContent = newChar; }, 175);
                    setTimeout(function() { digitEl.classList.remove('flipping'); }, 360);
                })(digitEls[i], newStr[i]);
            }
        }
    }

    counterEls.forEach(function(el) { renderDigits(el, currentSales); });

    function tick() {
        var prev = currentSales;
        currentSales++;
        counterEls.forEach(function(el) { updateDigits(el, prev, currentSales); });
        setTimeout(tick, MS_PER_SALE * (0.7 + Math.random() * 0.6));
    }

    setTimeout(tick, MS_PER_SALE - (msElapsed % MS_PER_SALE));
})();
