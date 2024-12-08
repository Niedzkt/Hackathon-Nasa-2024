{% extends "base.html" %}

{% block content %}

<script src="https://unpkg.com/leaflet.heat/dist/leaflet-heat.js"></script>
<script src="https://unpkg.com/@turf/turf/turf.min.js"></script>

<div id="map"></div>

<script>
    var map = L.map('map').setView([50.86, 20.629], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    var popup = L.popup();

    // Function to handle polygon submission and generate heatmap
    function genHeatMap() {
        console.log("Generating heatmap for polygon:", polygonPoints);

        // Send polygon points to the backend
        fetch('/map/solar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                polygon_points: polygonPoints.map(function(latlng) {
                    return { lat: latlng.lat, lng: latlng.lng };
                })
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Backend response:', data);

            if (!data.heat_array || data.heat_array.length === 0) {
                console.error('No heat points received');
                return;
            }

            var heatArray = data.heat_array;

            // Add heatmap layer
            var heat = L.heatLayer(heatArray, {
                radius: 25,
                blur: 55,
                maxZoom: 17,
            }).addTo(map);

            // Optionally draw circles around the points
            
	})}

    var startPoint = null;
    var rectangle = null;
    var drawing = false;  // Flag to check if drawing is in progress

    var polygonPoints = [];  // List of points for the polygon
    var polygon = null;  // Reference to the drawn polygon

    var markers = [];  // List of markers on the map

    // Function to add markers with popups for each point
    function addMarker(latlng) {
        var marker = L.marker(latlng).addTo(map);
        marker.bindPopup('Lat: ' + latlng.lat.toFixed(6) + ', Lng: ' + latlng.lng.toFixed(6)).openPopup();
        markers.push(marker);  // Add marker to the list to remove later
    }

    // Function to clear all markers from the map
    function clearMarkers() {
        markers.forEach(function(marker) {
            map.removeLayer(marker);
        });
        markers = [];  // Clear the list of markers
    }

    function updatePolygon() {
        if (polygon) {
            map.removeLayer(polygon);
        }

        // Draw polygon if we have at least 3 points
        if (polygonPoints.length > 2) {
            polygon = L.polygon(polygonPoints, { color: 'blue', weight: 0.5 }).addTo(map);
        }
    }

    // Event mousedown - start holding the right mouse button
    map.on('mousedown', function(e) {
        if (e.originalEvent.button === 2 && e.originalEvent.ctrlKey) {  // Check if it's right-click with Ctrl
            startPoint = e.latlng;
            drawing = true;  // Start drawing

            // If a rectangle exists, remove it
            if (rectangle) {
                map.removeLayer(rectangle);
                rectangle = null;  // Reset rectangle
                clearMarkers();
            }

            // Listen for mouse movement (dynamic drawing)
            map.on('mousemove', onMouseMove);
        }
    });

    // Event mousemove - draw rectangle while moving the cursor
    function onMouseMove(e) {
        if (drawing && startPoint) {
            var currentPoint = e.latlng;

            // Define rectangle coordinates from startPoint to currentPoint
            var bounds = L.latLngBounds(startPoint, currentPoint);

            // If the rectangle exists, update its bounds
            if (rectangle) {
                rectangle.setBounds(bounds);
            } else {
                // Create a new rectangle
                rectangle = L.rectangle(bounds, { color: "blue", weight: 0.5 }).addTo(map);
            }
            clearMarkers();  // Remove previous markers
            addMarker(bounds.getNorthWest());  // Northwest corner
            addMarker(bounds.getNorthEast());  // Northeast corner
            addMarker(bounds.getSouthWest());  // Southwest corner
            addMarker(bounds.getSouthEast());  // Southeast corner
        }
    }

    // Event mouseup - stop holding the right mouse button
    map.on('mouseup', function(e) {
        if (e.originalEvent.button === 2 && drawing) {  // Check if it's right-click and drawing is in progress
            map.off('mousemove', onMouseMove);  // Stop tracking mouse movement
            drawing = false;  // Finished drawing
            startPoint = null;  // Reset start point
        }
    });

    map.on('click', function(e) {
        if (!drawing) {  // Add points only if we're not drawing a rectangle
            var point = e.latlng;
            polygonPoints.push(point);  // Add point to the list of vertices

            // If the polygon already exists, remove it before drawing a new one
            if (polygon) {
                map.removeLayer(polygon);
            }

            if(rectangle) {
                map.removeLayer(rectangle);
                rectangle = null;
                clearMarkers();
            }

            // Draw a new polygon if we have at least 3 points
            if (polygonPoints.length > 2) {
                polygon = L.polygon(polygonPoints, { color: 'blue', weight: 0.5 }).addTo(map);
            }
            addMarker(point);
        }
    });

    map.on('contextmenu', function(e) {  // Use contextmenu to react to the right mouse button
        // Remove the existing polygon and reset the list of points
        if (polygon) {
            map.removeLayer(polygon);
            polygon = null;
            polygonPoints = [];
            clearMarkers();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'z') {  // Check if Ctrl+Z is pressed
            if (polygonPoints.length > 0) {
                polygonPoints.pop();  // Remove the last point from the list
                updatePolygon();  // Update the polygon on the map

                // Remove the last marker
                var lastMarker = markers.pop();
                if (lastMarker) {
                    lastMarker.remove();  // Remove the last marker from the map
                }

                console.log("Last vertex undone.");
            }
        }
        if (e.key === 'Enter') {  // Check if Enter is pressed
            console.log("Enter pressed - generating heatmap.");

            // Generate heatmap for the polygon
            if (polygonPoints.length > 2) {
                genHeatMap();  // Generate heatmap based on the polygon
            } else {
                console.error("Polygon must have at least 3 points.");
            }
        }
    });

    map.getContainer().oncontextmenu = function (e) {
        e.preventDefault();  // Prevent the context menu from appearing
    };

</script>

{% endblock %}
