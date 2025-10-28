function toggleGroup(groupId) {
    console.log('Toggling group:', groupId); // Debug log
    const content = document.getElementById('group-content-' + groupId);
    const icon = document.getElementById('group-icon-' + groupId);
    
    if (!content || !icon) {
        console.error('Element not found for group:', groupId);
        return;
    }
    
    if (content.style.display === 'block' || content.style.display === '') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    }
}

function toggleSubsections(blogId) {
    console.log('Toggling subsections for blog:', blogId); // Debug log
    const content = document.getElementById('subsections-' + blogId);
    const icon = document.getElementById('icon-' + blogId);
    
    if (!content || !icon) {
        console.error('Element not found for blog:', blogId);
        return;
    }
    
    if (content.style.display === 'block' || content.style.display === '') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    }
}

// Add click event to group headers for better UX
document.addEventListener('DOMContentLoaded', function() {
    // Add click event to all group headers
    const groupHeaders = document.querySelectorAll('.group-header');
    groupHeaders.forEach(header => {
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
});

function toggleGroup(groupId) {
    const content = document.getElementById('group-content-' + groupId);
    const icon = document.getElementById('group-icon-' + groupId);
    if (content.style.display === 'block') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    }
}

// Keep the existing toggleSubsections function
function toggleSubsections(blogId) {
    const content = document.getElementById('subsections-' + blogId);
    const icon = document.getElementById('icon-' + blogId);
    if (content.style.display === 'block') {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    } else {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    }
}
