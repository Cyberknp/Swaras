1. Frontend UI development prompt

PROJECT: Swaras — ML-Powered Indian Classical Music Web App
STACK: React + TypeScript + Tailwind CSS (Vite) | Single-Page Application

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPT & AESTHETIC DIRECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Swaras is a Python/ML-powered Android app that generates authentic
Hindusthani swara sequences (Sapthaka form) — bridging ancient raga
tradition with modern machine learning.

Aesthetic: "Sacred Geometry meets Digital Minimalism"
  - Color palette: deep saffron (#FF6B2B), ivory (#FAF3E0), gold (#D4AF37),
    midnight indigo (#1A1040), rose (#C2185B) — rich but never garish
  - Typography: Cormorant Garamond (headings, elegant serif with classical
    weight), DM Sans (body, clean modern contrast)
  - Textures: subtle aged-manuscript grain, tanpura woodgrain on sections,
    faint mandala/rangoli geometric SVG overlays (opacity 3–6%)
  - Motion: smooth 60fps, staggered fade-up reveals on scroll, fluid swara
    note animations, no jarring transitions
  - Feel: a museum-quality digital exhibit — reverent, poetic, modern

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECTURE — COMPONENT BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build these components in order. Each is self-contained with its own
types, props, and internal state where needed.

1. <Navbar />
   - Sticky, glassmorphism background (backdrop-blur, semi-transparent)
   - Logo: Unicode "𝄞" or custom SVG + "Swaras" in Cormorant Garamond
   - Nav links: Features | Demo | How It Works | About | GitHub
   - CTA button: "Try Now" → scrolls to Demo
   - Dark/Light mode toggle (sun/moon icon, persisted to localStorage)
   - Mobile: hamburger menu with slide-in drawer

2. <Hero />
   - Full-viewport-height
   - Headline (large, ~80px): "Where Raga Meets Algorithm"
   - Subheadline: "Swaras uses machine learning to generate authentic
     Hindusthani swara sequences — a digital canvas for the classical soul."
   - Two CTAs: [▶ Generate Swaras] (primary, gold) + [View on GitHub] (ghost)
   - Background: animated SVG tanpura silhouette (subtle parallax), floating
     swara syllable particles (Sa Re Ga Ma Pa Dha Ni) drifting upward slowly
   - Faint mandala SVG, centered, rotating at 0.5rpm behind content
   - Bottom: gentle wave/border transition into next section

3. <Features />
   - Section title: "Crafted for the Classical Spirit"
   - 6 feature cards in a 3×2 responsive grid, each with:
     → Custom SVG icon (no emoji, no stock icons — design these)
     → Bold short title
     → 2-sentence evocative description
   - Cards: "ML-Powered Composition", "Authentic Raga Grammar",
     "Sapthaka Notation", "For Artists & Learners", "Open Source",
     "Android Native"
   - Card hover: lift shadow + gold left-border reveal animation
   - Staggered animation-delay on scroll entry (0ms, 100ms, 200ms...)

4. <Demo />
   - Section title: "Listen to the Algorithm Dream in Ragas"
   - Left panel — Controls:
     → Raga selector: dropdown with 8 ragas
       (Yaman, Bhairav, Bhimpalasi, Todi, Darbari, Kafi, Bhupali, Shivaranjani)
     → Sapthaka range: radio/toggle (Mandra | Madhya | Taar)
     → Sequence length: slider (4–16 notes, labeled)
     → Tempo: slider (Vilambit | Madhya | Drut) — slow/medium/fast
     → [✦ Generate Sequence] button (gold, animated shimmer on hover)
   - Right panel — Visualization:
     → On generate: animate 8–16 swara note cards flowing left-to-right
     → Each note card: large Devanagari syllable (सा रे ग म प ध नि) +
       Roman label (Sa, Re, Ga...) + subtle frequency badge
     → Notes pulse/glow in sequence order with timing based on tempo
     → Below: horizontal animated "staff" — SVG line with note circles
       bouncing along it in sequence (like a raga arpeggio visualization)
     → [▶ Play] button triggers CSS-keyframe sequential highlight of notes
   - Placeholder data: hardcode 5–6 raga sequence objects; simulate
     "generation" with a 1.2s loading shimmer then reveal
   - Visual separator: decorative SVG divider (lotus or geometric)

5. <HowItWorks />
   - Section title: "The Science Behind the Song"
   - 4-step horizontal (desktop) / vertical (mobile) infographic:
     Step 1 → "Raga Grammar Encoded" (dataset of classical compositions)
     Step 2 → "ML Model Trained" (sequence learning on swara patterns)
     Step 3 → "Parameters Selected" (user chooses raga, range, tempo)
     Step 4 → "Sequence Generated" (model outputs authentic swara path)
   - Each step: numbered circle (gold), icon, title, 1-sentence explanation
   - Connecting arrows/lines between steps (SVG, animated draw-on-scroll)
   - Note: "No music theory expertise required — the model handles grammar"

6. <WhySwaras />
   - Section title: "A Love Letter to the Classical Tradition"
   - Full-width section, warmer background (saffron tint or deep indigo)
   - 2-column layout: left = poetic paragraph copy about Indian classical
     heritage, the guru-shishya parampara, and digital preservation;
     right = large decorative SVG (tanpura, or stylized raga wheel)
   - Pull quote (large italic): "Every raga is a universe — Swaras lets
     you explore it at the speed of thought."
   - Subtle background texture: aged manuscript / handwritten notation

7. <Contributors />
   - Section title: "The Minds Behind the Music"
   - Responsive card grid (3 cols desktop, 1 col mobile)
   - Each card: avatar (placeholder initials-based colored circle),
     name, role (e.g., "ML Engineer", "Classical Music Advisor"),
     GitHub handle with link icon
   - 3 placeholder contributors — design cards to be elegant, not generic
   - Optional: "Want to contribute?" CTA linking to GitHub Issues

8. <Footer />
   - Dark background (midnight indigo)
   - Logo + tagline left
   - Nav links center
   - Social icons right: GitHub, Twitter/X, Instagram, Email
   - Bottom bar: "© 2025 Swaras Project · Built with ♩ and Python"
   - Hidden Easter egg: clicking the "ॐ" glyph (placed subtly in footer)
     triggers a full-screen ripple animation + soft "Om" chime sound
     (use the Web Audio API — 136Hz drone, 3 seconds, gentle fade)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEMING & DESIGN TOKENS (implement as Tailwind config + CSS vars)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

:root {
  --swaras-saffron: #FF6B2B;
  --swaras-gold: #D4AF37;
  --swaras-ivory: #FAF3E0;
  --swaras-indigo: #1A1040;
  --swaras-rose: #C2185B;
  --swaras-muted: #8B7355;
  --font-display: 'Cormorant Garamond', serif;
  --font-body: 'DM Sans', sans-serif;
}

Dark mode: invert ivory↔indigo, keep gold/saffron accents, darken cards.
Implement via Tailwind's `dark:` classes + class-based toggle on <html>.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLACEHOLDER DATA (define in /src/data/swaras.ts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export const RAGAS = [
  { id: 'yaman', name: 'Yaman', mood: 'Serene, devotional', time: 'Evening',
    sequence: ['Sa', 'Re', 'Ga', 'Ma#', 'Pa', 'Dha', 'Ni', 'Sa\''] },
  { id: 'bhairav', name: 'Bhairav', mood: 'Solemn, meditative', time: 'Dawn',
    sequence: ['Sa', 'Re♭', 'Ga', 'Ma', 'Pa', 'Dha♭', 'Ni', 'Sa\''] },
  { id: 'bhimpalasi', name: 'Bhimpalasi', mood: 'Longing, tender', time: 'Afternoon',
    sequence: ['Sa', 'Re', 'Ga♭', 'Ma', 'Pa', 'Dha', 'Ni♭', 'Sa\''] },
  // ... add 5 more ragas
];

export const SAPTHAKA = { MANDRA: 'mandra', MADHYA: 'madhya', TAAR: 'taar' };
export const DEVANAGARI_MAP = {
  Sa: 'सा', Re: 'रे', Ga: 'ग', Ma: 'म', Pa: 'प', Dha: 'ध', Ni: 'नि'
};

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCESSIBILITY & RESPONSIVE REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- WCAG AA contrast on all text/background combos
- All interactive elements: visible focus ring (gold outline)
- ARIA labels on icon-only buttons, sliders, and the visualizer region
- Smooth scroll behavior (CSS scroll-behavior: smooth)
- Breakpoints: mobile (< 640px), tablet (640–1024px), desktop (> 1024px)
- No horizontal overflow on any viewport
- Prefers-reduced-motion: disable parallax + particle animations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

src/
├── components/
│   ├── Navbar.tsx
│   ├── Hero.tsx
│   ├── Features.tsx
│   ├── Demo/
│   │   ├── Demo.tsx
│   │   ├── Controls.tsx
│   │   └── Visualizer.tsx
│   ├── HowItWorks.tsx
│   ├── WhySwaras.tsx
│   ├── Contributors.tsx
│   └── Footer.tsx
├── data/
│   └── swaras.ts
├── hooks/
│   ├── useDarkMode.ts
│   └── useScrollReveal.ts
├── types/
│   └── index.ts
├── App.tsx
└── main.tsx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY BAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ No placeholder Lorem Ipsum — all copy must be poetic, raga-themed
✓ No stock icon libraries — design SVG icons inline for the 6 features
✓ No generic purple-gradient AI aesthetics
✓ The Demo visualizer MUST animate — static output is not acceptable
✓ Easter egg (ॐ → Om sound) must be implemented, not mentioned
✓ All components must TypeScript-strict (no `any`)
✓ tailwind.config.ts must extend theme with all custom tokens above
✓ Google Fonts import in index.html: Cormorant Garamond + DM Sans
✓ README.md: setup instructions + screenshot placeholder
