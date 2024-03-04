document.addEventListener("DOMContentLoaded", function() {
    // Select all links in the side menu
    var sideMenuLinks = document.querySelectorAll('.side-menu a');

    // Add event listener to each link
    sideMenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Remove active class from all links
            sideMenuLinks.forEach(function(link) {
                link.classList.remove('active');
            });
            
            // Add active class to the clicked link
            this.classList.add('active');
        });
    });
});