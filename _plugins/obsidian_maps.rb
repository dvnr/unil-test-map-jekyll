# frozen_string_literal: true
require 'json'
require 'cgi'
require 'yaml'

# Render the supported subset of Obsidian Bases map views before wiki links.
class ObsidianMaps < Jekyll::Generator
  priority :highest

  def coordinates(value)
    parts = value.is_a?(Array) ? value : value.to_s.delete('[]').split(',')
    return unless parts.size == 2
    pair = parts.map { |part| Float(part) }
    pair if pair.all?(&:finite?) && pair[0].between?(-90, 90) && pair[1].between?(-180, 180)
  rescue ArgumentError, TypeError
    nil
  end

  def property(note, expression, fallback)
    key = expression.to_s.delete_prefix('note.')
    note.data[key.empty? ? fallback : key]
  end

  def generate(site)
    bases = Dir.glob(File.join(site.source, '**', '*.base')).reject do |path|
      path.start_with?(site.dest + File::SEPARATOR)
    end
    documents = site.collections['notes'].docs + site.pages
    documents.each do |document|
      document.content = document.content.gsub(/!\[\[([^\]\n]+\.base)\]\]/) do
        reference = Regexp.last_match(1)
        matches = bases.select do |path|
          path.delete_prefix(site.source + '/') == reference || File.basename(path) == reference
        end
        raise Jekyll::Errors::FatalException, "Map base missing or ambiguous: #{reference}" unless matches.size == 1
        base = YAML.safe_load(File.read(matches.first), permitted_classes: [], aliases: false) || {}
        views = Array(base['views']).select { |view| view['type'] == 'map' }
        raise Jekyll::Errors::FatalException, "No map view in #{reference}" if views.empty?
        # Never silently publish notes excluded by a private Obsidian filter.
        if base['filters'] || views.any? { |view| view['filters'] }
          raise Jekyll::Errors::FatalException, "Obsidian Maps: filters are not supported in #{reference}; create an unfiltered publication base"
        end
        views.map do |view|
          unless Array(view['mapTiles']).empty?
            raise Jekyll::Errors::FatalException, "Obsidian Maps: custom mapTiles are not supported in #{reference}"
          end
          markers = site.collections['notes'].docs.filter_map do |note|
            position = coordinates(property(note, view['coordinates'], 'coordinates'))
            next unless position
            extension = site.config['use_html_extension'] ? '.html' : ''
            { coordinates: position, title: note.data['title'] || File.basename(note.path, '.*'),
              url: "#{site.baseurl}#{note.url}#{extension}",
              icon: property(note, view['markerIcon'], 'icon'),
              color: property(note, view['markerColor'], 'color') }
          end
          payload = { markers: markers, center: coordinates(view['center']),
                      zoom: view.fetch('defaultZoom', 9), maxZoom: view.fetch('maxZoom', 19),
                      name: view.fetch('name', 'Map') }
          height = Integer(view.fetch('mapHeight', 500)).clamp(200, 1200)
          data = CGI.escapeHTML(JSON.generate(payload))
          %(<div class="obsidian-map" style="height: #{height}px" data-map="#{data}" role="region" aria-label="#{CGI.escapeHTML(payload[:name].to_s)}"><p>Loading map…</p></div>)
        end.join("\n")
      end
    end
  end
end
