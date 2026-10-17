/* Local Leaflet and Lucide assets; only background tiles require network access. */
(() => {
  document.querySelectorAll('.obsidian-map').forEach((container) => {
    const data = JSON.parse(container.dataset.map);
    container.replaceChildren();
    const map = L.map(container, {maxZoom: Number(data.maxZoom)});
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxNativeZoom: 19,
      maxZoom: Number(data.maxZoom),
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    const positions = [];
    data.markers.forEach((note) => {
      const pin = document.createElement('span');
      pin.className = 'obsidian-map-pin';
      pin.style.backgroundColor = CSS.supports('color', note.color) ? note.color : '#6750a4';
      const icon = document.createElement('i');
      icon.dataset.lucide = typeof note.icon === 'string' ? note.icon : 'map-pin';
      pin.append(icon);
      const marker = L.marker(note.coordinates, {
        title: note.title,
        icon: L.divIcon({html: pin, className: '', iconSize: [32, 32], iconAnchor: [16, 32]})
      }).addTo(map);
      const link = document.createElement('a');
      link.href = note.url;
      link.textContent = note.title;
      link.className = 'internal-link';
      marker.bindPopup(link);
      positions.push(note.coordinates);
    });
    if (data.center) map.setView(data.center, Number(data.zoom));
    else if (positions.length) map.fitBounds(positions, {padding: [24, 24], maxZoom: Number(data.zoom)});
    else map.setView([0, 0], 2);
    lucide.createIcons();
    if (!positions.length) {
      const message = L.control({position: 'topright'});
      message.onAdd = () => {
        const element = L.DomUtil.create('div', 'obsidian-map-message');
        element.textContent = 'No notes with valid coordinates.';
        return element;
      };
      message.addTo(map);
    }
    new ResizeObserver(() => map.invalidateSize()).observe(container);
  });
})();
