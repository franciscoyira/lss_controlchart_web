// Provide immediate feedback on button clicks
document.addEventListener('DOMContentLoaded', function() {
    // Function to handle button clicks
    function addWorkingState(id) {
        document.getElementById(id).addEventListener('click', function() {
            // For upload button, we need to add the class to the parent
            if (id === 'upload-data') {
                document.getElementById('upload-card').classList.add('working');
            } else {
                this.classList.add('working');
            }
            
            // Remove working class after callback completes (handled by MutationObserver)
        });
    }
    
    // Add click handlers to all option buttons
    addWorkingState('upload-card');
    addWorkingState('btn-in-control');
    addWorkingState('btn-out-of-control');
    
    // Create a MutationObserver to detect when the active class is added by the callback
    // This will remove the working class once the callback has completed
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const element = mutation.target;
                if (element.classList.contains('active') && element.classList.contains('working')) {
                    element.classList.remove('working');
                }
            }
        });
    });
    
    // Observe all three buttons for class changes
    const buttons = [
        document.getElementById('upload-card'), 
        document.getElementById('btn-in-control'), 
        document.getElementById('btn-out-of-control')
    ];
    
    buttons.forEach(function(button) {
        if (button) {
            observer.observe(button, { attributes: true });
        }
    });
});
