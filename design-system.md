# AN CANDLES — Technical Handover & Architecture Reference

**Target port:** Vanilla HTML5, CSS3, and JavaScript (ES modules)  
**Reference state:** Current project source, audited 2026-09-28  
**Scope:** Visual system, typography, spacing, layout, imagery, animation, and interaction presentation. Business logic, database design, checkout processing, and AI services are outside this visual-porting guide.

---

## 1. Visual Architecture Summary

The AN CANDLES interface is a warm editorial commerce system built from five principles:

1. **Clay-paper field:** a pale blush background replaces pure white.
2. **Cocoa typography:** near-brown text replaces black.
3. **Serif scale contrast:** large, light-weight Fraunces display type sits beside restrained Jost interface text.
4. **Rules instead of cards:** 1px borders and background bands create grouping; rounded, elevated cards are avoided in primary page composition.
5. **Slow motion:** entrances use long ease-out movement; product imagery zooms over 700–1200ms; controls change color over 300–500ms.

The dominant visual sequence is:

```text
full-bleed image / solid color band
    → large serif statement
    → narrow muted copy
    → generous vertical pause
    → asymmetric two-column composition
    → 1px divider rules
    → product or editorial image grid
```

---

# 2. Design System: The “An” Aesthetic

## 2.1 Canonical color palette

The application defines color values in OKLCH. The HEX values below are computed sRGB equivalents, rounded to 8-bit channels. Use the HEX values when the target environment cannot preserve OKLCH; retain OKLCH where supported for the closest source match.

| Semantic role | CSS token | Source OKLCH | sRGB HEX | Usage |
|---|---|---:|---:|---|
| Page background | `--background` | `oklch(0.955 0.014 55)` | `#F8EEE7` | Main page field |
| Soft section surface | `--surface` | `oklch(0.915 0.024 45)` | `#F2DED6` | Alternating bands, image backplates, headers |
| Deep surface | `--surface-deep` | `oklch(0.845 0.031 42)` | `#DFC6BD` | Selection highlight |
| Primary text / primary fill | `--foreground`, `--primary` | `oklch(0.305 0.033 45)` | `#3D2A21` | Headings, body text, dark buttons, overlays |
| Card / popover field | `--card`, `--popover` | `oklch(0.975 0.008 60)` | `#FBF6F1` | Light vessel/customizer surfaces |
| Text on primary | `--primary-foreground` | `oklch(0.965 0.012 60)` | `#FAF2EC` | Hero text and dark-button text |
| Secondary fill | `--secondary` | `oklch(0.915 0.024 45)` | `#F2DED6` | Secondary controls; same as surface |
| Muted fill | `--muted` | `oklch(0.925 0.018 50)` | `#F1E3DC` | Low-emphasis UI |
| Secondary text / focus ring | `--muted-foreground`, `--ring` | `oklch(0.545 0.029 46)` | `#7F6B62` | Descriptions, captions, placeholders |
| Blush accent | `--accent` | `oklch(0.88 0.035 35)` | `#EED0C8` | Lotus-blush selections |
| Botanical sage | `--sage` | `oklch(0.645 0.037 125)` | `#88927A` | Lotus/plant accents and confirmations |
| Ember gold | `--ember` | `oklch(0.72 0.11 62)` | `#D69459` | Warm highlights, step numbers, icons |
| Destructive | `--destructive` | `oklch(0.52 0.16 28)` | `#B33830` | Errors only |
| Hairline border / input line | `--border`, `--input` | `oklch(0.865 0.024 45)` | `#E1CEC6` | Dividers, outlines, field underlines |

**Source:** `src/styles.css:59-92`.

### Full vanilla token sheet

```css
:root {
  /* Brand colors: use OKLCH where supported. */
  --an-background: #f8eee7;
  --an-surface: #f2ded6;
  --an-surface-deep: #dfc6bd;
  --an-foreground: #3d2a21;
  --an-card: #fbf6f1;
  --an-primary: #3d2a21;
  --an-primary-foreground: #faf2ec;
  --an-secondary: #f2ded6;
  --an-muted: #f1e3dc;
  --an-muted-foreground: #7f6b62;
  --an-accent: #eed0c8;
  --an-sage: #88927a;
  --an-ember: #d69459;
  --an-destructive: #b33830;
  --an-border: #e1cec6;
  --an-ring: #7f6b62;

  --an-radius-base: 2px;
  --an-ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --an-container-max: 88rem; /* 1408px at a 16px root */
}
```

### Transparency combinations used in authored screens

Use `color-mix()` or explicit alpha channels in vanilla CSS:

```css
/* Equivalent compositing rules used by the source. */
--primary-25: color-mix(in srgb, var(--an-primary) 25%, transparent);
--primary-30: color-mix(in srgb, var(--an-primary) 30%, transparent);
--primary-35: color-mix(in srgb, var(--an-primary) 35%, transparent);
--primary-40: color-mix(in srgb, var(--an-primary) 40%, transparent);
--primary-45: color-mix(in srgb, var(--an-primary) 45%, transparent);
--background-85: color-mix(in srgb, var(--an-background) 85%, transparent);
--background-90: color-mix(in srgb, var(--an-background) 90%, transparent);
--background-95: color-mix(in srgb, var(--an-background) 95%, transparent);
```

