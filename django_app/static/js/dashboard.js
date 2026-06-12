(function () {
  function readJSON(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    try {
      return JSON.parse(el.textContent || 'null') || fallback;
    } catch (e) {
      return fallback;
    }
  }

  var distribution = readJSON('dist-data', { High: 0, Average: 0, 'At-Risk': 0 });
  var trend = readJSON('trend-data', []);
  var importance = readJSON('importance-data', []);

  // Chart 1 - Doughnut: performance distribution
  var distCtx = document.getElementById('distributionChart');
  if (distCtx) {
    new Chart(distCtx, {
      type: 'doughnut',
      data: {
        labels: ['High', 'Average', 'At-Risk'],
        datasets: [{
          data: [distribution.High, distribution.Average, distribution['At-Risk']],
          backgroundColor: ['#16A34A', '#D97706', '#DC2626'],
          borderWidth: 0
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
  }

  // Chart 2 - Horizontal bar: top feature importances
  var impCtx = document.getElementById('importanceChart');
  if (impCtx) {
    new Chart(impCtx, {
      type: 'bar',
      data: {
        labels: importance.map(function (d) { return d.feature.replace(/_/g, ' '); }),
        datasets: [{
          label: 'Importance',
          data: importance.map(function (d) { return d.importance; }),
          backgroundColor: '#2563EB'
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: '#EBF2FF' } },
          y: { grid: { display: false } }
        }
      }
    });
  }

  // Chart 3 - Line: predictions per day (last 30 days)
  var trendCtx = document.getElementById('trendChart');
  if (trendCtx) {
    new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: trend.map(function (d) { return d.day; }),
        datasets: [{
          label: 'Predictions',
          data: trend.map(function (d) { return d.count; }),
          borderColor: '#1B3A6B',
          backgroundColor: '#EBF2FF',
          fill: true,
          tension: 0.3,
          pointRadius: 3
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }
})();
