function toggleSubsections(id) {
  const container = document.getElementById(`subsections-${id}`);
  const icon = document.getElementById(`icon-${id}`);
  container.style.display = container.style.display === 'block' ? 'none' : 'block';
  icon.classList.toggle('fa-chevron-down');
  icon.classList.toggle('fa-chevron-up');
}

// Add this to your existing script
document.addEventListener('DOMContentLoaded', function() {
  // Process all code blocks in the content
  document.querySelectorAll('.content-html pre code').forEach(function(codeBlock) {
    const pre = codeBlock.parentElement;
    
    // Check if code block has a language class
    const languageMatch = codeBlock.className.match(/language-(\w+)/);
    if (languageMatch) {
      const language = languageMatch[1];
      
      // Create language label
      const label = document.createElement('div');
      label.className = 'language-label';
      label.textContent = language.toUpperCase();
      
      // Wrap the pre in a container
      const container = document.createElement('div');
      container.className = 'code-block';
      pre.parentNode.insertBefore(container, pre);
      container.appendChild(label);
      container.appendChild(pre);
    }
  });
});