Key instances:

- Hero: flat primary overlay at 25%, then vertical gradient from primary 45% at bottom through transparent to primary 25% at top (`Hero.tsx:18-19`).
- About: primary overlay at 40% (`about.tsx:38`).
- Collection cover and Instagram hover: primary overlay at 35% (`collections.$slug.tsx:41`; `InstagramGrid.tsx:46`).
- Cart backdrop: primary at 30% (`CartDrawer.tsx:15`).
- Scrolled navigation: background at 85% plus medium backdrop blur (`Navbar.tsx:31-33`).

### Candle Lab-only color swatches

These are feature colors, not global brand tokens (`candle-lab.tsx:18-23,57`):

| Swatch | OKLCH | HEX |
|---|---:|---:|
| Lotus | `oklch(0.85 0.06 350)` | `#EDBED3` |
| Sandalwood | `oklch(0.7 0.08 60)` | `#C4936B` |
| Green tea | `oklch(0.8 0.08 130)` | `#ADC992` |
| Cinnamon | `oklch(0.6 0.1 45)` | `#B16C4C` |
| Vanilla | `oklch(0.92 0.05 90)` | `#F1E4BF` |
| Default wax | `oklch(0.95 0.02 80)` | `#F6EDE0` |

### Dark mode status

The `.dark` selector repeats the light `background` and `foreground`; the current product does **not** implement a dark palette (`src/styles.css:95-98`). Do not invent a dark theme in an exact port.

---

## 2.2 Typography

### Font delivery

Load the exact families and axes in `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..500,100;1,9..144,300,100&family=Jost:wght@300;400;500&display=swap">
```

**Source:** `src/routes/__root.tsx:95-102`.

### Families and global rules

```css
:root {
  --font-display: "Fraunces", ui-serif, Georgia, serif;
  --font-body: "Jost", ui-sans-serif, system-ui, sans-serif;
}

body {
  font-family: var(--font-body);
  font-weight: 300;
  letter-spacing: 0.01em;
  color: var(--an-foreground);
  background: var(--an-background);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, blockquote {
  font-family: var(--font-display);
  font-weight: 300;
  letter-spacing: -0.02em;
  font-variation-settings: "SOFT" 100, "WONK" 0;
}
```

**Source:** `src/styles.css:22-23,109-127`.

### Type roles

| Role | Family | Size | Weight | Tracking | Line-height | Transform |
|---|---|---:|---:|---:|---:|---|
| Body default | Jost | inherited / usually 16px | 300 | `0.01em` | browser normal unless overridden | none |
| Body supporting | Jost | 14px | 300 | inherits `0.01em` | `1.625`–`1.9` | none |
| Eyebrow | Jost | 11px (`0.6875rem`) | 400 | `0.22em` | normal | uppercase |
| Navigation | Jost | 12px (`0.75rem`) | 400 | `0.18em` | normal | uppercase |
| Hero brand kicker | Jost | 10px (`0.625rem`) | 300 inherited | `0.32em` | normal | uppercase |
| Hero H1 | Fraunces | 52px mobile / 88px desktop | 300 | `-0.02em` | `0.95` | none |
| Major page H1 | Fraunces | 44–48px mobile / 64–80px desktop | 300 | `-0.02em` | `1.05`–`1.25` | none |
| Major section H2 | Fraunces | 36–40px mobile / 48–60px desktop | 300 | `-0.02em` | `1.1`–`1.25` | none |
| Card/product title | Fraunces via heading selector | 18–30px | 300 | `-0.02em` | `1.25`–`1.375` | none |
| CTA | Jost | 12px | inherited 300 | `0.2em` | normal | uppercase |
| Product/filter UI | Jost | 12px | 300 | `0.15em`–`0.18em` | normal | uppercase |

### Exact recurring line heights

```css
.leading-none    { line-height: 1; }
.leading-tight   { line-height: 1.25; }
.leading-snug    { line-height: 1.375; }
.leading-relaxed { line-height: 1.625; }
.leading-7       { line-height: 1.75rem; } /* 28px */
.leading-8       { line-height: 2rem; }    /* 32px */
.leading-1_9     { line-height: 1.9; }
```

Important intentional exceptions:

- Hero H1: `line-height: .95` (`Hero.tsx:30`).
- About hero: `line-height: 1.05` (`about.tsx:40`).
- Editorial statement headings: `1.1` or `1.15` (`BrandStory.tsx:10`; `MaterialsSection.tsx:21`).
- Long-form brand copy: `line-height: 1.9` (`BrandStory.tsx:18-22`; `about.tsx:53`).

### Tracking rule

The source globally applies `letter-spacing: 0.01em` to body and `-0.02em` to headings. For the requested vanilla reproduction, preserve these exact values even though the current project’s newer design guidance generally discourages negative tracking.

---

## 2.3 Borders, radii, focus, and selection

