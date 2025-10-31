# Literattus CSS Design System Documentation

This document catalogs all CSS components, patterns, and best practices for the Literattus frontend. All styles are defined in `frontend/static/css/main.css`.

---

## 🎨 Color Palette

### CSS Variables (`:root`)
```css
--primary-blue: #1e40af       /* Primary brand color */
--primary-dark: #1e3a8a       /* Darker blue for emphasis */
--accent-orange: #ff6b4a      /* Secondary action color */
--accent-cyan: #06b6d4        /* Information/discovery accent */
--accent-gold: #fbbf24        /* Achievement/reward accent */
--accent-purple: #a855f7      /* Creative/special accent */
--text-primary: #1f2937       /* Main text color */
--text-secondary: #6b7280     /* Secondary text */
--bg-light: #f9fafb          /* Light background */
--border-radius: 12px        /* Consistent border radius */
```

### Usage Guidelines

**Primary Blue (`#1e40af`):**
- Main CTAs and primary buttons
- Navigation active states
- Progress indicators
- Trust/authority elements

**Accent Orange (`#ff6b4a`):**
- Secondary actions
- Attention-grabbing elements
- Club/community features
- Warm, inviting CTAs

**Accent Cyan (`#06b6d4`):**
- Discovery features
- Information highlights
- Cool, refreshing accents
- Recommendations

**Accent Gold (`#fbbf24`):**
- Achievements and milestones
- Premium features
- Star ratings
- Decorative accents

**Accent Purple (`#a855f7`):**
- Creative features
- Special events
- Reading challenges
- Unique highlights

---

## 📦 Component Classes

### 1. Navigation

#### `.nav-link`
Base navigation link with hover effects.
```css
.nav-link {
    position: relative;
    color: var(--text-secondary);
    font-weight: 500;
    transition: all 0.3s ease;
}
```

**Usage:**
```html
<a href="#" class="nav-link px-4 py-2 rounded-lg">
    <i class="fas fa-home mr-1"></i> Home
</a>
```

#### `.nav-link-active`
Active state for current page navigation.
```css
.nav-link-active {
    color: var(--primary-blue) !important;
    background-color: rgba(30, 64, 175, 0.1) !important;
}
```
- Includes gradient underline effect
- Use for current page indicator

---

### 2. Buttons

#### `.btn-primary`
Primary action button with blue gradient.
```css
.btn-primary {
    background: linear-gradient(135deg, var(--primary-blue), #0ea5e9);
    color: white;
    font-weight: 600;
    /* Includes hover lift effect and ripple animation */
}
```

**Usage:**
```html
<button class="btn-primary px-8 py-4 rounded-lg">
    <i class="fas fa-rocket mr-2"></i> Get Started
</button>
```

**Features:**
- Hover: Translates up 2px with shadow
- Active: Returns to normal position
- Ripple effect on hover (white overlay)

#### `.btn-secondary`
Secondary action button with orange gradient.
```css
.btn-secondary {
    background: linear-gradient(135deg, var(--accent-orange), #ff8a65);
    color: white;
    /* Similar hover effects to primary */
}
```

#### `.btn-outline`
Outlined button for tertiary actions.
```css
.btn-outline {
    background: transparent;
    color: var(--primary-blue);
    border: 2px solid var(--primary-blue);
}
```

**When to Use:**
- **Primary:** Main call-to-action (1 per section)
- **Secondary:** Supporting actions, less critical
- **Outline:** Tertiary actions, cancel buttons, less emphasis

---

### 3. Cards

#### `.card`
Base card component with hover effects.
```css
.card {
    background: white;
    border-radius: var(--border-radius);
    border: 1px solid #e5e7eb;
    /* Includes gradient top border on hover */
}
```

**Features:**
- Subtle shadow that lifts on hover
- Gradient top border appears on hover
- Smooth transitions (0.3s)

**Usage:**
```html
<div class="card p-6">
    <h3>Card Title</h3>
    <p>Card content...</p>
</div>
```

#### `.dashboard-card`
Enhanced card for dashboard layouts.
```css
.dashboard-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
```

**Features:**
- Larger border radius (16px vs 12px)
- More prominent shadow
- Lifts 6px on hover
- Designed for data display

#### `.dashboard-card-accent`
Adds colored left border to dashboard cards.
```css
.dashboard-card-accent {
    border-left: 5px solid;
}
```

**Variants:**
- `.accent-blue` - Blue left border
- `.accent-orange` - Orange left border
- `.accent-cyan` - Cyan left border

**Usage:**
```html
<div class="dashboard-card dashboard-card-accent accent-blue">
    <!-- Content -->
</div>
```

#### `.feature-card`
Card optimized for feature displays.
```css
.feature-card {
    padding: 32px 24px;
    text-align: center;
}
```

**Typical Structure:**
```html
<div class="card feature-card">
    <span class="feature-icon">📚</span>
    <h3 class="feature-title">Feature Name</h3>
    <p class="feature-description">Description text...</p>
</div>
```

#### `.book-card`
Specialized card for book displays.
```css
.book-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    /* Includes scale-up and shadow on hover */
}
```

