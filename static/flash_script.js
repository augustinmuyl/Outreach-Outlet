
document.addEventListener('DOMContentLoaded', function() {
    let flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(flashMessage) {
        flashMessage.style.display = 'block';
        
        setTimeout(function() {
            flashMessage.style.opacity = '0';
            setTimeout(function() {
                flashMessage.style.display = 'none';
            }, 600);
        }, 1000);
    });
});