```css
*, *::before, *::after { box-sizing: border-box; }

/* Default divider */
.rule { border-color: var(--an-border); border-width: 1px; }

/* Radius scale derived from 2px base */
:root {
  --radius-sm: 0px;
  --radius-md: 2px;
  --radius-lg: 4px;
  --radius-xl: 8px;
  --radius-2xl: 12px;
  --radius-3xl: 16px;
  --radius-4xl: 20px;
}

::selection {
  background: var(--an-surface-deep);
  color: var(--an-foreground);
}

:focus-visible {
  outline: 1px solid var(--an-foreground);
  outline-offset: 3px;
}
```

Primary page elements use square corners or 0–2px radius. Circular controls are reserved for recognizable icon actions (wishlist, chat, confirmation mark). The customizer’s illustrated vessel deliberately uses larger radii to model an object rather than a UI card.

**Source:** `src/styles.css:14-20,100-137`.

---

## 2.4 Shadows

No custom shadow palette is authored. The few feature-level shadows use Tailwind v4 defaults verbatim:

```css
--shadow-xs:   0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm:   0 1px 3px 0 rgb(0 0 0 / 0.10),
               0 1px 2px -1px rgb(0 0 0 / 0.10);
--shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.10),
               0 2px 4px -2px rgb(0 0 0 / 0.10);
--shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.10),
               0 4px 6px -4px rgb(0 0 0 / 0.10);
--shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.10),
               0 8px 10px -6px rgb(0 0 0 / 0.10);
--shadow-2xl:  0 25px 50px -12px rgb(0 0 0 / 0.25);
```

Authored use:

- Wishlist circular button: `shadow-sm` (`ProductCard.tsx:61`).
- Chat launcher: `shadow-lg`; chat panel: `shadow-2xl` (`AnCandleChat.tsx:82,92`).
- Customizer vessel illustration: `shadow-xl` (`customize.tsx:64`).
- Main editorial sections and product cards: **no shadow**.

Do not apply shadows to ordinary content sections. Use background contrast and 1px rules first.

---

## 2.5 Core UI primitives

### Solid editorial CTA

```css
.btn-ink {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 1.05rem 2.4rem;
  border: 1px solid var(--an-primary);
  background: var(--an-primary);
  color: var(--an-primary-foreground);
  font: inherit;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  transition: background-color 400ms ease, color 400ms ease;
}
.btn-ink:hover { background: transparent; color: var(--an-primary); }
.btn-ink:disabled { opacity: 0.4; cursor: not-allowed; }
```

### Outline editorial CTA

```css
.btn-outline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 1.05rem 2.4rem;
  border: 1px solid var(--an-foreground);
  background: transparent;
  color: var(--an-foreground);
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  transition: background-color 400ms ease, color 400ms ease;
}
.btn-outline:hover {
  background: var(--an-primary);
  color: var(--an-primary-foreground);
}
```

### Underline field

```css
.field-line {
  width: 100%;
  padding: 0.75rem 0;
  border: 0;
  border-bottom: 1px solid var(--an-border);
  background: transparent;
  color: var(--an-foreground);
  font: inherit;
  font-size: 0.875rem;
  transition: border-color 300ms ease;
}
.field-line::placeholder { color: var(--an-muted-foreground); }
.field-line:focus { outline: 0; border-bottom-color: var(--an-foreground); }
```

**Source:** `src/styles.css:165-234`.

---

# 3. Animation & Motion Guidelines

## 3.1 Signature easing

The primary motion curve is:

```css
cubic-bezier(0.22, 1, 0.36, 1)
```

It is used for scroll reveals, the hero entrance, search overlay, cart drawer, and testimonial transitions. It produces a fast initial response and long soft landing.

---

## 3.2 Scroll reveal / fade-up

Source behavior (`Reveal.tsx:14-20`):

- Initial: `opacity: 0; transform: translateY(18px)`.
- Final: `opacity: 1; transform: translateY(0)`.
- Duration: `900ms`.
- Easing: `cubic-bezier(0.22, 1, 0.36, 1)`.
- Trigger: element enters viewport, with effective viewport margin `-80px`.
- Play count: once.
- Common delays: `0`, `50ms`, `80ms`, `100ms`, `120ms`, `150ms`; product grids repeat `0/80/160/240ms` by row position.

Vanilla implementation:

```css
.reveal {
  opacity: 0;
  transform: translate3d(0, 18px, 0);
  transition:
    opacity 900ms cubic-bezier(0.22, 1, 0.36, 1),
    transform 900ms cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal.is-visible {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}
```

```js
const revealObserver = new IntersectionObserver(
  (entries, observer) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target); // once: true
    }
  },
  { root: null, rootMargin: '-80px 0px', threshold: 0 }
);

document.querySelectorAll('.reveal').forEach((element) => {
  const delay = element.dataset.delay;
  if (delay) element.style.transitionDelay = `${delay}ms`;
  revealObserver.observe(element);
});
```

Example stagger:

```html
<div class="reveal" data-delay="0">…</div>
<div class="reveal" data-delay="80">…</div>
<div class="reveal" data-delay="160">…</div>
<div class="reveal" data-delay="240">…</div>
```

---

## 3.3 Hero entrance

Source: `Hero.tsx:23-27`.

```css
@keyframes hero-enter {
  from { opacity: 0; transform: translate3d(0, 24px, 0); }
  to   { opacity: 1; transform: translate3d(0, 0, 0); }
}
.hero-content {
  animation: hero-enter 1100ms cubic-bezier(0.22, 1, 0.36, 1) both;
}
```

