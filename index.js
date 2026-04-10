function toggleMode() {
    var body = document.body;
    var newMode = body.getAttribute('data-mode') === 'ios' ? 'gbc' : 'ios';

    body.setAttribute('data-mode', newMode);

    document.getElementById('opt-ios').classList.toggle('active', newMode === 'ios');
    document.getElementById('opt-gbc').classList.toggle('active', newMode === 'gbc');
}