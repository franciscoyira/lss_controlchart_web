// Provide immediate feedback on option card clicks.
// Uses event delegation because Dash renders the components with React
// after the page loads, so elements don't exist at DOMContentLoaded time.

// Pulse a card as soon as it's clicked (sample data cards)
document.addEventListener('click', function (e) {
    const card = e.target.closest('.option-card');
    // The upload card opens a file dialog on click; it gets its feedback
    // from the 'change' handler below instead, so a cancelled dialog
    // doesn't leave it pulsing forever
    if (card && !card.querySelector('input[type="file"]')) {
        card.classList.add('working');
    }
});

// Pulse the upload card once a file has actually been chosen
document.addEventListener('change', function (e) {
    if (e.target instanceof HTMLInputElement && e.target.type === 'file') {
        const card = e.target.closest('.option-card');
        if (card) {
            card.classList.add('working');
        }
    }
}, true);

// Stop pulsing once the callback marks the card as active.
// (Dash usually rewrites the class attribute wholesale, which already clears
// 'working'; this observer covers the cases where it doesn't.)
const workingObserver = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
        const el = mutation.target;
        if (el.classList && el.classList.contains('active') && el.classList.contains('working')) {
            el.classList.remove('working');
        }
    });
});

workingObserver.observe(document.documentElement, {
    attributes: true,
    subtree: true,
    attributeFilter: ['class']
});
