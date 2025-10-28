document.addEventListener('DOMContentLoaded', function() {
    const blogSearch = document.getElementById('blogSearch');
    const toggleShowBtn = document.getElementById('toggleShowBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const blogsGrid = document.getElementById('blogsGrid');
    const blogCheckboxes = document.querySelectorAll('.blog-checkbox');
    const selectedArea = document.getElementById('selectedArea');
    const selectedList = document.getElementById('selectedList');
    const selectedCount = document.querySelector('.selected-count');
    const groupAddButtons = document.querySelectorAll('.group-add-btn');
    
    let selectedBlogs = new Map(); // Map to store selected blogs (id -> title)
    let isShowingAll = true; // Track if all blogs are currently shown
    
    // Toggle Show/Hide functionality
    toggleShowBtn.addEventListener('click', function() {
        const blogItems = blogsGrid.querySelectorAll('.blog-checkbox-item');
        
        if (isShowingAll) {
            // Hide all
            blogItems.forEach(item => {
                item.style.display = 'none';
            });
            toggleShowBtn.textContent = 'Show All';
            isShowingAll = false;
        } else {
            // Show all
            blogItems.forEach(item => {
                item.style.display = 'flex';
            });
            toggleShowBtn.textContent = 'Hide All';
            isShowingAll = true;
        }
    });
    
    // Search functionality
    blogSearch.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const blogItems = blogsGrid.querySelectorAll('.blog-checkbox-item');
        
        blogItems.forEach(item => {
            const blogTitle = item.getAttribute('data-blog-title');
            const matchesSearch = blogTitle.includes(searchTerm);
            item.style.display = matchesSearch ? 'flex' : 'none';
        });
        
        // Update toggle button text based on search results
        const visibleItems = Array.from(blogItems).filter(item => item.style.display !== 'none');
        if (visibleItems.length === 0 && searchTerm) {
            toggleShowBtn.textContent = 'Show All';
            isShowingAll = false;
        } else if (visibleItems.length === blogItems.length) {
            toggleShowBtn.textContent = 'Hide All';
            isShowingAll = true;
        } else {
            toggleShowBtn.textContent = 'Show All';
            isShowingAll = false;
        }
    });
    
    // Select All functionality
    selectAllBtn.addEventListener('click', function() {
        const visibleBlogItems = Array.from(blogsGrid.querySelectorAll('.blog-checkbox-item'))
            .filter(item => item.style.display !== 'none');
        
        visibleBlogItems.forEach(item => {
            const checkbox = item.querySelector('.blog-checkbox');
            const blogId = checkbox.value;
            const blogTitle = checkbox.nextElementSibling.textContent;
            
            checkbox.checked = true;
            selectedBlogs.set(blogId, blogTitle);
        });
        
        updateSelectedArea();
    });
    
    // Deselect All functionality
    deselectAllBtn.addEventListener('click', function() {
        blogCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        selectedBlogs.clear();
        updateSelectedArea();
    });
    
    // Checkbox change handler
    blogCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const blogId = this.value;
            const blogTitle = this.nextElementSibling.textContent;
            
            if (this.checked) {
                selectedBlogs.set(blogId, blogTitle);
            } else {
                selectedBlogs.delete(blogId);
            }
            
            updateSelectedArea();
        });
    });
    
    // Update selected area
    function updateSelectedArea() {
        selectedList.innerHTML = '';
        selectedCount.textContent = `(${selectedBlogs.size})`;
        
        if (selectedBlogs.size > 0) {
            selectedArea.style.display = 'block';
            
            selectedBlogs.forEach((title, id) => {
                const selectedItem = document.createElement('div');
                selectedItem.className = 'selected-item';
                selectedItem.innerHTML = `
                    <span>${title}</span>
                    <button type="button" class="remove-selected" data-blog-id="${id}">&times;</button>
                `;
                selectedList.appendChild(selectedItem);
            });
            
            // Add event listeners to remove buttons
            document.querySelectorAll('.remove-selected').forEach(btn => {
                btn.addEventListener('click', function() {
                    const blogId = this.getAttribute('data-blog-id');
                    selectedBlogs.delete(blogId);
                    const checkbox = document.querySelector(`#blog_${blogId}`);
                    if (checkbox) checkbox.checked = false;
                    updateSelectedArea();
                });
            });
        } else {
            selectedArea.style.display = 'none';
        }
    }
    
// Bulk add functionality - FIXED VERSION
groupAddButtons.forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (selectedBlogs.size === 0) {
            alert('Please select at least one blog post');
            return;
        }
        
        const groupId = this.getAttribute('data-group-id');
        const groupName = this.textContent.trim();
        // Get the URL from the parent container's data attribute
        const bulkAddUrl = this.closest('.group-buttons').getAttribute('data-bulk-add-url');
        
        if (confirm(`Add ${selectedBlogs.size} selected blog(s) to "${groupName}"?`)) {
            // Create a single form to submit all selected blogs
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = bulkAddUrl; // Use the URL from data attribute
            form.style.display = 'none';
            
            // Add group_id
            const groupIdInput = document.createElement('input');
            groupIdInput.type = 'hidden';
            groupIdInput.name = 'group_id';
            groupIdInput.value = groupId;
            form.appendChild(groupIdInput);
            
            // Add all selected blog IDs
            selectedBlogs.forEach((title, blogId) => {
                const blogIdInput = document.createElement('input');
                blogIdInput.type = 'hidden';
                blogIdInput.name = 'blog_ids';
                blogIdInput.value = blogId;
                form.appendChild(blogIdInput);
            });
            
            document.body.appendChild(form);
            form.submit();
        }
    });
});
});