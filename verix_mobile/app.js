document.getElementById('start-btn').addEventListener('click', function() {
    const btn = this;
    const greeting = document.getElementById('greeting');

    // Add immediate feedback
    btn.style.opacity = '0';
    btn.style.pointerEvents = 'none';

    setTimeout(() => {
        btn.classList.add('hidden');
        greeting.classList.remove('hidden');
    }, 300);
});
