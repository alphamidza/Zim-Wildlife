// Initialize the drought map
function initMap() {
    // Coordinates for Zimbabwe
    const zimbabweCoords = [-19.0154, 29.1549];
    
    // Create the map centered on Zimbabwe
    const map = L.map('drought-map').setView(zimbabweCoords, 6);
    
    // Add the base tile layer (using OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // In a real implementation, you would add drought intensity layers from your data
    // This is just a demonstration with sample data
    
    // Sample provinces with drought levels (0-4)
    const provinces = [
        {name: "Harare", coords: [-17.8252, 31.0335], level: 2},
        {name: "Bulawayo", coords: [-20.1325, 28.6265], level: 3},
        {name: "Manicaland", coords: [-18.9216, 32.1746], level: 1},
        {name: "Mashonaland Central", coords: [-16.7644, 31.0794], level: 2},
        {name: "Mashonaland East", coords: [-17.7624, 31.9019], level: 3},
        {name: "Mashonaland West", coords: [-17.4857, 29.7889], level: 4},
        {name: "Masvingo", coords: [-20.0748, 30.8323], level: 2},
        {name: "Matabeleland North", coords: [-18.5332, 27.5496], level: 1},
        {name: "Matabeleland South", coords: [-21.0089, 29.2368], level: 0},
        {name: "Midlands", coords: [-19.0552, 29.6035], level: 3}
    ];
    
    // Color scale for drought levels
    const colors = {
        0: '#ffff00', // D0 - Abnormally Dry
        1: '#fcd37f', // D1 - Moderate Drought
        2: '#ffaa00', // D2 - Severe Drought
        3: '#e60000', // D3 - Extreme Drought
        4: '#730000'  // D4 - Exceptional Drought
    };
    
    // Add markers for each province
    provinces.forEach(province => {
        const marker = L.circleMarker(province.coords, {
            radius: 10,
            fillColor: colors[province.level],
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup(`<b>${province.name}</b><br>Drought Level: ${province.level}`);
    });
    
    // In a real implementation, you would add polygon layers for each region
    // and style them according to drought intensity
}

// Initialize the map when the page loads
window.onload = initMap;