// Add copy buttons to all code blocks
document.addEventListener('DOMContentLoaded', function() {
    // Find all code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach((codeBlock) => {
        const pre = codeBlock.parentElement;
        
        // Create wrapper div for pre element
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';
        
        // Create header for code block
        const header = document.createElement('div');
        header.className = 'code-block-header';
        
        // Get language from class name (e.g., language-python)
        let language = 'code';
        const classes = codeBlock.className.split(' ');
        for (let cls of classes) {
            if (cls.startsWith('language-')) {
                language = cls.replace('language-', '');
                break;
            }
        }
        
        // Create language label
        const languageLabel = document.createElement('span');
        languageLabel.className = 'code-language';
        languageLabel.textContent = language;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');
        
        // Add click event to copy button
        copyButton.addEventListener('click', function() {
            const code = codeBlock.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(code).then(() => {
                // Change button text to "Copied"
                copyButton.innerHTML = '<i class="fas fa-check"></i> Copied';
                copyButton.classList.add('copied');
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy code:', err);
                // Fallback for older browsers
                fallbackCopy(code, copyButton);
            });
        });
        
        // Append elements
        header.appendChild(languageLabel);
        header.appendChild(copyButton);
        
        // Wrap the pre element
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(header);
        wrapper.appendChild(pre);
    });
});

// Fallback copy function for older browsers
function fallbackCopy(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        button.innerHTML = '<i class="fas fa-check"></i> Copied';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-copy"></i> Copy';
            button.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('Fallback copy failed:', err);
    }
    
    document.body.removeChild(textArea);
}