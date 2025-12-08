// ========================================
// LOADING SCREEN
// ========================================
window.addEventListener('load', function() {
    const loadingScreen = document.getElementById('loadingScreen');
    
    // Hide loading screen after 2 seconds
    setTimeout(function() {
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            loadingScreen.style.visibility = 'hidden';
            loadingScreen.style.pointerEvents = 'none';
        }
    }, 2000);
});

// ========================================
// TOGGLE GROUP FUNCTION
// ========================================
function toggleGroup(groupId) {
    console.log('Toggling group:', groupId);
    
    const content = document.getElementById('group-content-' + groupId);
    const icon = document.getElementById('group-icon-' + groupId);
    
    if (!content || !icon) {
        console.error('Element not found for group:', groupId);
        return;
    }
    
    // Toggle display
    if (content.style.display === 'block') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
        console.log('Group closed:', groupId);
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
        console.log('Group opened:', groupId);
    }
}

// ========================================
// TOGGLE SUBSECTIONS FUNCTION
// ========================================
function toggleSubsections(blogId) {
    console.log('Toggling subsections for blog:', blogId);
    
    const content = document.getElementById('subsections-' + blogId);
    const icon = document.getElementById('icon-' + blogId);
    
    if (!content || !icon) {
        console.error('Element not found for blog:', blogId);
        return;
    }
    
    // Toggle display
    if (content.style.display === 'block') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
        console.log('Subsections closed:', blogId);
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
        console.log('Subsections opened:', blogId);
    }
}

// ========================================
// DOM READY EVENT
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Add click event to all group headers for better UX
    const groupHeaders = document.querySelectorAll('.group-header');
    console.log('Found', groupHeaders.length, 'group headers');
    
    groupHeaders.forEach(header => {
        // Skip if already has onclick
        if (header.hasAttribute('onclick')) {
            return;
        }
        
        header.addEventListener('click', function(e) {
            // Don't trigger if the click was on the toggle button
            if (!e.target.closest('.toggle-btn')) {
                const groupId = this.querySelector('.toggle-btn')?.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
                if (groupId) {
                    toggleGroup(groupId);
                }
            }
        });
    });
    
    // Add smooth scrolling for subsection links
    const subsectionLinks = document.querySelectorAll('.subsection-link');
    subsectionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.includes('#')) {
                e.preventDefault();
                const targetId = href.split('#')[1];
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Press 'Escape' to close all open groups and subsections
        if (e.key === 'Escape') {
            document.querySelectorAll('.group-content[style*="display: block"]').forEach(content => {
                const groupId = content.id.replace('group-content-', '');
                toggleGroup(groupId);
            });
            
            document.querySelectorAll('.subsections[style*="display: block"]').forEach(subsection => {
                const blogId = subsection.id.replace('subsections-', '');
                toggleSubsections(blogId);
            });
        }
    });
    
    // Add terminal-style typing effect to welcome message (optional)
    const welcomeTitle = document.querySelector('.welcome-message h1');
    if (welcomeTitle && welcomeTitle.textContent) {
        const originalText = welcomeTitle.textContent;
        welcomeTitle.textContent = '';
        let charIndex = 0;
        
        function typeWriter() {
            if (charIndex < originalText.length) {
                welcomeTitle.textContent += originalText.charAt(charIndex);
                charIndex++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Start typing effect after loading screen
        setTimeout(typeWriter, 2500);
    }
    
    console.log('All event listeners attached successfully');
});

// ========================================
// SCROLL ANIMATIONS (Optional Enhancement)
// ========================================
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

// Observe all cards when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        observer.observe(card);
    });
});

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Function to close all groups
function closeAllGroups() {
    document.querySelectorAll('.group-content[style*="display: block"]').forEach(content => {
        const groupId = content.id.replace('group-content-', '');
        toggleGroup(groupId);
    });
}

// Function to open all groups
function openAllGroups() {
    document.querySelectorAll('.group-content').forEach(content => {
        const groupId = content.id.replace('group-content-', '');
        if (content.style.display !== 'block') {
            toggleGroup(groupId);
        }
    });
}

// Function to search blogs (can be extended)
function searchBlogs(query) {
    const blogItems = document.querySelectorAll('.blog-item');
    const lowerQuery = query.toLowerCase();
    
    blogItems.forEach(item => {
        const title = item.querySelector('.blog-title')?.textContent.toLowerCase() || '';
        if (title.includes(lowerQuery)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Console welcome message
console.log('%c$ blog.start', 'color: #00ff41; font-size: 20px; font-family: monospace;');
console.log('%cWelcome to the Terminal Blog!', 'color: #8b949e; font-size: 14px; font-family: monospace;');
console.log('%cPress ESC to close all groups', 'color: #8b949e; font-size: 12px; font-family: monospace;');


// Typing Animation Script
(function() {
    const quotes = [
        "If you love too much, you will be cheated,\nif you speak too much, you will lie,\nif you cry too much, you will lose your sight,\nif you think too much, you will be depressed,\nif you care too much, you will be taken for granted,\nif you trust too much, you will be betrayed,\nif you work too much, you will lose your life.\n\nDon't be too much, because that too much can hurt you so much."
    ];
    
    const typingText = document.getElementById('typingText');
    const cursor = document.querySelector('.cursor-blink');
    
    let quoteIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let isPaused = false;
    
    function type() {
        const currentQuote = quotes[quoteIndex];
        
        if (!isDeleting && charIndex <= currentQuote.length) {
            // Typing forward
            typingText.textContent = currentQuote.substring(0, charIndex);
            charIndex++;
            
            if (charIndex > currentQuote.length) {
                // Finished typing, pause before restarting
                isPaused = true;
                setTimeout(() => {
                    isPaused = false;
                    charIndex = 0;
                    typingText.textContent = '';
                }, 3000); // Pause for 3 seconds after complete
                return;
            }
            
            // Random typing speed for more natural effect
            const typingSpeed = Math.random() * 50 + 30;
            setTimeout(type, typingSpeed);
        } else if (isPaused) {
            setTimeout(type, 100);
        } else {
            // Start over
            setTimeout(type, 500);
        }
    }
    
    // Start typing when page loads
    window.addEventListener('load', function() {
        setTimeout(type, 3000); // Start after 3 seconds (after loading screen)
    });
})();