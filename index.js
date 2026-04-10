function setMode(mode) {
    document.body.setAttribute('data-mode', mode);
    document.getElementById('opt-ios').classList.toggle('active', mode === 'ios');
    document.getElementById('opt-gbc').classList.toggle('active', mode === 'gbc');
    document.getElementById('ring-ios').style.display = mode === 'ios' ? '' : 'none';
    document.getElementById('ring-gbc').style.display = mode === 'gbc' ? '' : 'none';
    history.replaceState(null, '', mode === 'gbc' ? '?mode=gbc' : '?mode=ios');
}

function toggleMode() {
    var current = document.body.getAttribute('data-mode');
    setMode(current === 'ios' ? 'gbc' : 'ios');
}

// Restore mode from URL on load
document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    var mode = params.get('mode');
    if (mode === 'gbc') {
        setMode('gbc');
    }
});