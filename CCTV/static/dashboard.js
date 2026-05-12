let allAlerts = [];
let currentFilter = 'ALL';
let dashboardStarted = false;

function goToDashboard() {
    var landing = document.getElementById('landing-page');
    var dashboard = document.getElementById('dashboard-page');
    landing.style.opacity = '0';
    landing.style.transition = 'opacity 0.4s';
    setTimeout(function() {
        landing.style.display = 'none';
        dashboard.style.display = 'block';
        if (!dashboardStarted) {
            dashboardStarted = true;
            fetchRules();
            fetchAlerts();
            fetchStats();
            setInterval(fetchAlerts, 3000);
            setInterval(fetchStats, 3000);
        }
    }, 400);
}

function goToLanding() {
    document.getElementById('dashboard-page').style.display = 'none';
    var landing = document.getElementById('landing-page');
    landing.style.display = 'flex';
    landing.style.opacity = '1';
}

function openStream() {
    window.open('/video_feed', '_blank');
}

function filterAlerts(filter, event) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(function(b) {
        b.classList.remove('active');
    });
    if (event && event.target) event.target.classList.add('active');
    renderAlerts();
}

function renderAlerts() {
    var container = document.getElementById('alerts-container');
    var filtered = allAlerts;
    if (currentFilter !== 'ALL') {
        filtered = allAlerts.filter(function(a) {
            return a.severity === currentFilter || a.source === currentFilter;
        });
    }
    container.innerHTML = filtered.map(function(a) {
        return '<div class="alert-item ' + a.severity + '">' +
            '<div class="alert-header">' +
            '<div style="display:flex;gap:6px;align-items:center;">' +
            '<span class="alert-source">' + a.source + '</span>' +
            '<span class="severity-badge ' + a.severity + '">' + a.severity + '</span>' +
            '</div>' +
            '<span class="alert-time">' + new Date(a.timestamp).toLocaleTimeString() + '</span>' +
            '</div>' +
            '<div class="alert-msg">' + a.message + '</div>' +
            '<div class="alert-ips">' + a.src_ip + ' &rarr; ' + a.dst_ip + '</div>' +
            '</div>';
    }).join('');
}

function fetchAlerts() {
    fetch('/api/alerts')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            allAlerts = data;
            document.getElementById('alert-count').textContent = data.length + ' events';
            renderAlerts();
        });
}

function fetchStats() {
    fetch('/api/stats')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            document.getElementById('stat-total').textContent = data.total;
            document.getElementById('stat-high').textContent = data.high;
            document.getElementById('stat-medium').textContent = data.medium;
            document.getElementById('stat-low').textContent = data.low;
        });
}

function fetchRules() {
    fetch('/api/rules')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var container = document.getElementById('rules-container');
            container.innerHTML = data.map(function(r) {
                return '<div class="rule-row">' +
                    '<span class="rule-ips">' + r.src_ip + ' &rarr; ' + r.dst_ip + '</span>' +
                    '<span class="rule-action">' + r.action + '</span>' +
                    '</div>';
            }).join('');
        });
}
