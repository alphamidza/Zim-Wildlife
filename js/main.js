// Set current date in the header
document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // For demonstration, we'll add a mobile menu button if needed
    // In a real implementation, you would add this dynamically
    console.log('Zimbabwe Drought Management System initialized');
    
    // Example of fetching drought data (would be replaced with real API calls)
    fetchDroughtData();
});

function fetchDroughtData() {
    // In a real implementation, this would fetch from an API
    console.log('Fetching drought data...');
    // Simulate API call
    setTimeout(() => {
        console.log('Drought data loaded');
        // Update UI elements with fetched data
    }, 1000);
}

// Search functionality
document.querySelector('.search-box button').addEventListener('click', function() {
    const searchTerm = document.querySelector('.search-box input').value;
    if (searchTerm.trim() !== '') {
        alert(`Searching for: ${searchTerm}`);
        // In real implementation, would redirect to search results
    }
});

// Language selector functionality
document.querySelector('.language-selector select').addEventListener('change', function() {
    const lang = this.value;
    console.log(`Language changed to: ${lang}`);
    // In real implementation, would reload page with selected language
    alert(`Language selection would change to ${lang} in a real implementation`);
});