No delay is applied.

---

## 3.4 Autumn leaves and lotus petals

Exact source keyframes (`src/styles.css:251-258`):

```css
@keyframes leaf-fall {
  0% {
    transform: translate3d(0, -10vh, 0) rotate(0deg);
    opacity: 0;
  }
  10% { opacity: 1; }
  50% {
    transform: translate3d(40px, 45vh, 0) rotate(180deg);
  }
  90% { opacity: 0.9; }
  100% {
    transform: translate3d(-30px, 105vh, 0) rotate(360deg);
    opacity: 0;
  }
}

.leaf-fall {
  animation: leaf-fall 16s linear infinite;
  will-change: transform;
}
```

Eight-instance distribution (`FallingLeaves.tsx:1-9`):

| Left | Delay | Duration | Size | Shape/color |
|---:|---:|---:|---:|---|
| 6% | 0s | 14s | 22px | maple / ember |
| 18% | 4s | 17s | 16px | lotus / sage |
| 31% | 8s | 15s | 20px | maple / ember |
| 47% | 2s | 19s | 14px | petal / ember |
| 62% | 6s | 16s | 24px | maple / ember |
| 74% | 10s | 18s | 18px | lotus / sage |
| 86% | 3s | 15s | 16px | petal / ember |
| 94% | 12s | 20s | 20px | maple / ember |

Container rule:

```css
.falling-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.falling-decoration > span { position: absolute; top: -2.5rem; }
```

The source SVG path opacity is `.85` for lotus, `.7` for petals, and `.8` for maple leaves (`FallingLeaves.tsx:15-27`).

---

## 3.5 Product and editorial image hover

### Standard product card

```css
.product-card__image-primary {
  transition: transform 1200ms ease-out;
}
.product-card:hover .product-card__image-primary {
  transform: scale(1.04);
}
.product-card__image-secondary {
  opacity: 0;
  transition: opacity 700ms ease; /* browser CSS ease */
}
.product-card:hover .product-card__image-secondary { opacity: 1; }
.product-card__quick-add {
  opacity: 0;
  transform: translateY(0.75rem); /* 12px */
  transition: all 500ms ease;     /* source uses transition-all */
}
.product-card:hover .product-card__quick-add,
.product-card:focus-within .product-card__quick-add {
  opacity: 1;
  transform: translateY(0);
}
```

**Source:** `ProductCard.tsx:31,39,65`.

### Other image scales

| Context | Duration | Scale | Easing explicitly set? |
|---|---:|---:|---|
| Sale product | 700ms | `1.04` | No; CSS default `ease` |
| Instagram tile | 1200ms | `1.04` | No; CSS default `ease` |
| Collection list image | 1200ms | `1.03` | No; CSS default `ease` |
| Product detail image | 1200ms | `1.06` | No; CSS default `ease` |

**Sources:** `UpcomingSale.tsx:32`; `InstagramGrid.tsx:44`; `collections.index.tsx:48`; `product.$slug.tsx:81`.

---

## 3.6 Overlays and transient panels

### Search overlay

```css
@keyframes search-enter {
  from { opacity: 0; transform: translateY(-12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.search-overlay {
  animation: search-enter 350ms cubic-bezier(0.22, 1, 0.36, 1) both;
}
```

Exit reverses to `opacity:0; translateY(-12px)`. Source: `SearchOverlay.tsx:32-37`.

### Cart drawer

```css
.cart-backdrop { transition: opacity 500ms cubic-bezier(0.22,1,0.36,1); }
.cart-panel {
  transition: transform 500ms cubic-bezier(0.22,1,0.36,1);
  transform: translateX(100%);
}
.cart.is-open .cart-panel { transform: translateX(0); }
```

Source backdrop only specifies opacity states; the motion library supplies its default transition because no explicit backdrop transition is set. The panel explicitly uses 500ms and the signature curve (`CartDrawer.tsx:14-29`). For deterministic vanilla output, use 500ms for both.

### Mobile menu

Full-screen opacity transition only: `0 → 1 → 0`, duration `300ms`; no custom easing (`Navbar.tsx:85-93`).

### Chat panel

States (`AnCandleChat.tsx:76-82`):

```text
enter from: opacity 0; translateY(18px); scale(.98)
open:       opacity 1; translateY(0);    scale(1)
exit to:    opacity 0; translateY(12px); scale(.98)
```

No explicit duration/easing is supplied in source, so the motion library default transition applies. For an exact dependency-free port, either use a spring approximation or set a deterministic CSS approximation:

```css
.chat-panel {
  transform-origin: bottom right;
  transition: opacity 300ms ease, transform 300ms cubic-bezier(0.22,1,0.36,1);
}
```

The 300ms approximation is a porting choice, not a source-authored value.

### Testimonials

- Auto-advance interval: `6000ms`.
- Enter: `opacity 0`, `translateY(12px)` → visible.
- Exit: `opacity 0`, `translateY(-12px)`.
- Duration: `600ms`.
- Easing: signature curve.
- Sequencing: wait for exit before entering next item.

Source: `Testimonials.tsx:13-15,24-31`.

