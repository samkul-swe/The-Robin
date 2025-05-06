document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // URL form submission
    const urlForm = document.getElementById('url-form');
    if (urlForm) {
        urlForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAnalysisForm(this);
        });
    }
    
    // Manual form submission
    const manualForm = document.getElementById('manual-form');
    if (manualForm) {
        manualForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAnalysisForm(this);
        });
    }
    
    // Form submission handler
    function submitAnalysisForm(form) {
        // Show loading spinner
        const loadingEl = document.getElementById('loading');
        loadingEl.classList.remove('hidden');
        
        // Disable submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        
        // Create form data
        const formData = new FormData(form);
        
        // Send AJAX request
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'An error occurred during analysis');
                });
            }
            return response.json();
        })
        .then(result => {
            // Hide loading spinner
            loadingEl.classList.add('hidden');
            
            // Re-enable submit button
            submitBtn.disabled = false;
            
            // Redirect to results page with data
            const resultJson = encodeURIComponent(JSON.stringify(result));
            window.location.href = `/results?result=${resultJson}`;
        })
        .catch(error => {
            // Hide loading spinner
            loadingEl.classList.add('hidden');
            
            // Re-enable submit button
            submitBtn.disabled = false;
            
            // Show error
            alert('Error: ' + error.message);
        });
    }
});