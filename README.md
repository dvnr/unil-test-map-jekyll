[![Netlify Status](https://api.netlify.com/api/v1/badges/8cfa8785-8df8-4aad-ad35-8f1c790b8baf/deploy-status)](https://app.netlify.com/sites/digital-garden-jekyll-template/deploys)

# Digital garden Jekyll template

Use this template repository to get started with your own digital garden.

**I wrote a tutorial explaining how to set it up: [Setting up your own digital garden with Jekyll](https://maximevaillancourt.com/blog/setting-up-your-own-digital-garden-with-jekyll)**

Preview the template here: https://digital-garden-jekyll-template.netlify.app/

- Based on Jekyll, a static website generator
- Supports Roam-style double bracket link syntax to other notes
- Creates backlinks to other notes automatically
- Features link previews on hover
- Includes graph visualization of the notes and their links
- Features a simple and responsive design
- Supports Markdown or HTML notes

<img width="1522" alt="Screen Shot 2020-05-19 at 23 05 46" src="https://user-images.githubusercontent.com/8457808/82400515-7d026d80-9a25-11ea-83f1-3b9cb8347e07.png">

## A note about GitHub Pages
> [!NOTE]  
> **Update (January 2023)**: it seems that GitHub Pages supports custom plugins now, thanks to GitHub Actions ([view relevant discussion](https://github.com/maximevaillancourt/digital-garden-jekyll-template/discussions/144)). 

GitHub Pages only partially supports this template: to power the interactive notes graph, this template uses a custom Jekyll plugin to generate the graph data in [`notes_graph.json`](https://github.com/maximevaillancourt/digital-garden-jekyll-template/blob/7ac331a4113bac77c993856562acc2bfbde9f2f7/_plugins/bidirectional_links_generator.rb#L102), and [GitHub Pages doesn't support custom Jekyll plugins](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll#plugins).

If you want to use the graph with GitHub Pages, you may try building your garden locally using Jekyll then pushing the result to GitHub Pages.

Alternatively, you may deploy your garden to Netlify and it'll work out of the box. [I wrote a guide explaining how to set this up](https://maximevaillancourt.com/blog/setting-up-your-own-digital-garden-with-jekyll).

If you don't care about the graph, you can simply remove it from this layout, [as explained here](https://github.com/maximevaillancourt/digital-garden-jekyll-template/discussions/132#discussioncomment-3625772).

## License

Source code is available under the [MIT license](LICENSE.md).

## Publish Obsidian Maps in Jekyll

This site renders an Obsidian Bases map embed such as `![[index.base]]` inside
an exported note. Use the **Map** navigation link to open the existing example
(`_notes/home.md`). The two example article notes already contain coordinates.

Keep your `.base` file and its Markdown notes in `_notes`. For example:

```yaml
# A note's YAML front matter
---
title: My place
coordinates: [46.52047, 6.63271]
icon: book-image
color: red
---
```

The renderer reads map views from the embedded base, including `coordinates`,
`markerIcon`, `markerColor`, `center`, `defaultZoom`, `maxZoom`, and `mapHeight`.
Coordinates may be a two-item YAML list or a comma-separated string. Invalid
coordinates are skipped. Marker popups link to the generated note pages and
respect Jekyll's `baseurl`. Missing icons/colors use a map pin and purple.
Lucide icon names and CSS color values are supported.

This is a publication adapter, not the Obsidian plugin running in a browser.
It currently includes **all notes with valid coordinates**. Bases filters and
custom `mapTiles` fail the build explicitly rather than being silently ignored.
Formulas, sorting, and other Bases features are not evaluated; use direct
`note.property` references for coordinates, icons, and colors. Review the notes
you export before publishing. No changes to your Obsidian vault are needed.

Leaflet 1.9.4 and Lucide 0.468.0 are vendored in `assets/vendor` with their
licenses. The map uses OpenStreetMap's standard tiles and attribution; visitors
need network access to `tile.openstreetmap.org`. Follow the
[OpenStreetMap tile usage policy](https://operations.osmfoundation.org/policies/tiles/)
and choose a suitable tile provider before high-volume deployment.

### Automatic map generation on Netlify

The map is generated **during every Netlify deployment**, directly from the
notes and `.base` files in the deployed Git revision. There is no manual marker
export, prebuilt map file to maintain, or running Obsidian instance required on
Netlify. The browser then makes the generated map interactive with Leaflet.

1. Connect this GitHub repository to a Netlify site and select your deployment
   branch (normally `main`). Keep continuous deployment enabled.
2. Use the repository root as the base directory. `netlify.toml` supplies the
   build command (`bundle exec jekyll build --trace`), publish directory
   (`_site`), Ruby/Bundler versions, and production build environment. Remove
   conflicting build settings in Netlify if you previously configured them.
3. Commit and push your exported Obsidian notes, embedded `.base` files, and
   the Jekyll map implementation to that branch. Netlify installs the locked
   dependencies, runs Jekyll (including the map generator), and publishes the
   generated site.
4. Open **Map** on the deployed site. When you add, remove, or move a place in
   Obsidian, commit and push the updated note. The next successful deploy
   regenerates its markers. Changes made only in your local vault do not reach
   Netlify until they are synced to the repository.

For example, changing `coordinates` in `_notes/articles/article-1.md` moves its
marker on the next deployment. Adding another note with valid coordinates adds
a marker automatically; removing its coordinates removes the marker. Changes
to the base's supported center, zoom, and marker property settings are also
applied during that build.

This matches the article's build-time publishing approach using Jekyll's
plugin lifecycle. The linked article uses the older Obsidian Map View plugin;
this repository reads the `.base` configuration used by **Obsidian Maps**.
It does not run the full Obsidian Bases query engine (see limitations above).
Map updates require a new deployment; they are not live-synced from a visitor's
or author's Obsidian application.

The existing GitHub Pages Actions workflow remains an alternative deployment
path. No push or Netlify deployment is performed by these local changes.

Run map integration checks with the project bundle available:

```sh
python3 -m unittest discover -s tests -v
```

The repository's existing front-matter plugin modifies notes lacking front
matter during a build. Run development builds in a temporary copy if you want
to keep those source notes untouched.