---

## 3.7 Interaction transitions

| Interaction | Exact transition |
|---|---|
| Navigation link fade | `opacity 300ms ease`; hover opacity `.55` |
| Solid/outline CTA | `background-color 400ms ease, color 400ms ease` |
| Hero/quote image-overlay CTA | `color/background-color 500ms ease` |
| Form underline | `border-color 300ms ease` |
| Sticky header state | `all 500ms ease` (Tailwind default timing) |
| Accordion chevron | `transform 200ms ease` |
| Filter inactive hover | transition opacity; hover `.6` |
| Scent family title | transition opacity; hover `.6` |
| Instagram overlay | opacity `500ms ease` |

---

## 3.8 Reduced motion

The source explicitly hides falling leaves for `prefers-reduced-motion: reduce`; extend the same policy to all nonessential motion in the vanilla port:

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .falling-decoration { display: none; }
  .reveal,
  .hero-content,
  .product-card__image-primary,
  .product-card__image-secondary,
  .product-card__quick-add,
  .search-overlay,
  .cart-panel,
  .chat-panel {
    animation: none !important;
    transition-duration: 0.01ms !important;
    transform: none !important;
  }
  .reveal { opacity: 1; }
}
```

---

# 4. Layout & Structure Principles

## 4.1 Breakpoints

The authored screens use Tailwind defaults:

```css
/* mobile-first */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

No custom breakpoint configuration is present.

---

## 4.2 Editorial container

Exact source (`styles.css:236-249`):

```css
.container-editorial {
  width: 100%;
  max-width: 88rem;       /* 1408px */
  margin-inline: auto;
  padding-inline: 1.5rem; /* 24px */
}
@media (min-width: 768px) {
  .container-editorial { padding-inline: 3rem; } /* 48px */
}
@media (min-width: 1280px) {
  .container-editorial { padding-inline: 4.5rem; } /* 72px */
}
```

The content width inside the 1408px shell is therefore:

- Under 768px: viewport minus 48px.
- 768–1279px: viewport minus 96px.
- 1280–1407px: viewport minus 144px.
- At 1408px and above: container remains 1408px including its internal padding, giving a maximum inner width of 1264px.

---

## 4.3 Vertical rhythm

The site uses large sectional pauses rather than card padding. Core recurring values:

| Pattern | Mobile | Desktop |
|---|---:|---:|
| Main editorial section | `py-32` = 128px | `py-44` = 176px |
| Secondary feature band | `py-28` = 112px | `py-40` = 160px |
| Compact feature band | `py-24` = 96px | `py-32` = 128px |
| Standard route top | `pt-20` = 80px | usually unchanged |
| Standard route bottom | `pb-32` = 128px | usually unchanged |
| Repeated section separation | `mt-32` = 128px | unchanged |
| Major internal block gap | `mt-16` = 64px | unchanged |
| Two-column gap | `gap-16` = 64px | `gap-24` = 96px |
| Product vertical gap | `gap-y-14` = 56px | unchanged |

Representative sources: `BrandStory.tsx:7`; `ExperienceHighlights.tsx:10`; `MaterialsSection.tsx:6`; `index.tsx:49,72,105`; `product.$slug.tsx:73,224,232`.

### Spacing rule

Use large outer spacing and relatively compact internal text spacing:

```text
section edge → heading group: 112–176px outer padding
kicker → heading: 16–24px
heading → paragraph: 20–32px
paragraph → CTA/content list: 32–48px
major media → next block: 64–80px
```

---

## 4.4 Grid grammar and asymmetry

### Editorial split

```css
.editorial-split {
  display: grid;
  gap: 4rem; /* 64px */
}
@media (min-width: 768px) {
  .editorial-split {
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 6rem; /* 96px */
  }
}
```

Variants:

- Brand story: `1.3fr 1fr` (`BrandStory.tsx:8`).
- About chapter: `1fr 1.6fr` (`about.tsx:51`).
- Product detail: `1.1fr 1fr` (`product.$slug.tsx:73`).
- Checkout: `1.4fr 1fr` (`checkout.tsx:153`).
- Cart: `1.6fr 1fr` (`cart.tsx:33`).
- Upcoming sale: `0.7fr 1.3fr` (`UpcomingSale.tsx:17`).
- Workshop hero: `1.05fr .95fr` (`workshop.tsx:53`).
- Customizer: `.9fr 1.1fr` at 1280px (`customize.tsx:60`).

These ratios intentionally prevent visual symmetry. Copy is usually narrower than the available column via `max-width: 28rem` or `32rem`, preserving blank space.

### Alternating collection rows

Two equal columns at ≥768px; reverse the image to column two for odd-indexed rows. Keep `gap: 5rem` (80px) and separate rows by `6rem` (96px) (`collections.index.tsx:35-41`).

