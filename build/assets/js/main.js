document.addEventListener('DOMContentLoaded', function() {
    initializeHomePageFeatures();
});

// Separate initialization function so it can be called from Angular components
function initializeHomePageFeatures() {
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // Skip empty anchors
            
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Header scroll effect
    const header = document.querySelector('header');
    if (header) {
        let lastScrollTop = 0;

        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > 100) {
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            } else {
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            }
            
            lastScrollTop = scrollTop;
        });
    }    // Add loading animation for images (exclude SVGs to preserve their animations)
    const images = document.querySelectorAll('img:not([src$=".svg"])');
    images.forEach(img => {
        // For already loaded images
        if (img.complete) {
            img.style.opacity = '1';
            img.style.transform = 'translateY(0)';
        } else {
            img.addEventListener('load', function() {
                this.style.opacity = '1';
                this.style.transform = 'translateY(0)';
            });
        }
        
        // Set initial styles for animation
        img.style.opacity = '0';
        img.style.transform = 'translateY(20px)';
        img.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    // Handle SVG images and objects separately to preserve their animations
    const svgImages = document.querySelectorAll('img[src$=".svg"], object[type="image/svg+xml"]');
    svgImages.forEach(element => {
        // Ensure SVG is visible and not affected by any transforms
        element.style.opacity = '1';
        element.style.transform = 'none';
        element.style.transition = 'none';
        
        // Reset any animations that might interfere
        element.style.animation = 'none';
        
        // For object elements, ensure they load properly
        if (element.tagName.toLowerCase() === 'object') {
            element.addEventListener('load', function() {
                // Ensure the object is visible once loaded
                this.style.opacity = '1';
            });
        }
    });    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe info boxes for animation
    const infoBoxes = document.querySelectorAll('.info-box');
    infoBoxes.forEach(box => {
        box.style.opacity = '0';
        box.style.transform = 'translateY(30px)';
        box.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(box);
    });

    // Add click tracking for buttons (analytics placeholder)
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Placeholder for analytics tracking
            console.log('Button clicked:', this.textContent);
        });
    });
}

// Export the function for use in Angular
if (typeof window !== 'undefined') {
    window.initializeHomePageFeatures = initializeHomePageFeatures;
}