**Features:**
- Hover: Translates up 8px and scales to 1.02
- Dramatic shadow increase
- Optimized for vertical book layout

---

### 4. Hero Sections

#### `.hero-section`
Full-width hero with gradient background.
```css
.hero-section {
    background: linear-gradient(135deg, #1e40af 0%, #0ea5e9 50%, #06b6d4 100%);
    color: white;
    padding: 80px 20px;
    border-radius: 24px;
    /* Includes decorative blur circles */
}
```

**Features:**
- Blue-to-cyan gradient
- Decorative blur effects (pseudo-elements)
- Floating geometric shapes
- Relative positioning for absolute children

**Usage:**
```html
<div class="hero-section">
    <div class="hero-content">
        <div class="absolute hero-geometric heart animate-float">
            <i class="fas fa-heart"></i>
        </div>
        <h1 class="hero-title">Main Heading</h1>
        <p class="hero-subtitle">Supporting text</p>
        <div class="hero-buttons">
            <button class="btn-primary">Action</button>
        </div>
    </div>
</div>
```

#### `.hero-geometric`
Base class for decorative shapes.
```css
.hero-geometric {
    position: absolute;
    opacity: 0.1;
    z-index: 0;
}
```

**Shape Variants:**
- `.heart` - 120x120px, top-right, orange
- `.star` - 80x80px, middle-right, gold
- `.moon` - 100x100px, bottom-left, cyan

**Combine with:**
- `.animate-float` for gentle floating effect
- Use staggered animation delays

---

### 5. Form Elements

#### `.form-group`
Container for form fields.
```css
.form-group {
    margin-bottom: 20px;
}
```

#### `.form-label`
Styled label for form inputs.
```css
.form-label {
    display: block;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 14px;
}
```

#### `.form-input`, `.form-textarea`, `.form-select`
Styled form inputs with focus states.
```css
.form-input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e5e7eb;
    border-radius: var(--border-radius);
    /* Focus: Blue border + shadow ring */
}
```

**Usage:**
```html
<div class="form-group">
    <label for="email" class="form-label">
        <i class="fas fa-envelope mr-2 text-blue-600"></i> Email
    </label>
    <input type="email" id="email" class="form-input" placeholder="your@email.com">
</div>
```

---

### 6. Grids & Layouts

#### `.dashboard-grid`
3-column responsive grid for dashboard.
```css
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 28px;
}
```

**Breakpoints:**
- Automatically adjusts columns based on container width
- Minimum column width: 300px
- Gap: 28px

#### `.feature-grid`
Auto-fit grid for feature cards.
```css
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
}
```

#### `.book-grid`
Grid optimized for book cards.
```css
.book-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 24px;
}
```

**auto-fill vs auto-fit:**
- `auto-fill`: Fills row with empty tracks
- `auto-fit`: Collapses empty tracks

---

### 7. Animations

#### `.animate-fade-in`
Fade in with slight upward movement.
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeIn 0.4s ease; }
```

#### `.animate-slide-left` / `.animate-slide-right`
Slide in from left or right.
```css
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}
```

**Staggering:**
```html
<div class="card animate-slide-left"></div>
<div class="card animate-slide-left" style="animation-delay: 0.1s;"></div>
<div class="card animate-slide-left" style="animation-delay: 0.2s;"></div>
```

#### `.animate-float`
Gentle floating effect for decorative elements.
```css
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
.animate-float { animation: float 3s ease-in-out infinite; }
```

#### `.animate-pulse`
Pulsing opacity (for loading states).
```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

---

### 8. Message Alerts

#### `.message-alert`
Base alert styling.
```css
.message-alert {
    background-color: #f0f9ff;
    border-left: 4px solid var(--primary-blue);
    color: var(--text-primary);
    font-weight: 500;
}
```

**Variants:**
- `.message-error` - Red background and border
- `.message-success` - Green background and border
- `.message-warning` - Yellow background and border

**Usage:**
```html
<div class="message-alert message-success rounded-lg px-4 py-4 mb-4 flex items-center gap-3">
    <i class="fas fa-check-circle text-green-500"></i>
    <span>Success message!</span>
</div>
```

---

### 9. Utility Classes