### Product grid

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: 1.5rem; /* 24px */
  row-gap: 3.5rem;    /* 56px */
}
@media (min-width: 768px) {
  .product-grid { column-gap: 2rem; } /* 32px */
}
@media (min-width: 1024px) {
  .product-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
```

Source: `ProductGrid.tsx:11`.

### Hairline grid

To create 1px dividers without nested card borders:

```css
.hairline-grid {
  display: grid;
  gap: 1px;
  background: var(--an-border);
}
.hairline-grid > * {
  background: var(--an-background);
}
```

Used for the “An” pillars, workshop metadata, and paired experience blocks (`AnMeaning.tsx:29-39`; `workshop.tsx:59-63`; `ExperienceHighlights.tsx:20-44`).

---

## 4.5 Borderless floating-text effect

The project does not put primary statements in conventional cards. The effect is achieved by:

1. A full-width page or color band.
2. A constrained editorial container.
3. Text blocks with `max-width` but no background, border, radius, or shadow.
4. Large section padding around those blocks.
5. Structural 1px rules only at transitions or list boundaries.
6. Images either full-bleed or aligned directly to the grid, not wrapped in ornamental frames.

Canonical structure:

```html
<section class="section-band">
  <div class="container-editorial editorial-split">
    <div class="reveal statement">
      <p class="eyebrow">The collection</p>
      <h2>Scents created to become part<br>of your everyday rituals.</h2>
    </div>
    <div class="reveal prose" data-delay="120">…</div>
  </div>
</section>
```

```css
.section-band { padding-block: 8rem; }
.statement { max-width: 40rem; }
.prose { max-width: 28rem; color: var(--an-muted-foreground); line-height: 1.9; }
```

Avoid:

```css
/* Not part of the primary AN aesthetic */
background: white;
border-radius: 16px;
box-shadow: 0 10px 30px rgba(...);
padding: 32px;
```

Exceptions are functional overlays/forms: chatbot panel, workshop form, and menus.

---

## 4.6 Full-bleed hero rules

Home hero (`Hero.tsx:10-40`):

```css
.home-hero {
  position: relative;
  width: 100%;
  height: 92vh;
  min-height: 620px;
  margin-top: -5rem; /* -80px; pulls behind 80px nav */
  overflow: hidden;
}
.home-hero > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.home-hero__content {
  position: relative;
  display: flex;
  height: 100%;
  flex-direction: column;
  justify-content: flex-end;
  padding-bottom: 6rem; /* 96px */
}
@media (min-width: 768px) {
  .home-hero__content { justify-content: center; padding-bottom: 0; }
}
```

Other cover heights:

- About cover: `70vh`, minimum `460px` (`about.tsx:32`).
- Collection cover: `60vh`, minimum `420px` (`collections.$slug.tsx:35`).
- Quote image band: `80vh`, minimum `520px` (`QuoteSection.tsx:6`).

---

## 4.7 Navigation and layering

- Announcement bar precedes navigation.
- Main nav height: `80px` (`h-20`).
- Navigation is sticky at `top:0`, `z-index:40`.
- Scroll state activates after `window.scrollY > 24px`.
- Scrolled state: 1px bottom border, 85% background, `backdrop-filter: blur(12px)` (Tailwind `backdrop-blur-md`), 500ms transition.
- Modal/search/cart layers: `z-index:50`.
- Floating chat: `z-index:60`.
- Mobile menu is full viewport and appears below the same `z-index:50` layer.

Source: `Navbar.tsx:19-35,85-100`; `CartDrawer.tsx:15,25`; `SearchOverlay.tsx:33`; `AnCandleChat.tsx:73`.

---

# 5. Asset Specifications

## 5.1 Bundled raster inventory

The filesystem reports the following encoded dimensions:

| Asset group | Encoded dimensions | Nominal ratio | Treatment |
|---|---:|---:|---|
| `hero.jpg` | 1920×1200 | 8:5 / 1.6 | Full-bleed cover |
| `atmosphere.jpg` | 1920×1088 | 30:17 / 1.765 | Full-bleed cover; often visually treated as 16:9 |
| `care.jpg` | 1408×1008 | 88:63 / 1.397 | Cropped to 4:3 |
| `craft.jpg` | 1408×1008 | 88:63 / 1.397 | Cropped to 16:9 or used in about |
| `ritual.jpg` | 1408×1008 | 88:63 / 1.397 | Cropped to 4:5 |
| `materials.jpg` | 1408×1200 | 88:75 / 1.173 | Natural width in scent section |
| Six original product JPGs | 1024×1280 | 4:5 | Product/card cover |
| Ten HD collection/product files | 928×1152 | 29:36 / 0.806 | Cropped to 4:5 |

The HD files use PNG encoding despite `.jpg` filenames; preserve browser compatibility, but normalize extensions/encoding during a clean port if desired.

Remote `.asset.json` logo/image pointers are resolved by the current asset pipeline and do not expose intrinsic dimensions in the JSX. Treat them as scalable branding resources where width is controlled and height remains automatic.

---

## 5.2 Aspect-ratio catalog

| Ratio | CSS | Where used |
|---:|---|---|
| 4:5 portrait | `aspect-ratio: 4 / 5; object-fit: cover;` | Product cards, product detail, thumbnails, workshop image, materials section |
| 4:3 landscape | `aspect-ratio: 4 / 3; object-fit: cover;` | Candle-care images, home care image, collection listing |
| 16:9 landscape | `aspect-ratio: 16 / 9; object-fit: cover;` | Craftsmanship banner, about studio image |
| 16:10 landscape | `aspect-ratio: 16 / 10; object-fit: cover;` | Workshop feature card on home |
| 1:1 square | `aspect-ratio: 1; object-fit: cover;` | Instagram tiles; customizer preview shell |
| Full viewport cover | width/height `100%`; `object-fit:cover` | Hero, about hero, collection hero, quote band |
| Fixed thumbnail 4:5 | 80×96, 64×80, 80×112, 128×160 | Search, checkout, drawer, cart |

Unless otherwise noted, no custom `object-position` is applied; the browser default `50% 50%` center crop is used.

---

## 5.3 Image CSS recipes

### Product image

```css
.media-product {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  object-position: 50% 50%;
}
```

### Full-bleed cover

```css
.media-cover {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 50%;
}
```

### Editorial landscape

```css
.media-landscape-4x3 { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
.media-landscape-16x9 { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
```

### Product logo watermark

```css
.product-media { position: relative; overflow: hidden; }
.product-watermark {
  position: absolute;
  left: 1rem;
  bottom: 1rem;
  width: 2.5rem; /* 40px on cards */
  opacity: 0.8;
  mix-blend-mode: multiply;
  pointer-events: none;
}
.product-detail .product-watermark {
  left: 1.25rem;
  bottom: 1.25rem;
  width: 3.5rem; /* 56px */
}
```

Source: `ProductCard.tsx:47-52`; `product.$slug.tsx:83-88`.

---

## 5.4 Loading rules

- Hero and route-cover images: eager/default loading because they are first-viewport content.
- Product listing, editorial images below the fold, thumbnails, footer logo, and Instagram tiles: `loading="lazy"`.
- Product images declare source dimensions `width="1024" height="1280"` even where some generated files are 928×1152; CSS `aspect-ratio:4/5` stabilizes layout.
- Hero declares `1920×1200`; quote declares `1920×1088`; craft/care/ritual images typically declare `1408×1008`.
- Global image rule: `image-rendering:auto`; no sharpening filter is applied (`styles.css:259`).

---

# 6. Page Composition Map

## 6.1 Global shell

```text
Announcement bar
Sticky 80px navigation
<main>
  Route content
</main>
Footer (128px top separation)
Cart drawer overlay
Search overlay
Floating chat control/panel
```

Provider/state technology is irrelevant to the visual port. Preserve this DOM stacking order and z-index hierarchy.

## 6.2 Home page sequence

Current order (`src/routes/index.tsx:43-107`):

```text
1. Full-bleed hero + falling leaves
2. Brand story split statement
3. “An” meaning band + three hairline-grid pillars + falling leaves
4. Workshop/customizer experience pair
5. Featured product heading + 4-column product grid
6. Scent editorial split band
7. Craftsmanship statement + 16:9 image + four ruled steps
8. Full-bleed quote image band
9. Materials editorial split band
10. Candle-care split section
11. Rotating testimonials
12. Six-tile Instagram grid
13. Centered newsletter
14. Footer
```

## 6.3 Commerce patterns

- Shop: title → full-width upcoming-sale band → border-y filters → product grid.
- Product: breadcrumb → 1.1/1 image/detail split → related products → recently viewed.
- Collections index: intro → alternating 4:3 image/text rows.
- Collection detail: 60vh cover → centered description → product grid.
- Cart/checkout: asymmetric utility grids with rules and no decorative cards.

## 6.4 Experience patterns

- Workshop: 1.05/.95 intro split → surface band with experience list + bordered form → centered social CTA.
- Customizer: square visual preview + option workflow in `.9/1.1` grid.
- Candle Lab: four-step rule indicator → two-column illustration/game controls.

---

# 7. Vanilla HTML/CSS/JS Porting Blueprint

## 7.1 Recommended file structure

```text
/
├── index.html
├── shop.html
├── product.html
├── collections.html
├── about.html
├── workshop.html
├── customize.html
├── candle-lab.html
├── assets/
│   ├── images/
│   ├── logos/
│   └── icons/
├── css/
│   ├── tokens.css
│   ├── base.css
│   ├── layout.css
│   ├── components.css
│   ├── motion.css
│   └── pages.css
└── js/
    ├── app.js
    ├── reveal.js
    ├── navigation.js
    ├── overlays.js
    ├── carousel.js
    └── candle-lab.js
```

## 7.2 Required base reset

```css
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
html, body { margin: 0; min-height: 100%; }
body { overflow-x: hidden; }
img { display: block; max-width: 100%; image-rendering: auto; }
a { color: inherit; text-decoration: none; }
button, input, select, textarea { font: inherit; color: inherit; }
button { border: 0; padding: 0; background: none; cursor: pointer; }
```

## 7.3 Reusable section skeleton

```html
<section class="section section--surface">
  <div class="container-editorial editorial-split">
    <figure class="reveal media-frame">
      <img class="media-product" src="assets/images/example.jpg" alt="">
    </figure>
    <div class="reveal copy-column" data-delay="120">
      <p class="eyebrow">Materials</p>
      <h2 class="section-title">What goes into<br>every candle</h2>
      <p class="body-muted">…</p>
    </div>
  </div>
</section>
```

```css
.section { padding-block: 8rem; }
.section--surface { background: var(--an-surface); }
.section-title {
  margin: 1.5rem 0 0;
  font-size: 2.25rem;
  line-height: 1.15;
}
.body-muted {
  max-width: 28rem;
  margin-top: 2rem;
  color: var(--an-muted-foreground);
  line-height: 1.9;
}
@media (min-width: 768px) {
  .section { padding-block: 11rem; }
  .section-title { font-size: 3rem; }
}
```

## 7.4 Sticky navigation script

```js
const header = document.querySelector('[data-site-header]');
const syncHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 24);
syncHeader();
window.addEventListener('scroll', syncHeader, { passive: true });
```

```css
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  transition: all 500ms ease;
}
.site-header.is-scrolled {
  border-bottom: 1px solid var(--an-border);
  background: color-mix(in srgb, var(--an-background) 85%, transparent);
  backdrop-filter: blur(12px);
}
.site-nav { height: 5rem; }
```

## 7.5 Overlay state pattern

```js
function setOverlay(name, open) {
  const overlay = document.querySelector(`[data-overlay="${name}"]`);
  if (!overlay) return;
  overlay.hidden = false;
  requestAnimationFrame(() => overlay.classList.toggle('is-open', open));
  document.documentElement.classList.toggle('has-overlay', open);
  if (!open) {
    overlay.addEventListener('transitionend', () => { overlay.hidden = true; }, { once: true });
  }
}
```

For production, add focus trapping, Escape-key close, return focus, and `aria-modal="true"`.

---

# 8. Fidelity Rules and Known Exceptions

1. **Do not substitute pure white or black.** Use `#F8EEE7` and `#3D2A21`.
2. **Do not convert primary page sections into elevated cards.** Preserve unframed text and large blank areas.
3. **Do not use bold display headings.** Fraunces remains weight 300 with SOFT 100.
4. **Do not reduce desktop gutters below 48px or the 1280px+ gutter below 72px.**
5. **Do not add rounded corners globally.** The base radius is 2px; primary CTAs are square.
6. **Keep imagery centered with `object-fit:cover` unless a future art direction defines a focal point.** No custom object-position currently exists.
7. **Keep motion slow and shallow.** Standard reveal travel is only 18px; hero travel is 24px.
8. **Preserve the signature cubic-bezier.** `cubic-bezier(0.22,1,0.36,1)` is the primary motion identity.
9. **Dark mode is not implemented.** Do not infer one from the presence of a `.dark` selector.
10. **Generic component-library styles are not brand direction.** Rounded menus, default shadows, and Radix transition helpers are implementation defaults, not the primary AN CANDLES aesthetic.
11. **Chat entrance timing is unspecified by the source.** Its state values are exact, but any fixed CSS duration is an approximation of the motion library’s default.
12. **Similar image zooms intentionally/accidentally vary between 700ms and 1200ms.** Preserve per-context timings for an exact port; standardize only as a deliberate redesign.

---

# 9. Source Reference Index

| Topic | Primary source |
|---|---|
| Tokens, typography, UI utilities, container, leaf keyframes | `src/styles.css:13-259` |
| Font stylesheet loading | `src/routes/__root.tsx:75-105` |
| Scroll reveal | `src/components/Reveal.tsx:4-23` |
| Hero composition and motion | `src/components/home/Hero.tsx:7-47` |
| Falling decoration instances and SVG shapes | `src/components/FallingLeaves.tsx:1-47` |
| Product hover and watermark | `src/components/ProductCard.tsx:16-82` |
| Product-detail media | `src/routes/product.$slug.tsx:73-105` |
| Sticky navigation and mobile menu | `src/components/Navbar.tsx:19-133` |
| Cart drawer motion | `src/components/CartDrawer.tsx:11-115` |
| Search overlay motion | `src/components/SearchOverlay.tsx:29-90` |
| Chat panel motion and geometry | `src/components/AnCandleChat.tsx:66-95` |
| Testimonial timing | `src/components/home/Testimonials.tsx:10-50` |
| “An” meaning hairline grid | `src/components/home/AnMeaning.tsx:13-41` |
| Experience asymmetric cards | `src/components/home/ExperienceHighlights.tsx:10-48` |
| Product-grid dimensions | `src/components/ProductGrid.tsx:5-18` |
| Editorial split examples | `BrandStory.tsx`, `ScentSection.tsx`, `MaterialsSection.tsx`, `Craftsmanship.tsx` |
| Collection alternating rows | `src/routes/collections.index.tsx:21-74` |
| Full-bleed collection cover | `src/routes/collections.$slug.tsx:29-62` |
| Workshop layout/form | `src/routes/workshop.tsx:51-103` |
| Candle Lab swatches/layout | `src/routes/candle-lab.tsx:18-128` |

---

## Final implementation baseline

For maximum fidelity, begin the vanilla rebuild by copying Sections **2.1**, **2.2**, **2.5**, **3.2**, **3.3**, **3.4**, **4.2**, and **7.2** directly into the CSS architecture. Build every page from the `container-editorial`, full-width bands, asymmetric grids, and fixed image ratios before adding interactive scripts. Motion should be added last, after the static composition matches at the 640px, 768px, 1024px, and 1280px breakpoints.
