// Initialize Leaflet map
var map = L.map('mapContainer').setView([51.505, -0.09], 13);
let dataLayer;

// Use an alternate tile server that supports subdomains for better performance
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a', 'b', 'c']  // Load from multiple subdomains for faster performance
}).addTo(map);

function go_button_onclick() {
    var country = document.getElementById("country").value;
    var admin_level = document.getElementById("admin level").value;
    var data_type = document.getElementById("data type").value;
    console.log("country: " + country);
    console.log("admin level: " + admin_level);
    console.log("data type: " + data_type);

    // Determine file path based on data type
    const url = `http://127.0.0.1:5000/${country}/hazard/flood/${admin_level}/?format=${data_type}`;
    //const filePath = data_type.toLowerCase() === 'geojson' ? 'https://github.com/mapaction/hazard-visualisation-tool/raw/refs/heads/main/data/lebanon-draft-01.json' : 'https://github.com/mapaction/hazard-visualisation-tool/raw/refs/heads/main/data/lebanon-draft-01.csv';

    // Load data from file
    loadDataFromFile(url, data_type.toLowerCase());
}

function loadDataFromFile(filePath, dataType) {
    fetch(filePath)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return dataType === 'geojson' ? response.json() : response.text();
        })
        .then(data => {
            processData(data, dataType);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error.message);
        });
}

function processData(data, dataType) {
    const isGeojson = dataType === 'geojson';
    const tableData = isGeojson ? geojsonToTable(data) : parseCSVToTable(data);
    
    // Display table
    document.getElementById('tableContainer').innerHTML = "";
    document.getElementById('tableContainer').appendChild(tableData);

    // Update map
    initMap(data, isGeojson);
}


function initMap(data, isGeojson) {
    if (!map) {
        map = L.map('mapContainer').setView([51.505, -0.09], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            subdomains: ['a', 'b', 'c']
        }).addTo(map);
    }

    if (dataLayer) {
        map.removeLayer(dataLayer);
    }

    // Create new data layer
    if (isGeojson) {
        dataLayer = L.geoJSON(data, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng);
            },
            onEachFeature: function(feature, layer) {
                if (feature.properties && feature.properties.name) {
                    layer.bindPopup(feature.properties.name);
                }
            }
        });
    } else {
        dataLayer = L.layerGroup();
        const rows = data.split('\n');
        for (let i = 1; i < rows.length; i++) {
            let [name, lat, lng] = rows[i].split(',');
            L.marker([parseFloat(lat), parseFloat(lng)])
                .bindPopup(name)
                .addTo(dataLayer);
        }
    }

    // Add the new data layer to the map
    dataLayer.addTo(map);

    // Fit the map bounds to the new data layer
    map.fitBounds(dataLayer.getBounds());
}

function geojsonToTable(geojson) {
    let table = document.createElement('table');
    table.className = 'table table-zebra';

    let headerRow = table.insertRow();
    ['Name', 'Latitude', 'Longitude'].forEach(header => {
        let th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    geojson.features.forEach(feature => {
        let row = table.insertRow();
        let nameCell = row.insertCell();
        nameCell.textContent = feature.properties.name;
        let latCell = row.insertCell();
        latCell.textContent = feature.geometry.coordinates[1];
        let lngCell = row.insertCell();
        lngCell.textContent = feature.geometry.coordinates[0];
    });

    return table;
}

function parseCSVToTable(csv) {
    const rows = csv.split('\n');
    
    // Create a table element
    let table = document.createElement('table');
    table.className = 'table table-zebra'; // Using DaisyUI classes

    // Create table header
    let headerRow = table.insertRow();
    let headers = rows[0].split(',');
    headers.forEach(header => {
        let th = document.createElement('th');
        th.textContent = header.trim();
        headerRow.appendChild(th);
    });

    // Create table body
    for (let i = 1; i < rows.length; i++) {
        let row = table.insertRow();
        let cells = rows[i].split(',');
        cells.forEach(cell => {
            let td = row.insertCell();
            td.textContent = cell.trim();
        });
    }

    return table;
}

// Function to populate the select element with country data
function populateCountrySelect(countries) {
    const select = document.getElementById('country');
    
    // Clear existing options
    select.innerHTML = '';
    
    // Add a default option
    const defaultOption = document.createElement('option');
    defaultOption.text = 'Select a country';
    defaultOption.value = '';
    select.add(defaultOption);
    
    // Add an option for each country

    for (var c of countries){
        const option = document.createElement('option');
        option.text = c.name;
        option.value = c.iso_3;
        select.add(option);

    };
}

async function fetchCountryData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/countries/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log(response.data);
        const data = await response.json();
        return data; // Assuming the API returns an array of [countryName, isoCode] tuples
    } catch (error) {
        console.error('Error fetching country data:', error);
        return [];
    }
}

async function initCountrySelect() {
    const countries = await fetchCountryData();
    populateCountrySelect(countries);
}


document.addEventListener('DOMContentLoaded', initCountrySelect);
