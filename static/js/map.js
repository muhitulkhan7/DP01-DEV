/**
 * Campus DengueWatch - Map Module
 * Purely map-related Leaflet.js logic per the JavaScript stack rule.
 */

(function (window) {
  'use strict';

  var CampusMap = {};

  /**
   * Initializes a Leaflet map with OpenStreetMap tiles restricted to the campus and 1 km buffer.
   */
  CampusMap.initMap = function (containerId, centerLat, centerLng, zoomLevel, boundary) {
    if (!document.getElementById(containerId)) {
      return null;
    }

    var defaultLat = centerLat || 23.759973;
    var defaultLng = centerLng || 90.348976;
    var defaultZoom = zoomLevel || 16;

    // Calculate or extract 1 km buffer bounding box
    var bufferBounds = null;
    if (boundary) {
      if (boundary.buffer_min_lat && boundary.buffer_max_lat && boundary.buffer_min_lng && boundary.buffer_max_lng) {
        bufferBounds = L.latLngBounds(
          [boundary.buffer_min_lat, boundary.buffer_min_lng],
          [boundary.buffer_max_lat, boundary.buffer_max_lng]
        );
      } else if (boundary.min_lat && boundary.max_lat && boundary.min_lng && boundary.max_lng) {
        // Fallback: ~1km buffer in degrees around bounding box
        bufferBounds = L.latLngBounds(
          [boundary.min_lat - 0.0090, boundary.min_lng - 0.0098],
          [boundary.max_lat + 0.0090, boundary.max_lng + 0.0098]
        );
      }
    }

    // Restrict viewport strictly to the campus and 1 km buffer zone
    var mapOptions = {
      center: [defaultLat, defaultLng],
      zoom: defaultZoom,
      minZoom: 14,
      maxZoom: 19,
      zoomControl: true,
      tap: true,
      touchZoom: true
    };

    if (bufferBounds) {
      mapOptions.maxBounds = bufferBounds;
      mapOptions.maxBoundsViscosity = 1.0;
    }

    var map = L.map(containerId, mapOptions);

    // Free OpenStreetMap Tile Layer (zero API key required)
    var tileOptionsStandard = {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    };

    var osmStandard = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', tileOptionsStandard);
    osmStandard.addTo(map);

    // 1. Draw 1 km Buffer Zone outline if defined
    if (bufferBounds) {
      L.rectangle(bufferBounds, {
        color: '#0d6efd',
        weight: 1.5,
        fillColor: '#0d6efd',
        fillOpacity: 0.03,
        dashArray: '6, 6'
      }).addTo(map).bindTooltip('1 km Monitoring Buffer', { sticky: true, direction: 'top' });
    }

    // 2. Draw true Campus Boundary polygon
    var campusLayer = null;
    if (boundary && boundary.geojson) {
      campusLayer = L.geoJSON(boundary.geojson, {
        style: {
          color: '#198754',
          weight: 2.5,
          fillColor: '#198754',
          fillOpacity: 0.12
        }
      }).addTo(map);

      var campusName = (boundary.name || 'Campus') + ' Boundary';
      campusLayer.bindTooltip(campusName, { sticky: true, className: 'campus-boundary-tooltip' });
    } else if (boundary && boundary.min_lat && boundary.max_lat && boundary.min_lng && boundary.max_lng) {
      var boxBounds = [
        [boundary.min_lat, boundary.min_lng],
        [boundary.max_lat, boundary.max_lng]
      ];
      campusLayer = L.rectangle(boxBounds, {
        color: '#198754',
        weight: 2.5,
        fillColor: '#198754',
        fillOpacity: 0.12
      }).addTo(map).bindTooltip('Campus Boundary', { sticky: true });
    }

    // Fit map view to campus boundary with comfortable padding so buffer context is visible
    if (campusLayer) {
      try {
        var cBounds = campusLayer.getBounds();
        if (cBounds.isValid()) {
          map.fitBounds(cBounds, { padding: [35, 35], maxZoom: 17 });
        }
      } catch (e) {
        // Fallback to center if fitBounds encounters an issue
      }
    }

    return map;
  };

  /**
   * Renders the heatmap density layer and individual report markers with popups.
   * Only active reports are passed in.
   */
  CampusMap.renderHeat = function (map, reportsData) {
    if (!map || !reportsData || reportsData.length === 0) {
      return;
    }

    var heatPoints = [];
    var markerGroup = L.layerGroup().addTo(map);

    reportsData.forEach(function (report) {
      // Heat point: [lat, lng, intensity]
      // All three categories contribute equally per agreed decisions
      heatPoints.push([report.lat, report.lng, 0.8]);

      // Report marker with detailed popup
      var popupContent = '<div class="p-1" style="max-width: 240px;">' +
        '<div class="fw-bold text-danger mb-1">' + report.category + '</div>' +
        (report.note ? '<p class="small mb-1 text-secondary">' + escapeHtml(report.note) + '</p>' : '') +
        (report.photo_url ? '<img src="' + report.photo_url + '" class="img-fluid rounded mb-1 popup-photo-preview" alt="Report photo">' : '') +
        '<div class="text-muted" style="font-size: 0.75rem;">' + report.created_at + '</div>' +
        '</div>';

      var marker = L.circleMarker([report.lat, report.lng], {
        radius: 7,
        fillColor: '#dc3545',
        color: '#ffffff',
        weight: 2,
        opacity: 0.9,
        fillOpacity: 0.8
      });

      marker.bindPopup(popupContent);
      markerGroup.addLayer(marker);
    });

    if (window.L && L.heatLayer) {
      L.heatLayer(heatPoints, {
        radius: 28,
        blur: 18,
        maxZoom: 17,
        gradient: {
          0.3: 'blue',
          0.5: 'lime',
          0.7: 'yellow',
          1.0: 'red'
        }
      }).addTo(map);
    }
  };

  /**
   * Enables click and tap to drop a pin and populate form coordinates.
   */
  CampusMap.enablePinPicker = function (map, initialLat, initialLng, latInputId, lngInputId, displayId, boundary) {
    if (!map) return;

    var latInput = document.getElementById(latInputId);
    var lngInput = document.getElementById(lngInputId);
    var displayEl = displayId ? document.getElementById(displayId) : null;
    var currentMarker = null;

    function isInsideBoundary(lat, lng) {
      if (!boundary) return true;
      if (boundary.min_lat && boundary.max_lat && boundary.min_lng && boundary.max_lng) {
        if (lat < boundary.min_lat || lat > boundary.max_lat || lng < boundary.min_lng || lng > boundary.max_lng) {
          return false;
        }
      }
      if (boundary.geojson) {
        try {
          var geom = boundary.geojson.geometry || (boundary.geojson.features && boundary.geojson.features[0].geometry) || boundary.geojson;
          if (geom && geom.type === 'Polygon' && geom.coordinates && geom.coordinates[0]) {
            var ring = geom.coordinates[0];
            var inside = false;
            var n = ring.length;
            var p1x = ring[0][0], p1y = ring[0][1];
            for (var i = 1; i <= n; i++) {
              var p2x = ring[i % n][0], p2y = ring[i % n][1];
              if (lat > Math.min(p1y, p2y) && lat <= Math.max(p1y, p2y)) {
                if (lng <= Math.max(p1x, p2x)) {
                  var xinters = (p1y !== p2y) ? (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x : p1x;
                  if (p1x === p2x || lng <= xinters) {
                    inside = !inside;
                  }
                }
              }
              p1x = p2x;
              p1y = p2y;
            }
            return inside;
          }
        } catch (err) { }
      }
      return true;
    }

    function setCoordinates(lat, lng) {
      var roundedLat = Number(lat).toFixed(6);
      var roundedLng = Number(lng).toFixed(6);

      if (latInput) latInput.value = roundedLat;
      if (lngInput) lngInput.value = roundedLng;
      if (displayEl) {
        var inside = isInsideBoundary(Number(lat), Number(lng));
        if (inside) {
          displayEl.textContent = roundedLat + ', ' + roundedLng + ' (Inside Campus)';
          displayEl.classList.remove('text-muted', 'text-danger');
          displayEl.classList.add('text-success', 'fw-bold');
        } else {
          displayEl.textContent = roundedLat + ', ' + roundedLng + ' (Outside campus boundary)';
          displayEl.classList.remove('text-muted', 'text-success');
          displayEl.classList.add('text-danger', 'fw-bold');
        }
      }

      if (!currentMarker) {
        currentMarker = L.marker([lat, lng], { draggable: true }).addTo(map);
        currentMarker.on('dragend', function (e) {
          var pos = e.target.getLatLng();
          setCoordinates(pos.lat, pos.lng);
        });
      } else {
        currentMarker.setLatLng([lat, lng]);
      }
    }

    // Set initial pin if values are present (e.g. form redisplay after error)
    if (initialLat && initialLng && !isNaN(initialLat) && !isNaN(initialLng)) {
      setCoordinates(initialLat, initialLng);
    }

    // Click / tap handler on map
    map.on('click', function (e) {
      setCoordinates(e.latlng.lat, e.latlng.lng);
    });
  };

  function escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  window.CampusMap = CampusMap;
})(window);

