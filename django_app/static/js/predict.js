(function () {
  var form = document.getElementById('predict-form');
  if (!form) return;
  form.addEventListener('submit', function () {
    var spinner = document.getElementById('submit-spinner');
    var label = document.getElementById('submit-label');
    var btn = document.getElementById('submit-btn');
    if (spinner) spinner.style.display = 'inline-block';
    if (label) label.textContent = 'Predicting...';
    if (btn) btn.setAttribute('disabled', 'disabled');
  });
})();
