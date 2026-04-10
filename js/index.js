var EMULATOR_SRC = '/play/monopong-gbc.html';

function unloadEmulator() {
    var frame = document.getElementById('emulator-frame');
    frame.src = 'about:blank';
    document.getElementById('emulator-container').style.display = 'none';
    document.getElementById('gbc-back').style.display = 'none';
    document.body.classList.remove('emulator-active');
}

function setMode(mode) {
    document.body.setAttribute('data-mode', mode);
    document.getElementById('opt-ios').classList.toggle('active', mode === 'ios');
    document.getElementById('opt-gbc').classList.toggle('active', mode === 'gbc');
    document.getElementById('ring-ios').style.display = mode === 'ios' ? 'flex' : 'none';
    document.getElementById('ring-gbc').style.display = mode === 'gbc' ? 'block' : 'none';
    unloadEmulator();
    history.replaceState(null, '', mode === 'gbc' ? '?mode=gbc' : '?mode=ios');
}

function toggleMode() {
    var current = document.body.getAttribute('data-mode');
    setMode(current === 'ios' ? 'gbc' : 'ios');
}

function showEmulator() {
    document.getElementById('ring-gbc').style.display = 'none';
    document.getElementById('emulator-frame').src = EMULATOR_SRC;
    document.getElementById('emulator-container').style.display = 'block';
    document.getElementById('gbc-back').style.display = 'block';
    document.body.classList.add('emulator-active');
}

function hideEmulator() {
    unloadEmulator();
    document.getElementById('ring-gbc').style.display = 'block';
}

// Restore mode from URL on load
document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    var mode = params.get('mode');
    if (mode === 'gbc') {
        setMode('gbc');
    }
});