#### `.gradient-text`
Gradient text effect.
```css
.gradient-text {
    background: linear-gradient(135deg, var(--primary-blue), var(--accent-orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

#### `.shadow-lg-blue` / `.shadow-lg-orange`
Colored shadows for emphasis.
```css
.shadow-lg-blue {
    box-shadow: 0 16px 32px rgba(30, 64, 175, 0.15);
}
```

#### `.text-gradient-blue-orange`
Horizontal blue-to-orange gradient text.
```css
.text-gradient-blue-orange {
    background: linear-gradient(90deg, var(--primary-blue), var(--accent-orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

---

## 📱 Responsive Design

### Breakpoints
```css
@media (max-width: 768px)  /* Mobile */
@media (max-width: 480px)  /* Small mobile */
```

### Mobile Adjustments (768px)
- Hero title: 56px → 40px
- Hero subtitle: 24px → 18px
- Button layout: Flex column with 100% width
- Book grid: Minimum 160px columns

### Small Mobile (480px)
- Hero section: 80px → 50px padding
- Hero title: 32px
- Hero subtitle: 16px

### Mobile-First Patterns
1. **Stack grids vertically**
2. **Full-width buttons**
3. **Reduce font sizes**
4. **Collapse navigation to hamburger**
5. **Increase touch target sizes**

---

## 🎯 Pattern Usage Guide

### When to Use Each Component

**Cards:**
- `.card` - General content containers
- `.dashboard-card` - Data display, metrics
- `.feature-card` - Marketing features, benefits
- `.book-card` - Book catalog display

**Buttons:**
- `.btn-primary` - 1 per section, main action
- `.btn-secondary` - Supporting actions
- `.btn-outline` - Tertiary, cancel, less emphasis

**Grids:**
- `.dashboard-grid` - 3-column dashboard layout
- `.feature-grid` - Features, quick actions
- `.book-grid` - Book catalogs, media grids

**Hero:**
- `.hero-section` - Landing pages, dashboard welcome
- Include `.hero-geometric` for visual interest
- Use `.animate-float` on decorative elements

**Animations:**
- Entry animations: `.animate-fade-in`, `.animate-slide-left/right`
- Decorative: `.animate-float`
- Loading: `.animate-pulse`
- Stagger delays: `style="animation-delay: 0.1s;"`

---

## ✅ Best Practices

### 1. Consistent Spacing
- Card padding: `p-6` (24px) or `p-8` (32px)
- Grid gaps: 24px - 28px
- Section margins: `mb-8` to `mb-12`

### 2. Icon Usage
- Font Awesome icons for all UI icons
- Emoji for large decorative icons (📚, 🔍, 👥)
- Always include `mr-1` or `mr-2` spacing after icons in buttons

### 3. Color Hierarchy
- Primary actions: Blue gradient
- Secondary actions: Orange gradient
- Informational: Cyan
- Success: Green
- Warning: Yellow/Gold
- Error: Red

### 4. Typography Scale
- Page titles: `text-4xl` (36px) to `text-5xl` (48px)
- Section headings: `text-3xl` (30px)
- Card titles: `text-xl` (20px) to `text-2xl` (24px)
- Body text: `text-base` (16px)
- Small text: `text-sm` (14px) or `text-xs` (12px)

### 5. Animation Timing
- Quick interactions: 0.3s
- Page transitions: 0.4s - 0.5s
- Floating animations: 3s
- Stagger delay: 0.1s increments

### 6. Accessibility
- Maintain 4.5:1 contrast ratio for text
- Include ARIA labels for icons
- Ensure keyboard navigation
- Provide focus indicators

### 7. Empty States
- Large icon (text-6xl)
- Clear heading (text-2xl)
- Helpful description
- Actionable CTA button
- Center alignment

---

## 🔧 Maintenance

### Adding New Components
1. Add to `main.css` in appropriate section
2. Follow naming convention (`.component-name`)
3. Document in this file
4. Include usage examples
5. Test responsive behavior

### Modifying Existing Components
1. Check all usage instances
2. Maintain backward compatibility
3. Update documentation
4. Test across all templates
5. Verify accessibility

---

## 📚 Examples

### Complete Card Example
```html
<div class="dashboard-card dashboard-card-accent accent-blue animate-slide-left">
    <div class="card-header">
        <div class="card-icon">
            <i class="fas fa-book-open text-blue-600"></i>
        </div>
        <div>
            <h2 class="card-title">Reading Progress</h2>
            <p class="text-gray-600 text-sm">Track your books</p>
        </div>
    </div>
    <div class="p-4 bg-blue-50 rounded-lg border-2 border-blue-100">
        <!-- Card content -->
    </div>
    <div class="mt-6 text-center">
        <a href="#" class="btn-primary px-6 py-2 rounded-lg">
            <i class="fas fa-search mr-2"></i> Find Books
        </a>
    </div>
</div>
```

### Complete Hero Example
```html
<div class="hero-section animate-fade-in">
    <div class="hero-content">
        <div class="absolute hero-geometric heart animate-float">
            <i class="fas fa-heart"></i>
        </div>
        <div class="absolute hero-geometric star animate-float" style="animation-delay: 0.5s;">
            <i class="fas fa-star"></i>
        </div>
        <h1 class="hero-title">Welcome to Literattus</h1>
        <p class="hero-subtitle">Your reading journey starts here</p>
        <div class="hero-buttons">
            <a href="#" class="btn-primary px-8 py-4 rounded-lg">
                <i class="fas fa-rocket mr-2"></i> Get Started
            </a>
            <a href="#" class="btn-outline px-8 py-4 rounded-lg">
                <i class="fas fa-info-circle mr-2"></i> Learn More
            </a>
        </div>
    </div>
</div>
```

---

*Document Version: 1.0*  
*Last Updated: October 30, 2025*  
*Maintained by: Literattus Frontend Team*

